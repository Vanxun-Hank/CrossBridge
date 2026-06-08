from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Callable

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from .admin_page import ADMIN_PAGE_HTML
from .db import build_engine, build_session_factory, get_database_url, run_migrations
from .models import TimelineApplication, TimelineAuditEvent, TimelineNode
from .nodes import (
    INITIAL_CURRENT_NODE,
    NODE_CODES,
    NODE_LABELS,
    NODES,
    STATES_REQUIRING_CUSTOMER_NOTE,
    initial_state_for,
    next_node_code,
)
from .schemas import AdminNodeUpdateRequest, CreateApplicationRequest

API_PREFIX = "/crossbridge-timeline/v1"
ADMIN_PREFIX = "/crossbridge-timeline-admin/v1"
ADMIN_PAGE_PATH = "/crossbridge-admin/timeline"
# DB is the source of truth for SSE: poll every few seconds, emit only what changed.
SSE_POLL_SECONDS = 2.0


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _parse_reminder(raw: str | None) -> datetime | None:
    """Parse an ISO-8601 reminder; empty string clears the reminder."""
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="reminder_at must be ISO-8601 or empty"
        ) from exc


class ReadinessUnavailable(RuntimeError):
    """Function 2 could not be reached to check submission-readiness."""


def _http_readiness_checker(origin_package_id: str) -> dict[str, Any]:
    """Default readiness check: ask Function 2 (the single source of truth) over HTTP."""
    base = os.environ.get(
        "CROSSBRIDGE_DOCUMENTS_API_URL", "http://127.0.0.1:8082"
    ).rstrip("/")
    url = (
        f"{base}/crossbridge-documents/v1/packages/{origin_package_id}/submission-readiness"
    )
    try:
        resp = httpx.get(url, timeout=10.0)
    except httpx.HTTPError as exc:
        raise ReadinessUnavailable(str(exc)) from exc
    if resp.status_code == 404:
        return {"ready": False, "blocking": [{"code": "package_not_found"}], "warnings": []}
    if resp.status_code >= 500:
        raise ReadinessUnavailable(f"documents service returned {resp.status_code}")
    data = resp.json()
    return {
        "ready": bool(data.get("ready")),
        "blocking": data.get("blocking", []),
        "warnings": data.get("warnings", []),
    }


def compute_sse_events(
    rows: list[tuple[str, str | None]], last_seen: dict[str, str | None]
) -> list[tuple[str, str | None]]:
    """Pure diff used by the SSE poller (unit-tested directly).

    Given ``[(application_id, updated_at_iso)]`` and a ``last_seen`` map (mutated in
    place), return the entries whose ``updated_at`` is new or changed.
    """
    changed: list[tuple[str, str | None]] = []
    for app_id, updated_at in rows:
        if last_seen.get(app_id) != updated_at:
            last_seen[app_id] = updated_at
            changed.append((app_id, updated_at))
    return changed


def _audit(
    db: Session,
    *,
    sme_id: str,
    event_type: str,
    payload: dict[str, Any],
    application_id: str | None = None,
) -> None:
    db.add(
        TimelineAuditEvent(
            id=str(uuid.uuid4()),
            sme_id=sme_id,
            application_id=application_id,
            event_type=event_type,
            payload_json=_json(payload),
            created_at=utcnow(),
        )
    )


def create_app(
    *,
    database_url: str | None = None,
    migrate_on_startup: bool = True,
    readiness_checker: Callable[[str], dict[str, Any]] | None = None,
) -> FastAPI:
    resolved_database_url = database_url or get_database_url()
    engine = build_engine(resolved_database_url)
    session_factory = build_session_factory(engine)
    # Dependency-injected like Function 1's clarifier, so eval can stub Function 2.
    check_readiness: Callable[[str], dict[str, Any]] = (
        readiness_checker or _http_readiness_checker
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if migrate_on_startup:
            run_migrations(resolved_database_url)
        yield
        engine.dispose()

    app = FastAPI(title="CrossBridge Application Timeline API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.session_factory = session_factory

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    # ---- serialization (SME path strips internal_note entirely) ----------

    def _serialize_node(node: TimelineNode, *, include_internal: bool = False) -> dict[str, Any]:
        out = {
            "node_code": node.node_code,
            "sort_order": node.sort_order,
            "state": node.state,
            "label_zh": NODE_LABELS.get(node.node_code, {}).get("zh", node.node_code),
            "label_en": NODE_LABELS.get(node.node_code, {}).get("en", node.node_code),
            "customer_note_zh": node.customer_note_zh or "",
            "customer_note_en": node.customer_note_en or "",
            "reminder_at": _iso(node.reminder_at),
            "updated_at": _iso(node.updated_at),
        }
        if include_internal:
            out["internal_note"] = node.internal_note or ""
        return out

    def _nodes_for(db: Session, application_id: str) -> list[TimelineNode]:
        return db.scalars(
            select(TimelineNode)
            .where(TimelineNode.application_id == application_id)
            .order_by(TimelineNode.sort_order)
        ).all()

    def _serialize_application(
        db: Session, application: TimelineApplication, *, include_internal: bool = False
    ) -> dict[str, Any]:
        return {
            "id": application.id,
            "sme_id": application.sme_id,
            "origin_package_id": application.origin_package_id,
            "product_id": application.product_id,
            "product_label_zh": application.product_label_zh,
            "product_label_en": application.product_label_en,
            "scenario_code": application.scenario_code,
            "current_node_code": application.current_node_code,
            "status": application.status,
            "created_at": _iso(application.created_at),
            "updated_at": _iso(application.updated_at),
            "nodes": [
                _serialize_node(n, include_internal=include_internal)
                for n in _nodes_for(db, application.id)
            ],
        }

    def _serialize_summary(application: TimelineApplication) -> dict[str, Any]:
        return {
            "id": application.id,
            "origin_package_id": application.origin_package_id,
            "product_id": application.product_id,
            "product_label_zh": application.product_label_zh,
            "product_label_en": application.product_label_en,
            "scenario_code": application.scenario_code,
            "current_node_code": application.current_node_code,
            "current_node_label_zh": NODE_LABELS.get(application.current_node_code, {}).get(
                "zh", application.current_node_code
            ),
            "current_node_label_en": NODE_LABELS.get(application.current_node_code, {}).get(
                "en", application.current_node_code
            ),
            "status": application.status,
            "created_at": _iso(application.created_at),
            "updated_at": _iso(application.updated_at),
        }

    def _init_nodes(db: Session, application_id: str, *, now: datetime) -> None:
        for code, sort_order, _, _ in NODES:
            db.add(
                TimelineNode(
                    id=str(uuid.uuid4()),
                    application_id=application_id,
                    node_code=code,
                    sort_order=sort_order,
                    state=initial_state_for(code),
                    updated_at=now,
                )
            )

    def _get_application_or_404(db: Session, application_id: str) -> TimelineApplication:
        application = db.get(TimelineApplication, application_id)
        if application is None:
            raise HTTPException(status_code=404, detail="application not found")
        return application

    def _get_by_origin(db: Session, origin_package_id: str) -> TimelineApplication | None:
        return db.scalars(
            select(TimelineApplication).where(
                TimelineApplication.origin_package_id == origin_package_id
            )
        ).first()

    # ---- SME endpoints ---------------------------------------------------

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(f"{API_PREFIX}/applications")
    def create_or_resume_application(
        request: CreateApplicationRequest,
        response: Response,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        # Idempotent: one application per F2 package — a second submit returns the original.
        existing = _get_by_origin(db, request.origin_package_id)
        if existing is not None:
            result = _serialize_application(db, existing)
            result["resumed"] = True
            return result

        # Function 2 is the single source of truth for submission-readiness.
        try:
            readiness = check_readiness(request.origin_package_id)
        except ReadinessUnavailable as exc:
            raise HTTPException(
                status_code=503, detail="document-preparation service is unavailable"
            ) from exc
        if not readiness.get("ready"):
            raise HTTPException(
                status_code=422,
                detail={
                    "ready": False,
                    "blocking": readiness.get("blocking", []),
                    "warnings": readiness.get("warnings", []),
                },
            )

        now = utcnow()
        application = TimelineApplication(
            id=str(uuid.uuid4()),
            sme_id=request.sme_id,
            origin_package_id=request.origin_package_id,
            product_id=request.product_id,
            product_label_zh=request.product_label_zh,
            product_label_en=request.product_label_en,
            scenario_code=request.scenario_code,
            current_node_code=INITIAL_CURRENT_NODE,
            status="in_progress",
            created_at=now,
            updated_at=now,
        )
        db.add(application)
        _init_nodes(db, application.id, now=now)
        _audit(
            db,
            sme_id=request.sme_id,
            application_id=application.id,
            event_type="timeline_application_created",
            payload={
                "origin_package_id": request.origin_package_id,
                "product_id": request.product_id,
            },
        )
        db.commit()
        db.refresh(application)
        result = _serialize_application(db, application)
        result["resumed"] = False
        response.status_code = 201
        return result

    @app.get(f"{API_PREFIX}/applications")
    def list_applications(
        sme_id: str = "demo_sme_001", db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        rows = db.scalars(
            select(TimelineApplication)
            .where(TimelineApplication.sme_id == sme_id)
            .order_by(TimelineApplication.updated_at.desc())
        ).all()
        return {"sme_id": sme_id, "applications": [_serialize_summary(a) for a in rows]}

    @app.get(f"{API_PREFIX}/applications/{{application_id}}")
    def read_application(application_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        return _serialize_application(db, _get_application_or_404(db, application_id))

    @app.get(f"{API_PREFIX}/events")
    async def stream_events(request: Request, sme_id: str = "demo_sme_001") -> StreamingResponse:
        async def poll() -> list[tuple[str, str | None]]:
            def _query() -> list[tuple[str, str | None]]:
                db = session_factory()
                try:
                    rows = db.scalars(
                        select(TimelineApplication).where(
                            TimelineApplication.sme_id == sme_id
                        )
                    ).all()
                    return [(a.id, _iso(a.updated_at)) for a in rows]
                finally:
                    db.close()

            return await run_in_threadpool(_query)

        async def event_stream():
            # Baseline first so we don't replay the SME's current state as "updates".
            last_seen = {app_id: upd for app_id, upd in await poll()}
            while True:
                if await request.is_disconnected():
                    break
                await asyncio.sleep(SSE_POLL_SECONDS)
                for app_id, upd in compute_sse_events(await poll(), last_seen):
                    payload = json.dumps({"application_id": app_id, "updated_at": upd})
                    yield f"data: {payload}\n\n"
                yield ": keepalive\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ---- admin endpoints (nginx IP allowlist + Basic Auth) ---------------

    @app.get(f"{ADMIN_PREFIX}/applications")
    def admin_list_applications(db: Session = Depends(get_db)) -> dict[str, Any]:
        rows = db.scalars(
            select(TimelineApplication).order_by(TimelineApplication.updated_at.desc())
        ).all()
        return {
            "applications": [
                _serialize_application(db, a, include_internal=True) for a in rows
            ]
        }

    @app.patch(f"{ADMIN_PREFIX}/applications/{{application_id}}/nodes/{{node_code}}")
    def admin_update_node(
        application_id: str,
        node_code: str,
        request: AdminNodeUpdateRequest,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        application = _get_application_or_404(db, application_id)
        if node_code not in NODE_CODES:
            raise HTTPException(status_code=404, detail="unknown node_code")
        node = db.scalars(
            select(TimelineNode)
            .where(TimelineNode.application_id == application_id)
            .where(TimelineNode.node_code == node_code)
        ).first()
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")

        now = utcnow()
        # Note / reminder / internal edits are allowed on any node.
        if request.customer_note_zh is not None:
            node.customer_note_zh = request.customer_note_zh
        if request.customer_note_en is not None:
            node.customer_note_en = request.customer_note_en
        if request.internal_note is not None:
            node.internal_note = request.internal_note
        if request.reminder_at is not None:
            node.reminder_at = _parse_reminder(request.reminder_at)

        state_changed = request.state is not None and request.state != node.state
        if state_changed:
            # State transitions are restricted to the current node — no skipping ahead.
            if node_code != application.current_node_code:
                raise HTTPException(
                    status_code=409,
                    detail="cannot change state of a non-current node (no skipping)",
                )
            new_state = request.state
            if new_state in STATES_REQUIRING_CUSTOMER_NOTE:
                zh = (
                    request.customer_note_zh
                    if request.customer_note_zh is not None
                    else node.customer_note_zh
                ) or ""
                en = (
                    request.customer_note_en
                    if request.customer_note_en is not None
                    else node.customer_note_en
                ) or ""
                if not zh.strip() or not en.strip():
                    raise HTTPException(
                        status_code=422,
                        detail="rejected / supplement_required require non-empty "
                        "customer_note_zh and customer_note_en",
                    )
            node.state = new_state
            if new_state == "completed":
                nxt = next_node_code(node_code)
                if nxt is None:
                    application.status = "completed"
                else:
                    application.current_node_code = nxt
                    nxt_node = db.scalars(
                        select(TimelineNode)
                        .where(TimelineNode.application_id == application_id)
                        .where(TimelineNode.node_code == nxt)
                    ).first()
                    if nxt_node is not None and nxt_node.state == "pending":
                        nxt_node.state = "in_progress"
                        nxt_node.updated_at = now
            elif new_state == "rejected":
                application.status = "rejected"
            elif new_state == "in_progress":
                application.status = "in_progress"
            # supplement_required: application stays in_progress, current node unchanged.

        node.updated_at = now
        application.updated_at = now  # bump so the SME SSE poll detects the change
        _audit(
            db,
            sme_id=application.sme_id,
            application_id=application.id,
            event_type="timeline_node_updated",
            payload={
                "node_code": node_code,
                "state": node.state,
                "current_node_code": application.current_node_code,
                "status": application.status,
            },
        )
        db.commit()
        db.refresh(application)
        return _serialize_application(db, application, include_internal=True)

    @app.post(f"{ADMIN_PREFIX}/applications/{{application_id}}/reset")
    def admin_reset_application(
        application_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        application = _get_application_or_404(db, application_id)
        db.query(TimelineNode).filter(
            TimelineNode.application_id == application_id
        ).delete()
        now = utcnow()
        _init_nodes(db, application_id, now=now)
        application.current_node_code = INITIAL_CURRENT_NODE
        application.status = "in_progress"
        application.updated_at = now
        _audit(
            db,
            sme_id=application.sme_id,
            application_id=application.id,
            event_type="timeline_application_reset",
            payload={},
        )
        db.commit()
        db.refresh(application)
        return _serialize_application(db, application, include_internal=True)

    # ---- hidden admin single-page UI -------------------------------------

    @app.get(ADMIN_PAGE_PATH, response_class=HTMLResponse)
    def admin_page() -> HTMLResponse:
        # no-store: the console has no ?v= cache-buster, so always serve the latest
        # (operators should never get a stale cached copy after a deploy).
        return HTMLResponse(ADMIN_PAGE_HTML, headers={"Cache-Control": "no-store"})

    return app


app = create_app()

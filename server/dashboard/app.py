from __future__ import annotations

import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import build_engine, build_session_factory, get_database_url, run_migrations
from .models import DashboardExportEvent, PolicyBookmark, utcnow
from .schemas import ExportRequest, PolicyBookmarkCreateRequest

API_PREFIX = "/crossbridge-dashboard/v1"
DEMO_SME_ID = "demo_sme_001"
DISCLAIMER = (
    "CrossBridge AI only provides preliminary intelligent reference and operational "
    "guidance for SMEs’ cross-border financing. All assessment results, policy "
    "interpretations and optimization suggestions do not replace official bank review "
    "and professional financial/legal judgment. The final loan approval result and "
    "compliance standard are subject to the hosting bank’s official regulations and "
    "national financial supervision rules."
)


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpstreamError(RuntimeError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(message)
        self.service = service
        self.message = message


class HttpUpstreamClient:
    def __init__(self) -> None:
        self.business_url = os.environ.get(
            "CROSSBRIDGE_BUSINESS_API_URL", "http://127.0.0.1:8081"
        ).rstrip("/")
        self.documents_url = os.environ.get(
            "CROSSBRIDGE_DOCUMENTS_API_URL", "http://127.0.0.1:8082"
        ).rstrip("/")
        self.timeline_url = os.environ.get(
            "CROSSBRIDGE_TIMELINE_API_URL", "http://127.0.0.1:8083"
        ).rstrip("/")

    def _get_json(
        self,
        service: str,
        base_url: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{base_url}{path}"
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise UpstreamError(service, str(exc)) from exc
        if resp.status_code >= 400:
            raise UpstreamError(service, f"HTTP {resp.status_code} from {path}")
        try:
            data = resp.json()
        except ValueError as exc:
            raise UpstreamError(service, f"non-JSON response from {path}") from exc
        if not isinstance(data, dict):
            raise UpstreamError(service, f"unexpected response shape from {path}")
        return data

    def health(self) -> dict[str, Any]:
        services = {
            "business": (self.business_url, "/healthz"),
            "documents": (self.documents_url, "/healthz"),
            "timeline": (self.timeline_url, "/healthz"),
        }
        out: dict[str, Any] = {}
        for service, (base, path) in services.items():
            try:
                out[service] = {
                    "ok": self._get_json(service, base, path).get("status") == "ok"
                }
            except UpstreamError as exc:
                out[service] = {"ok": False, "detail": exc.message}
        return out

    def list_saved_drafts(self, sme_id: str) -> list[dict[str, Any]]:
        data = self._get_json(
            "business",
            self.business_url,
            "/crossbridge/v1/loan-matching/saved-drafts",
            params={"sme_id": sme_id},
        )
        return list(data.get("saved_drafts") or [])

    def list_document_packages(self, sme_id: str) -> list[dict[str, Any]]:
        data = self._get_json(
            "documents",
            self.documents_url,
            "/crossbridge-documents/v1/packages",
            params={"sme_id": sme_id},
        )
        packages = list(data.get("packages") or [])
        enriched: list[dict[str, Any]] = []
        for package in packages:
            package_id = package.get("id")
            item = dict(package)
            if package_id:
                detail = self._get_json(
                    "documents",
                    self.documents_url,
                    f"/crossbridge-documents/v1/packages/{package_id}",
                )
                readiness = self._get_json(
                    "documents",
                    self.documents_url,
                    f"/crossbridge-documents/v1/packages/{package_id}/submission-readiness",
                )
                item["official_forms"] = detail.get("official_forms", [])
                item["trade_terms"] = detail.get("trade_terms", {})
                item["submission_readiness"] = readiness
            enriched.append(item)
        return enriched

    def list_applications(self, sme_id: str) -> list[dict[str, Any]]:
        data = self._get_json(
            "timeline",
            self.timeline_url,
            "/crossbridge-timeline/v1/applications",
            params={"sme_id": sme_id},
        )
        return list(data.get("applications") or [])


def _serialize_bookmark(row: PolicyBookmark) -> dict[str, Any]:
    return {
        "id": row.id,
        "sme_id": row.sme_id,
        "title": row.title,
        "source_url": row.source_url,
        "source_title": row.source_title,
        "snippet": row.snippet,
        "document_type": row.document_type,
        "trust_tier": row.trust_tier,
        "origin_chat_id": row.origin_chat_id,
        "created_at": _iso(row.created_at),
    }


def _serialize_export(row: DashboardExportEvent) -> dict[str, Any]:
    return {
        "id": row.id,
        "sme_id": row.sme_id,
        "export_type": row.export_type,
        "payload": json.loads(row.payload_json or "{}"),
        "created_at": _iso(row.created_at),
    }


def _progress_summary(
    *,
    saved_drafts: list[dict[str, Any]],
    document_packages: list[dict[str, Any]],
    applications: list[dict[str, Any]],
    policy_bookmarks: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_product_ids = {
        product.get("product_id")
        for draft in saved_drafts
        for product in draft.get("selected_products", [])
        if product.get("product_id")
    }
    ready_packages = [
        p
        for p in document_packages
        if (p.get("submission_readiness") or {}).get("ready") is True
    ]
    active_applications = [
        a for a in applications if a.get("status") not in {"completed", "rejected"}
    ]
    return {
        "saved_draft_count": len(saved_drafts),
        "selected_product_count": len(selected_product_ids),
        "document_package_count": len(document_packages),
        "submission_ready_package_count": len(ready_packages),
        "application_count": len(applications),
        "active_application_count": len(active_applications),
        "policy_bookmark_count": len(policy_bookmarks),
    }


def _add_issue(issues: list[dict[str, str]], service: str, detail: str) -> None:
    issues.append({"service": service, "detail": detail})


def _build_overview(
    *,
    sme_id: str,
    db: Session,
    upstream_client: Any,
) -> dict[str, Any]:
    access_issues: list[dict[str, str]] = []

    try:
        saved_drafts = upstream_client.list_saved_drafts(sme_id)
    except Exception as exc:
        service = exc.service if isinstance(exc, UpstreamError) else "business"
        detail = exc.message if isinstance(exc, UpstreamError) else str(exc)
        _add_issue(access_issues, service, detail)
        saved_drafts = []

    try:
        document_packages = upstream_client.list_document_packages(sme_id)
    except Exception as exc:
        service = exc.service if isinstance(exc, UpstreamError) else "documents"
        detail = exc.message if isinstance(exc, UpstreamError) else str(exc)
        _add_issue(access_issues, service, detail)
        document_packages = []

    try:
        applications = upstream_client.list_applications(sme_id)
    except Exception as exc:
        service = exc.service if isinstance(exc, UpstreamError) else "timeline"
        detail = exc.message if isinstance(exc, UpstreamError) else str(exc)
        _add_issue(access_issues, service, detail)
        applications = []

    bookmarks = [
        _serialize_bookmark(row)
        for row in db.scalars(
            select(PolicyBookmark)
            .where(PolicyBookmark.sme_id == sme_id)
            .order_by(PolicyBookmark.created_at.desc())
        )
    ]

    return {
        "sme_id": sme_id,
        "generated_at": _generated_at(),
        "disclaimer": DISCLAIMER,
        "summary": _progress_summary(
            saved_drafts=saved_drafts,
            document_packages=document_packages,
            applications=applications,
            policy_bookmarks=bookmarks,
        ),
        "saved_drafts": saved_drafts,
        "document_packages": document_packages,
        "applications": applications,
        "policy_bookmarks": bookmarks,
        "access_issues": access_issues,
    }


def _fmt_hkd(value: Any) -> str:
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return "-"
    return f"HKD {amount:,}"


def _profile_line(profile: dict[str, Any]) -> str:
    return (
        f"Scenario: {profile.get('business_scenario') or '-'}; "
        f"Purpose: {profile.get('financing_purpose') or '-'}; "
        f"Requested: {_fmt_hkd(profile.get('requested_amount_hkd'))}; "
        f"Turnover: {_fmt_hkd(profile.get('annual_turnover_hkd'))}"
    )


def _markdown_report(overview: dict[str, Any]) -> str:
    summary = overview["summary"]
    lines = [
        "# CrossBridge Personal SME Financing Dashboard",
        "",
        f"- SME ID: `{overview['sme_id']}`",
        f"- Generated at: `{overview['generated_at']}`",
        f"- Saved financing drafts: {summary['saved_draft_count']}",
        f"- Saved product schemes: {summary['selected_product_count']}",
        f"- Document packages: {summary['document_package_count']}",
        f"- Submission-ready packages: {summary['submission_ready_package_count']}",
        f"- Applications: {summary['application_count']}",
        f"- Policy bookmarks: {summary['policy_bookmark_count']}",
        "",
        "## Core Function Disclaimer",
        "",
        overview["disclaimer"],
        "",
        "## AI Pre-assessment Reports and Saved Product Schemes",
        "",
    ]
    if overview["saved_drafts"]:
        for draft in overview["saved_drafts"]:
            lines.append(f"### {draft.get('name') or draft.get('id')}")
            lines.append("")
            lines.append(f"- Draft ID: `{draft.get('id')}`")
            lines.append(f"- Updated at: `{draft.get('updated_at') or '-'}`")
            lines.append(f"- {_profile_line(draft.get('draft_profile') or {})}")
            products = draft.get("selected_products") or []
            if products:
                lines.append("- Selected products:")
                for product in products:
                    name = product.get("product_name") or product.get("product_id")
                    lines.append(f"  - {name} (`{product.get('product_id')}`)")
            else:
                lines.append("- Selected products: none")
            lines.append("")
    else:
        lines.extend(["No saved financing drafts yet.", ""])

    lines.extend(["## Document Preparation", ""])
    if overview["document_packages"]:
        for package in overview["document_packages"]:
            readiness = package.get("submission_readiness") or {}
            forms = package.get("official_forms") or []
            lines.append(
                f"- `{package.get('id')}` {package.get('scenario_label_en') or package.get('scenario_code')}: "
                f"{package.get('checklist_done', 0)}/{package.get('checklist_total', 0)} checklist items, "
                f"ready={bool(readiness.get('ready'))}, official_forms={len(forms)}"
            )
    else:
        lines.append("No document packages yet.")
    lines.append("")

    lines.extend(["## Application Progress", ""])
    if overview["applications"]:
        for app in overview["applications"]:
            lines.append(
                f"- `{app.get('id')}` {app.get('product_label_en') or app.get('product_id') or '-'}: "
                f"{app.get('status')} / {app.get('current_node_label_en') or app.get('current_node_code')}"
            )
    else:
        lines.append("No applications yet.")
    lines.append("")

    lines.extend(["## Collected Policy Documents", ""])
    if overview["policy_bookmarks"]:
        for bookmark in overview["policy_bookmarks"]:
            lines.append(
                f"- [{bookmark.get('title')}]({bookmark.get('source_url')})"
                f" — {bookmark.get('source_title') or bookmark.get('document_type') or 'source'}"
            )
    else:
        lines.append("No collected policy documents yet.")
    lines.append("")

    if overview["access_issues"]:
        lines.extend(["## Access Issues", ""])
        for issue in overview["access_issues"]:
            lines.append(f"- {issue['service']}: {issue['detail']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def create_app(
    *,
    database_url: str | None = None,
    migrate_on_startup: bool = True,
    upstream_client: Any | None = None,
) -> FastAPI:
    resolved_database_url = database_url or get_database_url()
    engine = build_engine(resolved_database_url)
    session_factory = build_session_factory(engine)
    upstream = upstream_client or HttpUpstreamClient()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if migrate_on_startup:
            run_migrations(resolved_database_url)
        yield
        engine.dispose()

    app = FastAPI(title="CrossBridge Personal SME Financing Dashboard API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.session_factory = session_factory
    app.state.upstream_client = upstream

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        upstream_health = {}
        try:
            upstream_health = upstream.health()
        except Exception as exc:
            upstream_health = {"error": str(exc)}
        return {
            "status": "ok",
            "service": "crossbridge-dashboard",
            "upstreams": upstream_health,
        }

    @app.get(f"{API_PREFIX}/overview")
    def read_overview(
        sme_id: str = DEMO_SME_ID, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        return _build_overview(sme_id=sme_id, db=db, upstream_client=upstream)

    @app.get(f"{API_PREFIX}/policy-bookmarks")
    def list_policy_bookmarks(
        sme_id: str = DEMO_SME_ID, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        rows = db.scalars(
            select(PolicyBookmark)
            .where(PolicyBookmark.sme_id == sme_id)
            .order_by(PolicyBookmark.created_at.desc())
        )
        return {"sme_id": sme_id, "policy_bookmarks": [_serialize_bookmark(row) for row in rows]}

    @app.post(f"{API_PREFIX}/policy-bookmarks")
    def create_policy_bookmark(
        request: PolicyBookmarkCreateRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        bookmark = PolicyBookmark(
            id=str(uuid.uuid4()),
            sme_id=request.sme_id,
            title=request.title.strip(),
            source_url=request.source_url.strip(),
            source_title=(request.source_title or "").strip(),
            snippet=(request.snippet or "").strip(),
            document_type=(request.document_type or "").strip(),
            trust_tier=(request.trust_tier or "").strip(),
            origin_chat_id=request.origin_chat_id,
            created_at=utcnow(),
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return _serialize_bookmark(bookmark)

    @app.delete(f"{API_PREFIX}/policy-bookmarks/{{bookmark_id}}")
    def delete_policy_bookmark(bookmark_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        row = db.get(PolicyBookmark, bookmark_id)
        if row is not None:
            db.delete(row)
            db.commit()
        return {"deleted": True, "bookmark_id": bookmark_id}

    @app.post(f"{API_PREFIX}/reports/markdown")
    def export_markdown_report(
        request: ExportRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        overview = _build_overview(sme_id=request.sme_id, db=db, upstream_client=upstream)
        content = _markdown_report(overview)
        now = utcnow()
        event = DashboardExportEvent(
            id=str(uuid.uuid4()),
            sme_id=request.sme_id,
            export_type="markdown_report",
            payload_json=_json(
                {
                    "summary": overview["summary"],
                    "access_issue_count": len(overview["access_issues"]),
                    "filename": f"crossbridge-dashboard-{request.sme_id}-{now:%Y%m%d%H%M%S}.md",
                }
            ),
            created_at=now,
        )
        db.add(event)
        db.commit()
        return {
            "sme_id": request.sme_id,
            "filename": json.loads(event.payload_json)["filename"],
            "content_type": "text/markdown; charset=utf-8",
            "content": content,
            "export_event": _serialize_export(event),
        }

    @app.get(f"{API_PREFIX}/backups/json")
    def export_json_backup(
        sme_id: str = DEMO_SME_ID, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        overview = _build_overview(sme_id=sme_id, db=db, upstream_client=upstream)
        exports = [
            _serialize_export(row)
            for row in db.scalars(
                select(DashboardExportEvent)
                .where(DashboardExportEvent.sme_id == sme_id)
                .order_by(DashboardExportEvent.created_at.desc())
            )
        ]
        now = utcnow()
        event = DashboardExportEvent(
            id=str(uuid.uuid4()),
            sme_id=sme_id,
            export_type="json_backup",
            payload_json=_json({"summary": overview["summary"]}),
            created_at=now,
        )
        db.add(event)
        db.commit()
        return {
            "backup_version": "function7.v1",
            "generated_at": _iso(now),
            "sme_id": sme_id,
            "disclaimer": DISCLAIMER,
            "overview": overview,
            "export_events": exports,
            "current_export_event": _serialize_export(event),
        }

    return app


app = create_app()

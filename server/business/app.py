from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Iterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from files.language_utils import resolve_response_language

from .catalog import OFFICIAL_CATALOG_PATH, list_active_products, seed_catalog_products
from .db import build_engine, build_session_factory, get_database_url, run_migrations
from .matching import (
    FIELD_LABELS,
    LlmClarifier,
    fallback_question,
    match_products,
    merge_profile,
    missing_required_fields,
    product_snapshot,
    route_intent,
    try_direct_numeric_fill,
)
from .models import AuditEvent, MatchResult, MatchingSession, SmeProfile, isoformat_utc, utcnow
from .schemas import (
    ClarifyRequest,
    CreateSessionRequest,
    DraftProfile,
    RouteIntentRequest,
    UpdateDraftRequest,
)

DEMO_SME_ID = "demo_sme_001"
DEMO_SME_NAME = "CrossBridge Demo Trading Ltd."
MAX_CLARIFICATIONS = 3
# 可 resume 的「未完成」session —— 用户「暂时离开」不丢弃，重进时续填。
# matched / saved / discarded 都是终态：完成一次匹配后再进入 = 开新一轮，
# 不会把上一轮的旧候选方案 dump 出来（这是用户实测发现的 bug 根因）。
OPEN_SESSION_STATUSES = ("draft", "awaiting_clarification", "ready_to_match")


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _load_profile_json(value: str) -> DraftProfile:
    return DraftProfile.model_validate_json(value)


def _audit(
    db: Session,
    *,
    sme_id: str,
    event_type: str,
    payload: dict[str, Any],
    session_id: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            id=str(uuid.uuid4()),
            sme_id=sme_id,
            session_id=session_id,
            event_type=event_type,
            payload_json=_json(payload),
            created_at=utcnow(),
        )
    )


def _serialize_profile(profile: DraftProfile) -> dict[str, Any]:
    return profile.model_dump()


def _serialize_session(session: MatchingSession, db: Session) -> dict[str, Any]:
    profile = _load_profile_json(session.draft_profile_json)
    missing = missing_required_fields(profile)
    results = list(
        db.scalars(
            select(MatchResult)
            .where(MatchResult.session_id == session.id)
            .order_by(MatchResult.rank)
        )
    )
    return {
        "id": session.id,
        "sme_id": session.sme_id,
        "status": session.status,
        "draft_profile": _serialize_profile(profile),
        "clarification_count": session.clarification_count,
        "max_clarifications": MAX_CLARIFICATIONS,
        "current_question": session.current_question,
        "response_language": session.response_language,
        "missing_required_fields": missing,
        "missing_required_labels": [FIELD_LABELS[field] for field in missing],
        "ready_to_match": not missing,
        "match_results": [
            {
                "rank": result.rank,
                "score": result.score,
                "reasons": json.loads(result.reasons_json),
                "product": json.loads(result.product_snapshot_json),
            }
            for result in results
        ],
    }


def create_app(
    *,
    database_url: str | None = None,
    clarifier: Any | None = None,
    migrate_on_startup: bool = True,
    catalog_mode: str | None = None,
) -> FastAPI:
    resolved_database_url = database_url or get_database_url()
    engine = build_engine(resolved_database_url)
    SessionLocal = build_session_factory(engine)
    clarifier_service = clarifier or LlmClarifier()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if migrate_on_startup:
            run_migrations(resolved_database_url)
        with SessionLocal() as db:
            app.state.catalog_mode = seed_catalog_products(db, mode=catalog_mode)
        yield
        engine.dispose()

    app = FastAPI(title="CrossBridge SME Business API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_db() -> Iterator[Session]:
        with SessionLocal() as db:
            yield db

    def get_matching_session(session_id: str, db: Session) -> MatchingSession:
        session = db.get(MatchingSession, session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="matching session not found")
        return session

    @app.get("/healthz")
    def healthz() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "service": "crossbridge-business",
            "catalog_mode": app.state.catalog_mode,
            "official_catalog_available": OFFICIAL_CATALOG_PATH.exists(),
        }

    @app.get("/crossbridge/v1/loan-matching/catalog")
    def read_loan_product_catalog(db: Session = Depends(get_db)) -> dict[str, Any]:
        products = list_active_products(db)
        return {
            "catalog_mode": app.state.catalog_mode,
            "official_catalog_available": OFFICIAL_CATALOG_PATH.exists(),
            "product_count": len(products),
            "products": [
                {
                    "product_id": product.id,
                    "product_name": product.product_name,
                    "source_url": product.source_url,
                    "source_title": product.source_title,
                    "source_checked_at": isoformat_utc(product.source_checked_at),
                    "review_status": product.review_status,
                    "demo_only": product.demo_only,
                }
                for product in products
            ],
        }

    @app.post("/crossbridge/v1/loan-matching/route-intent")
    def loan_matching_route_intent(request: RouteIntentRequest) -> dict[str, Any]:
        return route_intent(request.message)

    @app.post("/crossbridge/v1/loan-matching/sessions")
    def create_matching_session(
        request: CreateSessionRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        # resume-or-create：同一 sme_id 若已有未丢弃/未保存的开放 session，续填它而非新建。
        # 这样「中途离开再回来」不会丢进度（原来每次新建 + 空 SmeProfile = 进度归零）。
        existing = db.scalars(
            select(MatchingSession)
            .where(MatchingSession.sme_id == request.sme_id)
            .where(MatchingSession.status.in_(OPEN_SESSION_STATUSES))
            .order_by(MatchingSession.updated_at.desc())
        ).first()
        if existing is not None:
            existing_profile = _load_profile_json(existing.draft_profile_json)
            # Re-entering F1 is a new visible interaction. Use the current UI setting
            # until the user sends a clear natural-language answer.
            existing.response_language = request.ui_language
            # 续填语义：已填草稿优先，新 prefill 只补当前为空的字段。
            merged = DraftProfile.model_validate(
                {
                    **request.prefill.model_dump(exclude_none=True),
                    **existing_profile.model_dump(exclude_none=True),
                }
            )
            if merged.model_dump() != existing_profile.model_dump():
                db.execute(delete(MatchResult).where(MatchResult.session_id == existing.id))
                existing.draft_profile_json = merged.model_dump_json()
                if missing_required_fields(merged):
                    existing.status = (
                        "awaiting_clarification" if existing.clarification_count else "draft"
                    )
                else:
                    existing.status = "ready_to_match"
            existing.current_question = fallback_question(merged, existing.response_language)
            existing.updated_at = utcnow()
            _audit(
                db,
                sme_id=existing.sme_id,
                session_id=existing.id,
                event_type="matching_session_resumed",
                payload={"prefill": request.prefill.model_dump(exclude_none=True)},
            )
            db.commit()
            return _serialize_session(existing, db)

        persisted = db.get(SmeProfile, request.sme_id)
        profile = (
            _load_profile_json(persisted.profile_json) if persisted else DraftProfile()
        )
        profile = merge_profile(profile, request.prefill)
        session = MatchingSession(
            id=str(uuid.uuid4()),
            sme_id=request.sme_id,
            status="draft",
            draft_profile_json=profile.model_dump_json(),
            clarification_count=0,
            current_question=fallback_question(profile, request.ui_language),
            response_language=request.ui_language,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(session)
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="matching_session_created",
            payload={"prefill": request.prefill.model_dump(exclude_none=True)},
        )
        db.commit()
        return _serialize_session(session, db)

    @app.get("/crossbridge/v1/loan-matching/sessions/{session_id}")
    def read_matching_session(
        session_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        return _serialize_session(get_matching_session(session_id, db), db)

    @app.patch("/crossbridge/v1/loan-matching/sessions/{session_id}/draft")
    def update_matching_draft(
        session_id: str, request: UpdateDraftRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        session = get_matching_session(session_id, db)
        if session.status == "discarded":
            raise HTTPException(status_code=409, detail="discarded session cannot be updated")
        profile = merge_profile(
            _load_profile_json(session.draft_profile_json), request.updates
        )
        db.execute(delete(MatchResult).where(MatchResult.session_id == session.id))
        session.draft_profile_json = profile.model_dump_json()
        session.status = "ready_to_match" if not missing_required_fields(profile) else "draft"
        session.current_question = fallback_question(profile, session.response_language)
        # 选项 chip / 手动填表都是「有进展」，清掉连续无进展计数，重新放开 LLM 澄清。
        if request.updates.model_dump(exclude_none=True):
            session.clarification_count = 0
        session.updated_at = utcnow()
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="matching_draft_updated",
            payload={"updates": request.updates.model_dump(exclude_none=True)},
        )
        db.commit()
        return _serialize_session(session, db)

    @app.post("/crossbridge/v1/loan-matching/sessions/{session_id}/clarify")
    def clarify_matching_session(
        session_id: str, request: ClarifyRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        session = get_matching_session(session_id, db)
        if session.status == "discarded":
            raise HTTPException(status_code=409, detail="discarded session cannot be updated")
        profile = _load_profile_json(session.draft_profile_json)
        session.response_language = resolve_response_language(
            request.message,
            previous=session.response_language,
            fallback=request.ui_language,
        )
        session.current_question = fallback_question(profile, session.response_language)

        # clarification_count = 连续「无进展」的 LLM 澄清次数（不是总次数）。
        # 乱输入只会累加它，不会污染草稿；达到上限就提示改用选项 chip / 直接填表，
        # 而 chip / 手动编辑走 draft PATCH 会把它清零 —— 所以永远不会被乱输入卡死。
        if session.clarification_count >= MAX_CLARIFICATIONS:
            session.updated_at = utcnow()
            db.commit()
            return {
                **_serialize_session(session, db),
                "clarifier_mode": "needs_manual",
                "clarifier_error": None,
            }

        # 当前正在问的字段（裸值优先填它）
        target_field = (missing_required_fields(profile) or [None])[0]

        applied: dict[str, Any] = {}
        made_progress = False
        clarifier_error: str | None = None

        # 1) 数值字段确定性兜底：用户这句基本就是个金额 → 直接填 target，跳过 LLM
        direct = try_direct_numeric_fill(target_field, request.message)
        if direct is not None and direct.model_dump(exclude_none=True):
            merged = merge_profile(profile, direct)
            if merged.model_dump() != profile.model_dump():
                profile = merged
                session.draft_profile_json = profile.model_dump_json()
                applied = direct.model_dump(exclude_none=True)
                made_progress = True
                mode = "direct"

        # 2) 否则走带 target_field 的 LLM 澄清
        if not made_progress:
            result = clarifier_service.clarify(profile, request.message, target_field=target_field)
            clarifier_error = result.error
            if result.decision is not None:
                updates = result.decision.extracted_updates
                applied = updates.model_dump(exclude_none=True)
                if applied:
                    merged = merge_profile(profile, updates)
                    if merged.model_dump() != profile.model_dump():
                        profile = merged
                        session.draft_profile_json = profile.model_dump_json()
                        made_progress = True
            if made_progress:
                mode = "llm"
            else:
                # 真的调到了 LLM 但什么都没抽到 = 乱输入；没配 API key = manual_fallback
                mode = "no_progress" if result.decision is not None else result.mode

        if made_progress:
            session.clarification_count = 0
        else:
            session.clarification_count += 1

        session.current_question = fallback_question(profile, session.response_language)
        session.status = (
            "ready_to_match"
            if not missing_required_fields(profile)
            else "awaiting_clarification"
        )
        session.updated_at = utcnow()
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="matching_clarification_processed",
            payload={
                "mode": mode,
                "made_progress": made_progress,
                "applied_updates": applied,
                "error": clarifier_error,
            },
        )
        db.commit()
        return {
            **_serialize_session(session, db),
            "clarifier_mode": mode,
            "clarifier_error": clarifier_error,
        }

    @app.post("/crossbridge/v1/loan-matching/sessions/{session_id}/match")
    def run_product_match(
        session_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        session = get_matching_session(session_id, db)
        profile = _load_profile_json(session.draft_profile_json)
        missing = missing_required_fields(profile)
        if missing:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "required fields are incomplete",
                    "missing_required_fields": missing,
                },
            )
        db.execute(delete(MatchResult).where(MatchResult.session_id == session.id))
        matched = match_products(profile, list_active_products(db))
        for rank, item in enumerate(matched, start=1):
            db.add(
                MatchResult(
                    id=str(uuid.uuid4()),
                    session_id=session.id,
                    product_id=item["product"]["product_id"],
                    rank=rank,
                    score=item["score"],
                    reasons_json=_json(item["reasons"]),
                    product_snapshot_json=_json(
                        {
                            **item["product"],
                            "needs_rm_confirmation": item["needs_rm_confirmation"],
                        }
                    ),
                    created_at=utcnow(),
                )
            )
        session.status = "matched"
        session.updated_at = utcnow()
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="loan_products_matched",
            payload={"matched_product_ids": [item["product"]["product_id"] for item in matched]},
        )
        db.commit()
        return _serialize_session(session, db)

    @app.post("/crossbridge/v1/loan-matching/sessions/{session_id}/save-profile")
    def save_sme_profile(
        session_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        session = get_matching_session(session_id, db)
        if session.status == "discarded":
            raise HTTPException(status_code=409, detail="discarded session cannot be saved")
        profile = _load_profile_json(session.draft_profile_json)
        now = utcnow()
        saved = db.get(SmeProfile, session.sme_id)
        if saved is None:
            saved = SmeProfile(
                sme_id=session.sme_id,
                profile_json=profile.model_dump_json(),
                confirmed_at=now,
                updated_at=now,
            )
            db.add(saved)
        else:
            saved.profile_json = profile.model_dump_json()
            saved.confirmed_at = now
            saved.updated_at = now
        session.status = "saved"
        session.updated_at = now
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="sme_profile_saved",
            payload={"profile": _serialize_profile(profile)},
        )
        db.commit()
        return {"saved": True, "sme_id": session.sme_id, "profile": _serialize_profile(profile)}

    @app.post("/crossbridge/v1/loan-matching/sessions/{session_id}/discard")
    def discard_matching_session(
        session_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        session = get_matching_session(session_id, db)
        session.status = "discarded"
        session.updated_at = utcnow()
        _audit(
            db,
            sme_id=session.sme_id,
            session_id=session.id,
            event_type="matching_session_discarded",
            payload={},
        )
        db.commit()
        return {"discarded": True, "session_id": session.id}

    @app.get("/crossbridge/v1/sme-profiles/{sme_id}")
    def read_sme_profile(sme_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        profile = db.get(SmeProfile, sme_id)
        return {
            "sme_id": sme_id,
            "demo_sme_name": DEMO_SME_NAME if sme_id == DEMO_SME_ID else None,
            "profile": _serialize_profile(_load_profile_json(profile.profile_json))
            if profile
            else None,
        }

    @app.delete("/crossbridge/v1/sme-profiles/{sme_id}")
    def clear_sme_profile(sme_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        profile = db.get(SmeProfile, sme_id)
        if profile is not None:
            db.delete(profile)
        _audit(
            db,
            sme_id=sme_id,
            event_type="sme_profile_cleared",
            payload={"profile_existed": profile is not None},
        )
        db.commit()
        return {"cleared": True, "sme_id": sme_id}

    app.state.SessionLocal = SessionLocal
    app.state.database_url = resolved_database_url
    return app


app = create_app()

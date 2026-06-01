from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .catalog import build_catalog, get_product_overlay, get_scenario
from .db import build_engine, build_session_factory, get_database_url, run_migrations
from .models import (
    DocumentAuditEvent,
    DocumentChecklistState,
    DocumentOfficialFormDraft,
    DocumentPackage,
    DocumentTemplateDraft,
    DocumentTradeTermsAcceptance,
)
from .official_forms import (
    cache_status,
    cached_form_path,
    forms_for_package,
    get_registered_form,
    load_form_registry,
)
from .schemas import (
    CreatePackageRequest,
    UpdateChecklistRequest,
    UpdateOfficialFormDraftRequest,
    UpdateProductRequest,
)

API_PREFIX = "/crossbridge-documents/v1"


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _audit(
    db: Session,
    *,
    sme_id: str,
    event_type: str,
    payload: dict[str, Any],
    package_id: str | None = None,
) -> None:
    db.add(
        DocumentAuditEvent(
            id=str(uuid.uuid4()),
            sme_id=sme_id,
            package_id=package_id,
            event_type=event_type,
            payload_json=_json(payload),
            created_at=utcnow(),
        )
    )


def create_app(
    *,
    database_url: str | None = None,
    migrate_on_startup: bool = True,
) -> FastAPI:
    resolved_database_url = database_url or get_database_url()
    engine = build_engine(resolved_database_url)
    session_factory = build_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if migrate_on_startup:
            run_migrations(resolved_database_url)
        # Load the read-only catalog + official-form registry once into app state.
        app.state.catalog = build_catalog()
        app.state.form_registry = load_form_registry()
        yield

    app = FastAPI(title="CrossBridge Document Preparation API", lifespan=lifespan)
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

    def catalog() -> dict[str, Any]:
        # Lifespan populates this; fall back to a fresh build for safety in tests.
        cat = getattr(app.state, "catalog", None)
        if cat is None:
            cat = build_catalog()
            app.state.catalog = cat
        return cat

    def form_registry() -> dict[str, Any]:
        reg = getattr(app.state, "form_registry", None)
        if reg is None:
            reg = load_form_registry()
            app.state.form_registry = reg
        return reg

    def _current_terms_sha() -> str:
        return form_registry().get("trade_terms", {}).get("sha256", "")

    def _trade_terms_accepted(db: Session, sme_id: str, terms_sha: str) -> bool:
        if not terms_sha:
            return False
        return db.scalars(
            select(DocumentTradeTermsAcceptance)
            .where(DocumentTradeTermsAcceptance.sme_id == sme_id)
            .where(DocumentTradeTermsAcceptance.terms_sha256 == terms_sha)
        ).first() is not None

    def _get_registered_form_or_404(form_id: str, package: DocumentPackage) -> dict[str, Any]:
        """Only registry-fixed form_ids that belong to the package's scenario are allowed."""
        form = get_registered_form(form_registry(), form_id)
        if form is None or package.scenario_code not in form.get("scenario_codes", []):
            raise HTTPException(status_code=404, detail="unknown form_id for this package")
        return form

    # ---- serialization ----------------------------------------------------

    def _checklist_with_state(scenario: dict[str, Any], states: dict[str, bool]) -> dict[str, Any]:
        groups = {}
        for group_key, group in scenario["checklist"].items():
            groups[group_key] = {
                "label_zh": group["label_zh"],
                "label_en": group["label_en"],
                "items": [
                    {**item, "checked": states.get(item["code"], False)}
                    for item in group["items"]
                ],
            }
        return groups

    def _official_forms_view(db: Session, package: DocumentPackage) -> list[dict[str, Any]]:
        """Official BOCHK forms for the package, product-exact matches first.

        ``cache_status`` is derived from the gitignored local cache: a deployment that
        has not run ``scripts/fetch_official_forms.py`` reports ``missing`` and the
        frontend shows a download hint instead of a fabricated form.
        """
        reg = form_registry()
        forms = forms_for_package(
            reg,
            scenario_code=package.scenario_code,
            selected_product_id=package.selected_product_id,
        )
        draft_rows = db.scalars(
            select(DocumentOfficialFormDraft).where(
                DocumentOfficialFormDraft.package_id == package.id
            )
        ).all()
        drafts_by_key = {(row.form_id, row.source_sha256): row for row in draft_rows}
        out: list[dict[str, Any]] = []
        for form in forms:
            sha = form["source_sha256"]
            draft = drafts_by_key.get((form["form_id"], sha))
            has_values = bool(draft and json.loads(draft.values_json or "{}"))
            out.append(
                {
                    "form_id": form["form_id"],
                    "name_zh": form.get("name_zh", ""),
                    "name_en": form.get("name_en", ""),
                    "source_url": form.get("source_url", ""),
                    "expected_pages": form.get("expected_pages"),
                    "expected_field_count": form.get("expected_field_count"),
                    "trade_terms_required": bool(form.get("trade_terms_required")),
                    "product_match": package.selected_product_id in form.get("product_ids", []),
                    "cache_status": cache_status(form),
                    "has_draft": has_values,
                    # Maps high-trust semantic codes (swift_bic, payment_amount, ...) to
                    # this form's AcroForm field names, so the client runs validation only
                    # against fields that are actually mapped to the official form.
                    "validation_bindings": form.get("validation_bindings", {}),
                }
            )
        return out

    def _overlay_with_state(overlay: dict[str, Any] | None, states: dict[str, bool]) -> dict[str, Any] | None:
        if overlay is None:
            return None
        return {
            **overlay,
            "checklist_items": [
                {**item, "checked": states.get(item["code"], False)}
                for item in overlay.get("checklist_items", [])
            ],
        }

    def _validate_product_for_scenario(
        cat: dict[str, Any], product_id: str | None, scenario_code: str
    ) -> dict[str, Any] | None:
        if product_id is None:
            return None
        overlay = get_product_overlay(cat, product_id)
        if overlay is None:
            raise HTTPException(status_code=400, detail="unknown selected_product_id")
        if scenario_code not in overlay.get("scenarios", []):
            raise HTTPException(
                status_code=400,
                detail="selected_product_id is incompatible with scenario_code",
            )
        return overlay

    def _allowed_checklist_codes(cat: dict[str, Any], package: DocumentPackage) -> set[str]:
        scenario = get_scenario(cat, package.scenario_code)
        if scenario is None:
            raise HTTPException(status_code=500, detail="scenario not found in catalog")
        allowed = {
            item["code"]
            for group in scenario["checklist"].values()
            for item in group["items"]
        }
        overlay = _validate_product_for_scenario(
            cat, package.selected_product_id, package.scenario_code
        )
        if overlay:
            allowed.update(item["code"] for item in overlay.get("checklist_items", []))
        return allowed

    def _serialize_package(db: Session, package: DocumentPackage) -> dict[str, Any]:
        cat = catalog()
        scenario = get_scenario(cat, package.scenario_code)
        if scenario is None:
            raise HTTPException(status_code=500, detail="scenario not found in catalog")

        state_rows = db.scalars(
            select(DocumentChecklistState).where(
                DocumentChecklistState.package_id == package.id
            )
        ).all()
        states = {row.item_code: row.checked for row in state_rows}

        overlay = _validate_product_for_scenario(
            cat, package.selected_product_id, package.scenario_code
        )

        reg = form_registry()
        terms_sha = _current_terms_sha()
        return {
            "id": package.id,
            "sme_id": package.sme_id,
            "scenario_code": package.scenario_code,
            "catalog_version": package.catalog_version,
            "scenario_label_zh": scenario["label_zh"],
            "scenario_label_en": scenario["label_en"],
            "selected_product_id": package.selected_product_id,
            "origin_matching_session_id": package.origin_matching_session_id,
            "status": package.status,
            "checklist": _checklist_with_state(scenario, states),
            "product_overlay": _overlay_with_state(overlay, states),
            # Custom self-made templates are retired (see PATCH .../templates -> 410 Gone);
            # document preparation now fills genuine official BOCHK forms.
            "official_forms": _official_forms_view(db, package),
            "trade_terms": {
                "url": reg.get("trade_terms", {}).get("url", ""),
                "sha256": terms_sha,
                "accepted": _trade_terms_accepted(db, package.sme_id, terms_sha),
            },
            "registry_version": reg.get("registry_version", ""),
            "catalog_note_zh": cat.get("note_zh", ""),
            "catalog_note_en": cat.get("note_en", ""),
        }

    def _get_package_or_404(db: Session, package_id: str) -> DocumentPackage:
        package = db.get(DocumentPackage, package_id)
        if package is None:
            raise HTTPException(status_code=404, detail="package not found")
        return package

    # ---- endpoints --------------------------------------------------------

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{API_PREFIX}/catalog")
    def read_catalog() -> dict[str, Any]:
        cat = catalog()
        return {
            "catalog_version": cat.get("catalog_version"),
            "catalog_status": cat.get("catalog_status"),
            "note_zh": cat.get("note_zh", ""),
            "note_en": cat.get("note_en", ""),
            "scenarios": cat["scenarios"],
            "templates": cat["templates"],
            "product_overlays": cat["product_overlays"],
        }

    @app.post(f"{API_PREFIX}/packages")
    def create_or_resume_package(
        request: CreatePackageRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        cat = catalog()
        if get_scenario(cat, request.scenario_code) is None:
            raise HTTPException(status_code=400, detail="unknown scenario_code")
        _validate_product_for_scenario(
            cat, request.selected_product_id, request.scenario_code
        )

        # Resume an existing active package for the same SME + scenario, else create.
        existing = db.scalars(
            select(DocumentPackage)
            .where(DocumentPackage.sme_id == request.sme_id)
            .where(DocumentPackage.scenario_code == request.scenario_code)
            .where(DocumentPackage.status == "active")
        ).first()

        if existing is not None:
            resumed = True
            package = existing
            if request.selected_product_id is not None:
                package.selected_product_id = request.selected_product_id
            if request.origin_matching_session_id is not None:
                package.origin_matching_session_id = request.origin_matching_session_id
            package.catalog_version = cat["catalog_version"]
            package.updated_at = utcnow()
        else:
            resumed = False
            package = DocumentPackage(
                id=str(uuid.uuid4()),
                sme_id=request.sme_id,
                scenario_code=request.scenario_code,
                catalog_version=cat["catalog_version"],
                selected_product_id=request.selected_product_id,
                origin_matching_session_id=request.origin_matching_session_id,
                status="active",
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            db.add(package)

        _audit(
            db,
            sme_id=request.sme_id,
            package_id=package.id,
            event_type="document_package_resumed" if resumed else "document_package_created",
            payload={
                "scenario_code": request.scenario_code,
                "selected_product_id": package.selected_product_id,
                "origin_matching_session_id": package.origin_matching_session_id,
            },
        )
        db.commit()
        db.refresh(package)
        result = _serialize_package(db, package)
        result["resumed"] = resumed
        return result

    @app.get(f"{API_PREFIX}/packages/{{package_id}}")
    def read_package(package_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        return _serialize_package(db, _get_package_or_404(db, package_id))

    @app.patch(f"{API_PREFIX}/packages/{{package_id}}/product")
    def update_product(
        package_id: str, request: UpdateProductRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        # Switching product preserves base-checklist progress (those rows are untouched);
        # only the product overlay shown changes.
        _validate_product_for_scenario(
            catalog(), request.selected_product_id, package.scenario_code
        )
        package.selected_product_id = request.selected_product_id
        package.updated_at = utcnow()
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_package_product_changed",
            payload={"selected_product_id": request.selected_product_id},
        )
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.patch(f"{API_PREFIX}/packages/{{package_id}}/checklist")
    def update_checklist(
        package_id: str, request: UpdateChecklistRequest, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        if request.item_code not in _allowed_checklist_codes(catalog(), package):
            raise HTTPException(status_code=400, detail="item_code is not part of the active package")
        row = db.scalars(
            select(DocumentChecklistState)
            .where(DocumentChecklistState.package_id == package.id)
            .where(DocumentChecklistState.item_code == request.item_code)
        ).first()
        if row is None:
            row = DocumentChecklistState(
                id=str(uuid.uuid4()),
                package_id=package.id,
                item_code=request.item_code,
                checked=request.checked,
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            db.add(row)
        else:
            row.checked = request.checked
            row.updated_at = utcnow()
        package.updated_at = utcnow()
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_checklist_updated",
            payload={"item_code": request.item_code, "checked": request.checked},
        )
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.patch(f"{API_PREFIX}/packages/{{package_id}}/templates/{{template_code}}")
    def update_template_gone(package_id: str, template_code: str) -> dict[str, Any]:
        # Self-made fill-in templates are retired in favour of genuine official BOCHK
        # forms (PATCH .../forms/{form_id}/draft). Kept registered so stale clients get
        # a clear 410 instead of silently writing to a dead contract.
        raise HTTPException(
            status_code=410,
            detail="custom templates are retired; prepare documents with official BOCHK forms",
        )

    # ---- official BOCHK forms --------------------------------------------

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/trade-terms/accept")
    def accept_trade_terms(
        package_id: str, request: Request, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        terms_sha = _current_terms_sha()
        if not terms_sha:
            raise HTTPException(status_code=500, detail="trade-finance terms sha not configured")
        if not _trade_terms_accepted(db, package.sme_id, terms_sha):
            db.add(
                DocumentTradeTermsAcceptance(
                    id=str(uuid.uuid4()),
                    sme_id=package.sme_id,
                    terms_sha256=terms_sha,
                    accepted_at=utcnow(),
                    terms_url=form_registry().get("trade_terms", {}).get("url"),
                    user_agent=request.headers.get("user-agent"),
                )
            )
            _audit(
                db,
                sme_id=package.sme_id,
                package_id=package.id,
                event_type="document_trade_terms_accepted",
                payload={"terms_sha256": terms_sha},
            )
        package.updated_at = utcnow()
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.get(f"{API_PREFIX}/packages/{{package_id}}/forms/{{form_id}}/pdf")
    def get_official_form_pdf(
        package_id: str, form_id: str, db: Session = Depends(get_db)
    ) -> FileResponse:
        package = _get_package_or_404(db, package_id)
        form = _get_registered_form_or_404(form_id, package)
        if form.get("trade_terms_required") and not _trade_terms_accepted(
            db, package.sme_id, _current_terms_sha()
        ):
            raise HTTPException(
                status_code=403,
                detail="accept the trade-finance terms before downloading this form",
            )
        status = cache_status(form)
        if status != "ready":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"official form not in local cache (status={status}); "
                    "run scripts/fetch_official_forms.py on the deployment host"
                ),
            )
        # Stream the original (encrypted) BOCHK PDF unchanged; the client fills it via
        # PDF.js annotationStorage and exports with saveDocument().
        return FileResponse(cached_form_path(form), media_type="application/pdf")

    @app.get(f"{API_PREFIX}/packages/{{package_id}}/forms/{{form_id}}/draft")
    def read_official_form_draft(
        package_id: str, form_id: str, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        form = _get_registered_form_or_404(form_id, package)
        sha = form["source_sha256"]
        row = db.scalars(
            select(DocumentOfficialFormDraft)
            .where(DocumentOfficialFormDraft.package_id == package.id)
            .where(DocumentOfficialFormDraft.form_id == form_id)
            .where(DocumentOfficialFormDraft.source_sha256 == sha)
        ).first()
        return {
            "form_id": form_id,
            "source_sha256": sha,
            "values": json.loads(row.values_json) if row else {},
        }

    @app.patch(f"{API_PREFIX}/packages/{{package_id}}/forms/{{form_id}}/draft")
    def update_official_form_draft(
        package_id: str,
        form_id: str,
        request: UpdateOfficialFormDraftRequest,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        form = _get_registered_form_or_404(form_id, package)
        # Persist only registry-whitelisted AcroForm fields; drop anything else the
        # viewer may have sent (defence against tampering / unexpected annotations).
        allowed = set(form.get("allowed_fields", []))
        filtered = {k: v for k, v in (request.values or {}).items() if k in allowed}
        sha = form["source_sha256"]
        row = db.scalars(
            select(DocumentOfficialFormDraft)
            .where(DocumentOfficialFormDraft.package_id == package.id)
            .where(DocumentOfficialFormDraft.form_id == form_id)
            .where(DocumentOfficialFormDraft.source_sha256 == sha)
        ).first()
        if row is None:
            row = DocumentOfficialFormDraft(
                id=str(uuid.uuid4()),
                package_id=package.id,
                form_id=form_id,
                source_sha256=sha,
                values_json=_json(filtered),
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            db.add(row)
        else:
            row.values_json = _json(filtered)
            row.updated_at = utcnow()
        package.updated_at = utcnow()
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_official_form_draft_saved",
            payload={"form_id": form_id, "field_count": len(filtered)},
        )
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/forms/{{form_id}}/exported")
    def mark_official_form_exported(
        package_id: str, form_id: str, db: Session = Depends(get_db)
    ) -> dict[str, str]:
        package = _get_package_or_404(db, package_id)
        _get_registered_form_or_404(form_id, package)
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_official_form_exported",
            payload={"form_id": form_id},
        )
        db.commit()
        return {"status": "ok"}

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/forms/{{form_id}}/printed")
    def mark_official_form_printed(
        package_id: str, form_id: str, db: Session = Depends(get_db)
    ) -> dict[str, str]:
        package = _get_package_or_404(db, package_id)
        _get_registered_form_or_404(form_id, package)
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_official_form_printed",
            payload={"form_id": form_id},
        )
        db.commit()
        return {"status": "ok"}

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/reset")
    def reset_package(package_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        db.query(DocumentChecklistState).filter(
            DocumentChecklistState.package_id == package.id
        ).delete()
        # Clear retired custom-template drafts and the new official-form drafts.
        # Trade-terms acceptance is keyed by sme_id (not package) and intentionally
        # survives a package reset.
        db.query(DocumentTemplateDraft).filter(
            DocumentTemplateDraft.package_id == package.id
        ).delete()
        db.query(DocumentOfficialFormDraft).filter(
            DocumentOfficialFormDraft.package_id == package.id
        ).delete()
        package.updated_at = utcnow()
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_package_reset",
            payload={},
        )
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/printed")
    def mark_printed(package_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_package_printed",
            payload={},
        )
        db.commit()
        return {"status": "ok"}

    return app


app = create_app()

from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .catalog import build_catalog, get_product_overlay, get_scenario, get_template
from .db import build_engine, build_session_factory, get_database_url, run_migrations
from .models import (
    DocumentAuditEvent,
    DocumentChecklistState,
    DocumentPackage,
    DocumentTemplateDraft,
)
from .schemas import (
    CreatePackageRequest,
    UpdateChecklistRequest,
    UpdateProductRequest,
    UpdateTemplateRequest,
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
        # Load the read-only catalog once into app state.
        app.state.catalog = build_catalog()
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

    def _templates_with_drafts(
        cat: dict[str, Any], drafts: dict[str, dict], scenario_code: str
    ) -> list[dict[str, Any]]:
        out = []
        for tpl in cat["templates"]:
            if scenario_code not in tpl.get("scenario_codes", [scenario_code]):
                continue
            out.append({**tpl, "content": drafts.get(tpl["code"], {})})
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

        draft_rows = db.scalars(
            select(DocumentTemplateDraft).where(
                DocumentTemplateDraft.package_id == package.id
            )
        ).all()
        drafts = {row.template_code: json.loads(row.content_json or "{}") for row in draft_rows}

        overlay = _validate_product_for_scenario(
            cat, package.selected_product_id, package.scenario_code
        )

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
            "templates": _templates_with_drafts(cat, drafts, package.scenario_code),
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
    def update_template(
        package_id: str,
        template_code: str,
        request: UpdateTemplateRequest,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        template = get_template(catalog(), template_code)
        if (
            template is None
            or package.scenario_code not in template.get("scenario_codes", [package.scenario_code])
        ):
            raise HTTPException(status_code=400, detail="unknown template_code")
        row = db.scalars(
            select(DocumentTemplateDraft)
            .where(DocumentTemplateDraft.package_id == package.id)
            .where(DocumentTemplateDraft.template_code == template_code)
        ).first()
        if row is None:
            row = DocumentTemplateDraft(
                id=str(uuid.uuid4()),
                package_id=package.id,
                template_code=template_code,
                content_json=_json(request.content),
                updated_at=utcnow(),
            )
            db.add(row)
        else:
            row.content_json = _json(request.content)
            row.updated_at = utcnow()
        package.updated_at = utcnow()
        _audit(
            db,
            sme_id=package.sme_id,
            package_id=package.id,
            event_type="document_template_saved",
            payload={"template_code": template_code},
        )
        db.commit()
        db.refresh(package)
        return _serialize_package(db, package)

    @app.post(f"{API_PREFIX}/packages/{{package_id}}/reset")
    def reset_package(package_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
        package = _get_package_or_404(db, package_id)
        db.query(DocumentChecklistState).filter(
            DocumentChecklistState.package_id == package.id
        ).delete()
        db.query(DocumentTemplateDraft).filter(
            DocumentTemplateDraft.package_id == package.id
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

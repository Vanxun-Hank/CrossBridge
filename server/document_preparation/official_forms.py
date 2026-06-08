from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FORM_REGISTRY_PATH = ROOT / "data" / "document_preparation" / "form_registry.json"
FORM_CACHE_DIR = ROOT / "data" / "document_preparation" / "official_forms_cache"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_form_registry(path: Path = FORM_REGISTRY_PATH) -> dict[str, Any]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    forms = registry.get("forms") or []
    form_ids = [form["form_id"] for form in forms]
    if len(form_ids) != len(set(form_ids)):
        raise ValueError("official form registry contains duplicate form_id values")
    return registry


def get_registered_form(registry: dict[str, Any], form_id: str) -> dict[str, Any] | None:
    return next((form for form in registry["forms"] if form["form_id"] == form_id), None)


def cached_form_path(form: dict[str, Any]) -> Path:
    return FORM_CACHE_DIR / form["cache_filename"]


def cache_status(form: dict[str, Any]) -> str:
    path = cached_form_path(form)
    if not path.is_file():
        return "missing"
    return "ready" if _sha256(path) == form["source_sha256"] else "sha_mismatch"


def forms_for_package(
    registry: dict[str, Any],
    *,
    scenario_code: str,
    selected_product_id: str | None,
) -> list[dict[str, Any]]:
    forms = [
        form
        for form in registry["forms"]
        if scenario_code in form.get("scenario_codes", [])
    ]
    return sorted(
        forms,
        key=lambda form: (
            0 if selected_product_id in form.get("product_ids", []) else 1,
            form["form_id"],
        ),
    )

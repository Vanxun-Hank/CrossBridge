from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_CATALOG_PATH = ROOT / "data" / "document_preparation" / "scenario_catalog.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenario_catalog(path: Path = SCENARIO_CATALOG_PATH) -> dict[str, Any]:
    catalog = _load_json(path)
    if catalog.get("catalog_status") != "source_verified_pending_human_review":
        raise ValueError("F2 scenario catalog status missing or unsupported")
    if not catalog.get("scenarios") or not catalog.get("templates"):
        raise ValueError("F2 scenario catalog must define scenarios and templates")
    return catalog


def build_catalog() -> dict[str, Any]:
    """Load the F2-owned readonly snapshot without reading Function 1 at runtime."""
    catalog = load_scenario_catalog()
    if not catalog.get("product_overlays"):
        raise ValueError(
            "F2 product snapshot is missing. Run scripts/sync_document_preparation_catalog.py"
        )
    return catalog


def get_scenario(catalog: dict[str, Any], scenario_code: str) -> dict[str, Any] | None:
    return next((s for s in catalog["scenarios"] if s["code"] == scenario_code), None)


def get_template(catalog: dict[str, Any], template_code: str) -> dict[str, Any] | None:
    return next((t for t in catalog["templates"] if t["code"] == template_code), None)


def get_product_overlay(catalog: dict[str, Any], product_id: str) -> dict[str, Any] | None:
    return catalog["product_overlays"].get(product_id)

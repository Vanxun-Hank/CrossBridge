#!/usr/bin/env python3
"""Generate the Function 2 readonly product snapshot from the F1 official catalog."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_PRODUCTS_PATH = ROOT / "data" / "official_products" / "bochk_products_latest.json"
DOCUMENT_CATALOG_PATH = ROOT / "data" / "document_preparation" / "scenario_catalog.json"

UNKNOWN_ZH = "需客户经理确认"
UNKNOWN_EN = "Subject to relationship-manager confirmation"
IMPORT_F1_SCENARIOS = {"overseas_procurement", "cross_border_ecommerce"}
EXPORT_F1_SCENARIOS = {"export_trade"}

DOCUMENT_TRANSLATIONS = {
    "供应商发票": "Supplier invoice",
    "信用证": "Letter of Credit",
    "采购订单或销售合同": "Purchase order or sales contract",
    "发票": "Invoice",
    "货物交付证明": "Evidence of delivery of goods",
    "原信用证（master L/C）": "Original Letter of Credit (master L/C)",
    "标明可转让的信用证": "Letter of Credit marked as transferable",
    "出口单据": "Export documents",
    "出口托收单据": "Export collection documents",
    "信用证项下出口单据": "Export documents under the Letter of Credit",
    "核心买方付款承诺": "Anchor buyer payment undertaking",
    "核心买方提供的采购订单（PO）或经核心买方确认的销售订单（SO）": (
        "Purchase Order (PO) provided by the anchor buyer or Sales Order (SO) "
        "confirmed by the anchor buyer"
    ),
}

FEE_TRANSLATIONS = {
    "手续费：融资金额的 1/4%，最低 HK$500": "Handling fee: 1/4% of financing amount, minimum HK$500",
    "手续费：融资金额的 1/8%，最低 HK$350": "Handling fee: 1/8% of financing amount, minimum HK$350",
    "手续费：融资金额的 1/4%，最低 HK$450": "Handling fee: 1/4% of financing amount, minimum HK$450",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _f2_scenarios_for(product: dict[str, Any]) -> list[str]:
    scenarios = set(product.get("scenarios") or [])
    result: list[str] = []
    if scenarios & IMPORT_F1_SCENARIOS:
        result.append("import_payment")
    if scenarios & EXPORT_F1_SCENARIOS:
        result.append("export_fulfillment")
    return result


def _translate_documents(documents: list[str]) -> list[str]:
    missing = [item for item in documents if item not in DOCUMENT_TRANSLATIONS]
    if missing:
        raise ValueError(f"Missing English document translations: {missing}")
    return [DOCUMENT_TRANSLATIONS[item] for item in documents]


def _translate_fee(fee_text: str | None) -> str:
    if not fee_text:
        return ""
    if fee_text not in FEE_TRANSLATIONS:
        raise ValueError(f"Missing English fee translation: {fee_text}")
    return FEE_TRANSLATIONS[fee_text]


def _product_overlay(product: dict[str, Any]) -> dict[str, Any]:
    localization = (product.get("localization") or {}).get("en") or {}
    required_documents = product.get("required_documents") or []
    required_documents_en = _translate_documents(required_documents)
    source_refs = product.get("source_refs") or []
    checklist_items = [
        {
            "code": f"product_{product['id']}_doc_{index}",
            "label_zh": document,
            "label_en": required_documents_en[index - 1],
            "evidence_level": "official_product_document_hint",
            "source_refs": source_refs,
        }
        for index, document in enumerate(required_documents, start=1)
    ]
    return {
        "product_id": product["id"],
        "product_name": product.get("product_name") or product["id"],
        "product_name_en": localization.get("product_name") or product["id"],
        "product_description": product.get("product_description") or "",
        "product_description_en": localization.get("product_description") or "",
        "scenarios": _f2_scenarios_for(product),
        "required_documents": required_documents,
        "required_documents_en": required_documents_en,
        "checklist_items": checklist_items,
        "has_published_documents": bool(required_documents),
        "fee_text": product.get("fee_text") or "",
        "fee_text_en": _translate_fee(product.get("fee_text")),
        "has_published_fee": bool(product.get("fee_text")),
        "source_refs": source_refs,
        "source_url": product.get("source_url") or "",
        "source_title": product.get("source_title") or "",
        "source_checked_at": product.get("source_checked_at"),
        "source_content_hash": product.get("source_content_hash"),
        "review_status": product.get("review_status") or "",
        "unknown_label_zh": UNKNOWN_ZH,
        "unknown_label_en": UNKNOWN_EN,
    }


def main() -> None:
    official_catalog = _load(OFFICIAL_PRODUCTS_PATH)
    document_catalog = _load(DOCUMENT_CATALOG_PATH)
    products = official_catalog["products"]
    document_catalog["product_overlay_source_catalog_version"] = official_catalog.get("catalog_version")
    document_catalog["product_overlay_generated_at"] = datetime.now(UTC).isoformat()
    document_catalog["product_overlays"] = {
        product["id"]: _product_overlay(product)
        for product in sorted(products, key=lambda item: item["id"])
    }
    DOCUMENT_CATALOG_PATH.write_text(
        json.dumps(document_catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(products)} product overlays to {DOCUMENT_CATALOG_PATH}")


if __name__ == "__main__":
    main()

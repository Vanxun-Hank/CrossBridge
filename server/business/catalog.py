from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import LoanProduct

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_CATALOG_PATH = ROOT / "data" / "official_products" / "bochk_products_latest.json"

DEMO_PRODUCTS = [
    {
        "id": "demo_overseas_procurement_working_capital",
        "product_name": "海外采购周转资金方案",
        "business_scenario": "overseas_procurement",
        "purposes": ["procurement_payment", "working_capital"],
        "min_requested_amount_hkd": 100_000,
        "max_requested_amount_hkd": 5_000_000,
        "min_annual_turnover_hkd": 1_000_000,
        "loan_limit_text": "DEMO ONLY：HKD 100,000 至 HKD 5,000,000",
        "tenor_text": "DEMO ONLY：最长 24 个月",
        "repayment_method_text": "DEMO ONLY：按月还款，实际安排需客户经理确认",
        "application_thresholds": ["DEMO ONLY：需提供采购用途资料", "实际资格需由银行审批"],
        "localization": {
            "en": {
                "product_name": "Overseas Procurement Working Capital Plan",
                "loan_limit_text": "DEMO ONLY: HKD 100,000 to HKD 5,000,000",
                "tenor_text": "DEMO ONLY: up to 24 months",
                "repayment_method_text": "DEMO ONLY: monthly repayments; actual arrangement requires relationship-manager confirmation",
                "application_thresholds": ["DEMO ONLY: procurement-purpose documents required", "Actual eligibility is subject to bank approval"],
            }
        },
    },
    {
        "id": "demo_cross_border_ecommerce_stocking",
        "product_name": "跨境电商备货方案",
        "business_scenario": "cross_border_ecommerce",
        "purposes": ["stocking", "working_capital"],
        "min_requested_amount_hkd": 100_000,
        "max_requested_amount_hkd": 3_000_000,
        "min_annual_turnover_hkd": 800_000,
        "loan_limit_text": "DEMO ONLY：HKD 100,000 至 HKD 3,000,000",
        "tenor_text": "DEMO ONLY：最长 18 个月",
        "repayment_method_text": "DEMO ONLY：分期还款，实际安排需客户经理确认",
        "application_thresholds": ["DEMO ONLY：需提供备货或销售资料", "实际资格需由银行审批"],
        "localization": {
            "en": {
                "product_name": "Cross-Border E-Commerce Inventory Plan",
                "loan_limit_text": "DEMO ONLY: HKD 100,000 to HKD 3,000,000",
                "tenor_text": "DEMO ONLY: up to 18 months",
                "repayment_method_text": "DEMO ONLY: instalment repayments; actual arrangement requires relationship-manager confirmation",
                "application_thresholds": ["DEMO ONLY: inventory or sales documents required", "Actual eligibility is subject to bank approval"],
            }
        },
    },
    {
        "id": "demo_export_order_fulfillment",
        "product_name": "出口订单履约方案",
        "business_scenario": "export_trade",
        "purposes": ["order_fulfillment", "working_capital"],
        "min_requested_amount_hkd": 200_000,
        "max_requested_amount_hkd": 8_000_000,
        "min_annual_turnover_hkd": 1_500_000,
        "loan_limit_text": "DEMO ONLY：HKD 200,000 至 HKD 8,000,000",
        "tenor_text": "DEMO ONLY：最长 12 个月",
        "repayment_method_text": "DEMO ONLY：按订单安排，实际方式需客户经理确认",
        "application_thresholds": ["DEMO ONLY：需提供出口订单资料", "实际资格需由银行审批"],
        "localization": {
            "en": {
                "product_name": "Export Order Fulfilment Plan",
                "loan_limit_text": "DEMO ONLY: HKD 200,000 to HKD 8,000,000",
                "tenor_text": "DEMO ONLY: up to 12 months",
                "repayment_method_text": "DEMO ONLY: arranged by order; actual method requires relationship-manager confirmation",
                "application_thresholds": ["DEMO ONLY: export-order documents required", "Actual eligibility is subject to bank approval"],
            }
        },
    },
]


def _catalog_values(item: dict, *, demo_only: bool) -> dict:
    source_checked_at = item.get("source_checked_at")
    values = {
        **item,
        "business_scenario": item["business_scenario"],
        "scenarios_json": json.dumps(
            item.get("scenarios", [item["business_scenario"]]), ensure_ascii=False
        ),
        "purposes_json": json.dumps(item["purposes"], ensure_ascii=False),
        "application_thresholds_json": json.dumps(
            item["application_thresholds"], ensure_ascii=False
        ),
        "interest_rate_text": item.get(
            "interest_rate_text",
            "DEMO ONLY：实际利率需客户经理确认"
            if demo_only
            else "BOCHK 公开页面未列明，需客户经理确认",
        ),
        "fee_text": item.get("fee_text", ""),
        "public_guidance_json": json.dumps(item.get("public_guidance", []), ensure_ascii=False),
        "required_documents_json": json.dumps(item.get("required_documents", []), ensure_ascii=False),
        "localization_json": json.dumps(item.get("localization", {}), ensure_ascii=False),
        "source_refs_json": json.dumps(item.get("source_refs", []), ensure_ascii=False),
        "review_notes_json": json.dumps(item.get("review_notes", []), ensure_ascii=False),
        "source_checked_at": (
            datetime.fromisoformat(source_checked_at) if source_checked_at else None
        ),
        "demo_only": demo_only,
        "active": item.get("active", True),
    }
    for key in (
        "loan_limit_min_hkd",
        "loan_limit_max_hkd",
        "extracted_at",
        "field_extractions",
    ):
        values.pop(key, None)
    return values


def _seed_products(db: Session, products: list[dict], *, demo_only: bool) -> None:
    for item in products:
        product = db.get(LoanProduct, item["id"])
        values = _catalog_values(item, demo_only=demo_only)
        for key in (
            "purposes",
            "scenarios",
            "application_thresholds",
            "localization",
            "public_guidance",
            "required_documents",
            "source_refs",
            "review_notes",
        ):
            values.pop(key, None)
        if product is None:
            db.add(LoanProduct(**values))
        else:
            for key, value in values.items():
                setattr(product, key, value)
    db.commit()


def seed_demo_products(db: Session) -> None:
    _seed_products(db, DEMO_PRODUCTS, demo_only=True)


def load_official_catalog(path: Path = OFFICIAL_CATALOG_PATH) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("catalog_status") != "source_verified_pending_human_review":
        raise ValueError("official catalog status is missing or unsupported")
    products = catalog.get("products")
    if not isinstance(products, list) or not products:
        raise ValueError("official catalog contains no products")
    return catalog


def seed_catalog_products(
    db: Session,
    *,
    mode: str | None = None,
    path: Path = OFFICIAL_CATALOG_PATH,
) -> str:
    resolved_mode = mode or os.environ.get("CROSSBRIDGE_CATALOG_MODE", "auto")
    if resolved_mode not in {"auto", "demo", "official"}:
        raise ValueError(f"unsupported catalog mode: {resolved_mode}")

    use_official = resolved_mode == "official" or (resolved_mode == "auto" and path.exists())
    if not use_official:
        _seed_products(db, DEMO_PRODUCTS, demo_only=True)
        db.query(LoanProduct).filter(LoanProduct.demo_only.is_(False)).update(
            {"active": False}
        )
        db.commit()
        return "demo"

    catalog = load_official_catalog(path)
    _seed_products(db, catalog["products"], demo_only=False)
    db.query(LoanProduct).filter(LoanProduct.demo_only.is_(True)).update({"active": False})
    db.commit()
    return "official"


def list_active_products(db: Session) -> list[LoanProduct]:
    return list(db.scalars(select(LoanProduct).where(LoanProduct.active.is_(True))))

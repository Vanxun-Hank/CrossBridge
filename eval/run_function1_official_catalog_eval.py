#!/usr/bin/env python3
"""Function 1 phase-2 eval for the crawled BOCHK public-source catalog."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from server.business.app import create_app
from server.business.catalog import OFFICIAL_CATALOG_PATH, load_official_catalog
from server.business.db import run_migrations

REPORTS_DIR = ROOT / "eval" / "reports"


class Eval:
    def __init__(self) -> None:
        self.cases: list[dict] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.cases.append({"name": name, "passed": bool(condition), "detail": detail})

    @property
    def passed(self) -> int:
        return sum(case["passed"] for case in self.cases)

    @property
    def total(self) -> int:
        return len(self.cases)


def post_match(client: TestClient, prefill: dict) -> dict:
    session = client.post(
        "/crossbridge/v1/loan-matching/sessions", json={"prefill": prefill}
    ).json()
    return client.post(
        f"/crossbridge/v1/loan-matching/sessions/{session['id']}/match"
    ).json()


def run_eval() -> Eval:
    result = Eval()
    catalog = load_official_catalog(OFFICIAL_CATALOG_PATH)
    products = catalog["products"]
    result.check("official snapshot exists", OFFICIAL_CATALOG_PATH.exists())
    result.check("crawler emitted exactly eight official source snapshots", len(catalog["sources"]) == 8)
    result.check("official catalog emits 26 product candidates", len(products) == 26)
    result.check(
        "all source URLs are BOCHK or HKMC official-domain URLs",
        all(
            urlparse(source["url"]).hostname
            in {"bochk.com", "www.bochk.com", "hkmc.com.hk", "www.hkmc.com.hk"}
            for source in catalog["sources"]
        ),
    )
    result.check(
        "all products retain source URL, hash and checked timestamp",
        all(
            product["source_url"]
            and product["source_content_hash"]
            and product["source_checked_at"]
            for product in products
        ),
    )
    result.check(
        "official products are not marked DEMO ONLY",
        all(product["demo_only"] is False for product in products),
    )
    result.check(
        "official products remain pending human review",
        all(product["review_status"] == "source_verified_pending_human_review" for product in products),
    )
    result.check(
        "all official products include complete English card localization",
        all(
            {
                "product_name",
                "product_description",
                "loan_limit_text",
                "interest_rate_text",
                "tenor_text",
                "repayment_method_text",
                "fee_text",
                "public_guidance",
                "required_documents",
                "application_thresholds",
            }.issubset(product["localization"]["en"])
            for product in products
        ),
    )
    result.check(
        "English official-product cards contain no Chinese fallback text",
        all(
            re.search(r"[\u4e00-\u9fff]", json.dumps(product["localization"]["en"], ensure_ascii=False))
            is None
            for product in products
        ),
    )
    result.check(
        "unpublished loan limits remain unknown rather than fabricated",
        any(
            product["max_requested_amount_hkd"] is None
            and product["loan_limit_text"] is None
            for product in products
        ),
    )
    unsecured = next(
        product for product in products if product["id"] == "bochk_small_business_loan_unsecured"
    )
    result.check(
        "unsecured-loan public terms are extracted from source",
        unsecured["max_requested_amount_hkd"] == 2_000_000
        and unsecured["tenor_text"] == "最长 60 个月"
        and unsecured["application_thresholds"][0] == "适用于经营 2 年或以上的企业",
    )
    result.check(
        "unsecured-loan promotional pricing retains its explicit end date",
        "2026-03-31" in unsecured["interest_rate_text"]
        and "以 BOCHK 最新公告为准" in unsecured["interest_rate_text"],
    )
    export_discounting = next(
        product for product in products if product["id"] == "bochk_export_invoice_discounting"
    )
    result.check(
        "export-invoice discounting details come from the BOCHK export-services page",
        export_discounting["source_url"]
        == "https://www.bochk.com/en/corporate/tradefinance/export.html"
        and export_discounting["tenor_text"] == "短期贷款；公开页面未列明具体天数"
        and export_discounting["required_documents"] == ["发票", "货物交付证明"],
    )
    result.check(
        "export-invoice discounting public handling fee comes from the BOCHK tariff PDF",
        export_discounting["fee_text"] == "手续费：融资金额的 1/4%，最低 HK$500"
        and any(
            ref["source_url"]
            == "https://www.bochk.com/dam/corporatebanking/tfs_tariffs_en.pdf"
            for ref in export_discounting["source_refs"]
        ),
    )
    trust_receipt = next(
        product for product in products if product["id"] == "bochk_trust_receipt_facilities"
    )
    result.check(
        "trust-receipt public repayment note is extracted",
        trust_receipt["repayment_method_text"] == "可于信托收据到期日还款",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "official-catalog.db"
        database_url = f"sqlite:///{db_path}"
        run_migrations(database_url)
        app = create_app(database_url=database_url, catalog_mode="official")
        with TestClient(app) as client:
            catalog_api = client.get("/crossbridge/v1/loan-matching/catalog").json()
            result.check("API loads official mode", catalog_api["catalog_mode"] == "official")
            result.check("API activates 26 official products", catalog_api["product_count"] == 26)
            result.check(
                "API deactivates mock products",
                all(product["demo_only"] is False for product in catalog_api["products"]),
            )
            procurement = post_match(
                client,
                {
                    "business_scenario": "overseas_procurement",
                    "annual_turnover_hkd": 8_000_000,
                    "financing_purpose": "procurement_payment",
                    "requested_amount_hkd": 1_200_000,
                    "target_market": "越南",
                },
            )
            procurement_ids = [
                item["product"]["product_id"] for item in procurement["match_results"]
            ]
            result.check(
                "Vietnam supplier example returns core official import candidates",
                {
                    "bochk_import_invoice_financing",
                    "bochk_import_loan",
                    "bochk_supply_chain_finance_solution",
                    "bochk_trust_receipt_facilities",
                }.issubset(procurement_ids),
                json.dumps(procurement_ids, ensure_ascii=False),
            )
            result.check(
                "official cards expose source links and pending-review status",
                all(
                    item["product"]["source_url"].startswith("https://www.bochk.com/")
                    and item["product"]["review_status"]
                    == "source_verified_pending_human_review"
                    for item in procurement["match_results"]
                ),
            )
            result.check(
                "official cards mark unpublished terms for RM confirmation",
                all(
                    "loan_limit" in item["product"]["needs_rm_confirmation"]
                    and "interest_rate" in item["product"]["needs_rm_confirmation"]
                    for item in procurement["match_results"]
                ),
            )
            result.check(
                "official cards do not carry DEMO ONLY disclaimer",
                all(
                    not item["product"]["demo_only"]
                    and "DEMO ONLY" not in item["product"]["disclaimer"]
                    for item in procurement["match_results"]
                ),
            )
        conn = sqlite3.connect(db_path)
        active_demo_count = conn.execute(
            "SELECT COUNT(*) FROM loan_products WHERE active = 1 AND demo_only = 1"
        ).fetchone()[0]
        conn.close()
        result.check("database has no active mock product in official mode", active_demo_count == 0)
    return result


def write_report(result: Eval) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "passed": result.passed,
        "total": result.total,
        "cases": result.cases,
    }
    json_path = REPORTS_DIR / f"function1_official_catalog_eval_{timestamp}.json"
    md_path = REPORTS_DIR / f"function1_official_catalog_eval_{timestamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Function 1 Official Catalog Eval Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Result: **{result.passed}/{result.total} passed**",
        "",
    ]
    for case in result.cases:
        status = "PASS" if case["passed"] else "FAIL"
        detail = f" - {case['detail']}" if case["detail"] else ""
        lines.append(f"- `{status}` {case['name']}{detail}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result.passed, "total": result.total, "report": str(md_path)}))
    return md_path


if __name__ == "__main__":
    outcome = run_eval()
    write_report(outcome)
    raise SystemExit(0 if outcome.passed == outcome.total else 1)

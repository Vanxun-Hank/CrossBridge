#!/usr/bin/env python3
"""Function 7 eval - Personal SME Financing Dashboard.

Runs hermetically with a temp SQLite DB and stubbed F1/F2/F3 upstreams. Function 7
owns only dashboard-native data, so the upstream stubs let this verify aggregation,
bookmarks, export contracts, and degraded upstream behavior without live ports.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from server.dashboard.app import DISCLAIMER, create_app
from server.dashboard.db import run_migrations

REPORTS_DIR = ROOT / "eval" / "reports"
API = "/crossbridge-dashboard/v1"


class Checks:
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


class StubUpstreams:
    def __init__(self) -> None:
        self.fail_documents = False

    def health(self) -> dict:
        return {
            "business": {"ok": True},
            "documents": {"ok": not self.fail_documents},
            "timeline": {"ok": True},
        }

    def list_saved_drafts(self, sme_id: str) -> list[dict]:
        return [
            {
                "id": "DRAFT-1",
                "sme_id": sme_id,
                "name": "Export trade working capital",
                "draft_profile": {
                    "business_scenario": "export_trade",
                    "financing_purpose": "order_fulfillment",
                    "requested_amount_hkd": 1200000,
                    "annual_turnover_hkd": 9000000,
                },
                "selected_products": [
                    {
                        "product_id": "bochk_export_invoice",
                        "product_name": "出口发票贴现",
                        "product_name_en": "Export Invoice Discounting",
                    }
                ],
                "matched_count": 2,
                "updated_at": "2026-06-08T10:00:00+00:00",
            }
        ]

    def list_document_packages(self, sme_id: str) -> list[dict]:
        if self.fail_documents:
            raise RuntimeError("documents service unavailable")
        return [
            {
                "id": "PKG-1",
                "sme_id": sme_id,
                "scenario_code": "export_fulfillment",
                "scenario_label_en": "Export order fulfilment",
                "selected_product_id": "bochk_export_invoice",
                "saved_draft_id": "DRAFT-1",
                "checklist_done": 3,
                "checklist_total": 4,
                "official_forms": [{"form_id": "F-1", "has_draft": True}],
                "submission_readiness": {
                    "ready": True,
                    "blocking": [],
                    "warnings": [{"code": "trade_terms"}],
                },
                "updated_at": "2026-06-08T11:00:00+00:00",
            }
        ]

    def list_applications(self, sme_id: str) -> list[dict]:
        return [
            {
                "id": "APP-1",
                "sme_id": sme_id,
                "origin_package_id": "PKG-1",
                "product_id": "bochk_export_invoice",
                "product_label_en": "Export Invoice Discounting",
                "current_node_code": "credit_assessment",
                "current_node_label_en": "Credit assessment",
                "status": "in_progress",
                "updated_at": "2026-06-08T12:00:00+00:00",
            }
        ]


def run_checks() -> Checks:
    result = Checks()

    with tempfile.TemporaryDirectory() as temp_dir:
        database_url = f"sqlite:///{Path(temp_dir) / 'f7.db'}"
        run_migrations(database_url)
        run_migrations(database_url)
        result.check("migrations run repeatably", True)

        upstream = StubUpstreams()
        app = create_app(database_url=database_url, migrate_on_startup=False, upstream_client=upstream)
        with TestClient(app) as client:
            health = client.get("/healthz")
            result.check(
                "GET /healthz ok",
                health.status_code == 200 and health.json().get("service") == "crossbridge-dashboard",
                json.dumps(health.json()),
            )

            empty = client.get(f"{API}/policy-bookmarks")
            result.check(
                "policy bookmark list starts empty",
                empty.status_code == 200 and empty.json()["policy_bookmarks"] == [],
            )

            created = client.post(
                f"{API}/policy-bookmarks",
                json={
                    "sme_id": "demo_sme_001",
                    "title": "HKMA SME Financing Guarantee Scheme",
                    "source_url": "https://www.hkma.gov.hk/example",
                    "source_title": "HKMA",
                    "snippet": "Guarantee coverage reference",
                    "document_type": "regulator_guidance",
                    "trust_tier": "official",
                    "origin_chat_id": "chat-1",
                },
            )
            bj = created.json()
            result.check(
                "POST /policy-bookmarks creates bookmark",
                created.status_code == 200 and bj["title"].startswith("HKMA"),
                json.dumps(bj),
            )

            overview = client.get(f"{API}/overview")
            oj = overview.json()
            result.check(
                "overview aggregates F1/F2/F3/F7 data",
                overview.status_code == 200
                and oj["summary"]["saved_draft_count"] == 1
                and oj["summary"]["document_package_count"] == 1
                and oj["summary"]["application_count"] == 1
                and oj["summary"]["policy_bookmark_count"] == 1
                and oj["summary"]["submission_ready_package_count"] == 1,
                json.dumps(oj["summary"]),
            )
            result.check("overview includes fixed disclaimer", oj["disclaimer"] == DISCLAIMER)

            report = client.post(f"{API}/reports/markdown", json={"sme_id": "demo_sme_001"})
            text = report.json()["content"]
            result.check(
                "markdown report includes key sections and disclaimer",
                report.status_code == 200
                and "# CrossBridge Personal SME Financing Dashboard" in text
                and "Core Function Disclaimer" in text
                and DISCLAIMER in text
                and "Export Invoice Discounting" in text
                and "HKMA SME Financing Guarantee Scheme" in text,
            )

            backup = client.get(f"{API}/backups/json")
            backup_json = backup.json()
            backup_str = json.dumps(backup_json, ensure_ascii=False, sort_keys=True)
            result.check(
                "JSON backup is valid and includes current export event",
                backup.status_code == 200
                and backup_json["backup_version"] == "function7.v1"
                and backup_json["current_export_event"]["export_type"] == "json_backup",
            )
            result.check("backup does not leak bank-private internal_note", "internal_note" not in backup_str)

            deleted = client.delete(f"{API}/policy-bookmarks/{bj['id']}")
            after_delete = client.get(f"{API}/policy-bookmarks")
            result.check(
                "DELETE /policy-bookmarks/{id} removes bookmark",
                deleted.status_code == 200 and after_delete.json()["policy_bookmarks"] == [],
            )

            upstream.fail_documents = True
            degraded = client.get(f"{API}/overview")
            dj = degraded.json()
            result.check(
                "overview degrades gracefully when one upstream fails",
                degraded.status_code == 200
                and dj["summary"]["saved_draft_count"] == 1
                and dj["summary"]["document_package_count"] == 0
                and any(i["service"] == "documents" for i in dj["access_issues"]),
                json.dumps(dj["access_issues"]),
            )

    return result


def write_reports(checks: Checks) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORTS_DIR / f"eval_function7_{stamp}.json"
    md_path = REPORTS_DIR / f"eval_function7_{stamp}.md"
    payload = {
        "suite": "function7",
        "passed": checks.passed,
        "total": checks.total,
        "cases": checks.cases,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Function 7 Eval",
        "",
        f"Passed: {checks.passed}/{checks.total}",
        "",
    ]
    for case in checks.cases:
        mark = "PASS" if case["passed"] else "FAIL"
        lines.append(f"- {mark}: {case['name']}")
        if case["detail"] and not case["passed"]:
            lines.append(f"  - {case['detail']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    checks = run_checks()
    json_path, md_path = write_reports(checks)
    print(f"Function 7 eval: {checks.passed}/{checks.total} passed")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return 0 if checks.passed == checks.total else 1


if __name__ == "__main__":
    raise SystemExit(main())

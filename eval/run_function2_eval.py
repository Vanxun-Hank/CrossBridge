#!/usr/bin/env python3
"""Function 2 eval - document-preparation workbench (port 8082 service).

Mirrors the Function 1 eval harness: temp SQLite + own migrations + TestClient,
flat case list, markdown/json report under eval/reports/, exit 0/1.

Function 2 is fully independent of Function 1 at runtime: its own DB, own Alembic
env, and an F2-owned readonly material snapshot. These tests must NOT touch the
Function 1 database or its eval baselines.
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

from server.document_preparation.app import create_app
from server.document_preparation import catalog as catalog_module
from server.document_preparation.catalog import build_catalog
from server.document_preparation.db import build_engine, build_session_factory, run_migrations
from server.document_preparation.models import DocumentAuditEvent

REPORTS_DIR = ROOT / "eval" / "reports"

API = "/crossbridge-documents/v1"


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


def _checked_codes(package: dict) -> list[str]:
    return [
        item["code"]
        for group in package["checklist"].values()
        for item in group["items"]
        if item["checked"]
    ]


def _checked_overlay_codes(package: dict) -> list[str]:
    overlay = package.get("product_overlay") or {}
    return [item["code"] for item in overlay.get("checklist_items", []) if item["checked"]]


def run_checks() -> Checks:
    result = Checks()

    catalog = build_catalog()
    catalog_source = Path(catalog_module.__file__).read_text(encoding="utf-8")
    result.check(
        "F2 runtime catalog loader does not read the F1 official-products JSON",
        "official_products" not in catalog_source,
    )
    result.check(
        "F2 catalog status is source_verified_pending_human_review",
        catalog.get("catalog_status") == "source_verified_pending_human_review",
    )
    scenario_codes = [s["code"] for s in catalog["scenarios"]]
    result.check(
        "catalog covers both import and export scenarios",
        scenario_codes == ["import_payment", "export_fulfillment"],
        json.dumps(scenario_codes),
    )
    template_codes = [t["code"] for t in catalog["templates"]]
    result.check(
        "catalog exposes the import, export and shared editable templates",
        set(template_codes)
        == {"supplier_payment_form", "export_fulfillment_form", "financing_cover_sheet"},
        json.dumps(template_codes, ensure_ascii=False),
    )
    overlays = catalog["product_overlays"]
    result.check("snapshot contains all 26 product overlays", len(overlays) == 26, str(len(overlays)))
    result.check(
        "snapshot has 14 import-compatible overlays",
        sum("import_payment" in overlay["scenarios"] for overlay in overlays.values()) == 14,
    )
    result.check(
        "snapshot has 20 export-compatible overlays",
        sum("export_fulfillment" in overlay["scenarios"] for overlay in overlays.values()) == 20,
    )

    with_docs = sorted(pid for pid, o in overlays.items() if o["has_published_documents"])
    result.check(
        "exactly the 12 products with published documents carry overlay materials",
        len(with_docs) == 12,
        str(len(with_docs)),
    )
    result.check(
        "import invoice financing overlay = supplier invoice (from official page)",
        overlays["bochk_import_invoice_financing"]["required_documents"] == ["供应商发票"],
        json.dumps(overlays["bochk_import_invoice_financing"]["required_documents"], ensure_ascii=False),
    )
    result.check(
        "export invoice discounting overlay = invoice + delivery proof",
        overlays["bochk_export_invoice_discounting"]["required_documents"] == ["发票", "货物交付证明"],
        json.dumps(overlays["bochk_export_invoice_discounting"]["required_documents"], ensure_ascii=False),
    )
    result.check(
        "supply-chain invoice-payment overlay = invoice + anchor-buyer undertaking",
        overlays["bochk_supply_chain_invoice_payment"]["required_documents"]
        == ["发票", "核心买方付款承诺"],
        json.dumps(
            overlays["bochk_supply_chain_invoice_payment"]["required_documents"],
            ensure_ascii=False,
        ),
    )
    result.check(
        "all 12 published-document overlays carry complete English translations",
        all(
            len(overlay["required_documents"]) == len(overlay["required_documents_en"])
            and all(overlay["required_documents_en"])
            for overlay in overlays.values()
            if overlay["has_published_documents"]
        ),
    )
    result.check(
        "exactly four overlays carry published fee text",
        sum(overlay["has_published_fee"] for overlay in overlays.values()) == 4,
    )
    result.check(
        "unpublished product materials are not fabricated (import loan stays empty)",
        overlays["bochk_import_loan"]["required_documents"] == []
        and overlays["bochk_import_loan"]["has_published_documents"] is False,
    )
    result.check(
        "products without published docs expose an RM-confirmation label",
        all(
            o["unknown_label_zh"] == "需客户经理确认"
            for o in overlays.values()
            if not o["has_published_documents"]
        ),
    )
    result.check(
        "exactly 14 products remain RM-confirmation only",
        sum(not overlay["has_published_documents"] for overlay in overlays.values()) == 14,
    )
    import_scenario = next(s for s in catalog["scenarios"] if s["code"] == "import_payment")
    export_scenario = next(s for s in catalog["scenarios"] if s["code"] == "export_fulfillment")
    result.check(
        "import base pack has the three checklist tiers",
        set(import_scenario["checklist"].keys())
        == {"public_source_hint", "suggested_preparation", "bank_to_confirm"},
    )

    def _all_items(scenario: dict) -> list[dict]:
        return [it for g in scenario["checklist"].values() for it in g["items"]]

    result.check(
        "import base-pack items are fully bilingual (zh+en present)",
        all(it.get("label_zh") and it.get("label_en") for it in _all_items(import_scenario)),
    )
    result.check(
        "export base-pack items are fully bilingual (zh+en present)",
        all(it.get("label_zh") and it.get("label_en") for it in _all_items(export_scenario)),
    )
    result.check(
        "all base-pack items carry evidence level and source metadata",
        all(
            it.get("evidence_level") and "source_url" in it and it.get("source_note_zh")
            and it.get("source_note_en")
            for scenario in catalog["scenarios"]
            for it in _all_items(scenario)
        ),
    )
    result.check(
        "templates carry bilingual labels",
        all(t.get("label_zh") and t.get("label_en") for t in catalog["templates"]),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "f2.db"
        database_url = f"sqlite:///{db_path}"
        run_migrations(database_url)
        app = create_app(database_url=database_url, migrate_on_startup=False)
        with TestClient(app) as client:
            cat_api = client.get(f"{API}/catalog")
            result.check("GET /catalog returns 200", cat_api.status_code == 200)
            result.check(
                "GET /catalog exposes import + export scenarios",
                [s["code"] for s in cat_api.json()["scenarios"]]
                == ["import_payment", "export_fulfillment"],
            )
            invalid_unknown = client.post(
                f"{API}/packages",
                json={
                    "sme_id": "demo_invalid_001",
                    "scenario_code": "import_payment",
                    "selected_product_id": "unknown_product",
                },
            )
            result.check("POST /packages rejects unknown product", invalid_unknown.status_code == 400)
            invalid_scenario = client.post(
                f"{API}/packages",
                json={
                    "sme_id": "demo_invalid_002",
                    "scenario_code": "import_payment",
                    "selected_product_id": "bochk_export_invoice_discounting",
                },
            )
            result.check(
                "POST /packages rejects scenario-incompatible product",
                invalid_scenario.status_code == 400,
            )

            create = client.post(
                f"{API}/packages",
                json={
                    "sme_id": "demo_sme_001",
                    "scenario_code": "import_payment",
                    "selected_product_id": "bochk_import_invoice_financing",
                    "origin_matching_session_id": "sess-eval-1",
                },
            )
            result.check("POST /packages creates a package", create.status_code == 200)
            pkg = create.json()
            pid = pkg["id"]
            result.check("new package is not flagged resumed", pkg.get("resumed") is False)
            result.check(
                "F1 product code is preselected on the package",
                pkg["selected_product_id"] == "bochk_import_invoice_financing",
            )
            result.check(
                "package overlay reflects the preselected product official documents",
                pkg["product_overlay"]["required_documents"] == ["供应商发票"],
            )
            result.check(
                "package exposes the three checklist tiers",
                set(pkg["checklist"].keys())
                == {"public_source_hint", "suggested_preparation", "bank_to_confirm"},
            )
            result.check(
                "import package exposes supplier form plus shared financing cover",
                {template["code"] for template in pkg["templates"]}
                == {"supplier_payment_form", "financing_cover_sheet"},
            )

            chk = client.patch(
                f"{API}/packages/{pid}/checklist",
                json={"item_code": "imp_prep_invoice", "checked": True},
            )
            result.check("PATCH /checklist returns 200", chk.status_code == 200)
            invalid_chk = client.patch(
                f"{API}/packages/{pid}/checklist",
                json={"item_code": "made_up_item", "checked": True},
            )
            result.check("PATCH /checklist rejects arbitrary item_code", invalid_chk.status_code == 400)
            overlay_code = pkg["product_overlay"]["checklist_items"][0]["code"]
            overlay_chk = client.patch(
                f"{API}/packages/{pid}/checklist",
                json={"item_code": overlay_code, "checked": True},
            )
            result.check("published product overlay item can be checked", overlay_chk.status_code == 200)
            result.check(
                "published product overlay check is serialized",
                _checked_overlay_codes(overlay_chk.json()) == [overlay_code],
                json.dumps(_checked_overlay_codes(overlay_chk.json())),
            )

            tpl = client.patch(
                f"{API}/packages/{pid}/templates/supplier_payment_form",
                json={"content": {"supplier_name": "ABC Co", "swift_bic": "BKCHHKHH"}},
            )
            result.check("PATCH /templates returns 200", tpl.status_code == 200)
            cover_tpl = client.patch(
                f"{API}/packages/{pid}/templates/financing_cover_sheet",
                json={"content": {"financing_purpose": "Import working capital"}},
            )
            result.check("shared financing-cover template saves", cover_tpl.status_code == 200)
            wrong_tpl = client.patch(
                f"{API}/packages/{pid}/templates/export_fulfillment_form",
                json={"content": {"buyer_name": "Wrong scenario"}},
            )
            result.check("scenario-incompatible template is rejected", wrong_tpl.status_code == 400)

            resume = client.post(
                f"{API}/packages",
                json={"sme_id": "demo_sme_001", "scenario_code": "import_payment"},
            )
            result.check("resume returns same package id", resume.json()["id"] == pid)
            result.check("resume is flagged resumed", resume.json().get("resumed") is True)

            fetched = client.get(f"{API}/packages/{pid}").json()
            result.check(
                "checklist progress persists across resume",
                _checked_codes(fetched) == ["imp_prep_invoice"],
                json.dumps(_checked_codes(fetched)),
            )
            result.check(
                "overlay progress persists across resume",
                _checked_overlay_codes(fetched) == [overlay_code],
                json.dumps(_checked_overlay_codes(fetched)),
            )
            saved_tpl = next(
                t for t in fetched["templates"] if t["code"] == "supplier_payment_form"
            )
            result.check(
                "template draft persists across resume",
                saved_tpl["content"].get("swift_bic") == "BKCHHKHH",
                json.dumps(saved_tpl["content"], ensure_ascii=False),
            )

            switched = client.patch(
                f"{API}/packages/{pid}/product",
                json={"selected_product_id": "bochk_import_loan"},
            ).json()
            result.check(
                "switching product preserves base checklist progress",
                _checked_codes(switched) == ["imp_prep_invoice"],
                json.dumps(_checked_codes(switched)),
            )
            result.check(
                "switched-to product without published docs is not fabricated",
                switched["product_overlay"]["required_documents"] == []
                and switched["product_overlay"]["has_published_documents"] is False,
            )
            switched_back = client.patch(
                f"{API}/packages/{pid}/product",
                json={"selected_product_id": "bochk_import_invoice_financing"},
            ).json()
            result.check(
                "switching back restores hidden overlay progress",
                _checked_overlay_codes(switched_back) == [overlay_code],
                json.dumps(_checked_overlay_codes(switched_back)),
            )
            incompatible_switch = client.patch(
                f"{API}/packages/{pid}/product",
                json={"selected_product_id": "bochk_export_invoice_discounting"},
            )
            result.check(
                "PATCH /product rejects scenario-incompatible product",
                incompatible_switch.status_code == 400,
            )

            after_reset = client.post(f"{API}/packages/{pid}/reset").json()
            result.check("reset clears checklist", _checked_codes(after_reset) == [])
            reset_tpl = next(
                t for t in after_reset["templates"] if t["code"] == "supplier_payment_form"
            )
            result.check("reset clears template drafts", reset_tpl["content"] == {})
            result.check("reset clears overlay progress", _checked_overlay_codes(after_reset) == [])

            printed = client.post(f"{API}/packages/{pid}/printed")
            result.check("POST /printed returns 200", printed.status_code == 200)

            exp = client.post(
                f"{API}/packages",
                json={
                    "sme_id": "demo_sme_002",
                    "scenario_code": "export_fulfillment",
                    "selected_product_id": "bochk_export_invoice_discounting",
                },
            )
            result.check(
                "export-scenario package loads export base pack",
                exp.status_code == 200
                and exp.json()["scenario_code"] == "export_fulfillment",
            )
            result.check(
                "export package exposes export form plus shared financing cover",
                {template["code"] for template in exp.json()["templates"]}
                == {"export_fulfillment_form", "financing_cover_sheet"},
            )

            unknown = client.post(
                f"{API}/packages",
                json={"sme_id": "demo_sme_003", "scenario_code": "import_payment"},
            )
            result.check("unrelated SME gets its own package", unknown.json()["id"] != pid)

        engine = build_engine(database_url)
        session = build_session_factory(engine)()
        try:
            audit_count = session.query(DocumentAuditEvent).count()
            audit_event_types = {
                event.event_type for event in session.query(DocumentAuditEvent).all()
            }
        finally:
            session.close()
        result.check("document audit events are recorded", audit_count >= 6, str(audit_count))
        result.check(
            "reset and printed audit records are present",
            {"document_package_reset", "document_package_printed"} <= audit_event_types,
            json.dumps(sorted(audit_event_types)),
        )

    return result


def write_report(result: Checks) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "passed": result.passed,
        "total": result.total,
        "cases": result.cases,
    }
    json_path = REPORTS_DIR / f"function2_eval_{timestamp}.json"
    md_path = REPORTS_DIR / f"function2_eval_{timestamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Function 2 Document Preparation Eval Report",
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
    outcome = run_checks()
    write_report(outcome)
    raise SystemExit(0 if outcome.passed == outcome.total else 1)

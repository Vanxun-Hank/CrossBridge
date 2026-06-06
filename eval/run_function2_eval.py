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
from server.document_preparation import official_forms as official_forms_module
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
        # Keep this API test hermetic even when a developer has populated the real
        # gitignored cache for browser testing. The ready-cache path is exercised by
        # scripts/check_official_forms_pdfjs.mjs against the genuine local PDFs.
        original_form_cache_dir = official_forms_module.FORM_CACHE_DIR
        official_forms_module.FORM_CACHE_DIR = Path(temp_dir) / "missing-official-forms"
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
            official_ids = [f["form_id"] for f in pkg["official_forms"]]
            result.check(
                "import package exposes the official import-scenario forms",
                set(official_ids)
                == {
                    "tt_remittance",
                    "import_invoice_financing",
                    "import_loan_drawdown",
                    "irrevocable_documentary_credit",
                },
                json.dumps(official_ids),
            )
            result.check(
                "the product-exact official form is ranked first",
                official_ids[0] == "import_invoice_financing"
                and pkg["official_forms"][0]["product_match"] is True,
                json.dumps(official_ids),
            )
            result.check(
                "official forms report a missing local cache in the hermetic eval env",
                all(f["cache_status"] == "missing" for f in pkg["official_forms"]),
            )
            result.check(
                "trade-finance forms are terms-gated; TT remittance is not",
                next(
                    f for f in pkg["official_forms"] if f["form_id"] == "import_invoice_financing"
                )["trade_terms_required"] is True
                and next(
                    f for f in pkg["official_forms"] if f["form_id"] == "tt_remittance"
                )["trade_terms_required"] is False,
            )
            result.check(
                "package no longer exposes self-made templates",
                "templates" not in pkg,
            )
            result.check(
                "package surfaces unaccepted trade-terms status with a stable sha",
                pkg["trade_terms"]["accepted"] is False and bool(pkg["trade_terms"]["sha256"]),
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

            gone = client.patch(
                f"{API}/packages/{pid}/templates/supplier_payment_form",
                json={"content": {"supplier_name": "ABC Co"}},
            )
            result.check("retired custom-template endpoint returns 410 Gone", gone.status_code == 410)

            # Trade-finance forms are gated behind explicit terms acceptance.
            gated = client.get(f"{API}/packages/{pid}/forms/import_invoice_financing/pdf")
            result.check("trade-finance PDF is 403 before terms acceptance", gated.status_code == 403)
            accepted = client.post(f"{API}/packages/{pid}/trade-terms/accept")
            result.check("POST /trade-terms/accept returns 200", accepted.status_code == 200)
            result.check(
                "package reflects accepted trade terms",
                accepted.json()["trade_terms"]["accepted"] is True,
            )
            after_accept = client.get(f"{API}/packages/{pid}/forms/import_invoice_financing/pdf")
            result.check(
                "after acceptance the terms gate opens (cache still missing -> 409)",
                after_accept.status_code == 409,
            )
            tt_pdf = client.get(f"{API}/packages/{pid}/forms/tt_remittance/pdf")
            result.check(
                "non-gated TT form skips 403 and reports missing cache (409)",
                tt_pdf.status_code == 409,
            )
            unknown_form = client.get(f"{API}/packages/{pid}/forms/not_a_form/pdf")
            result.check("unknown form_id is rejected (404)", unknown_form.status_code == 404)

            draft = client.patch(
                f"{API}/packages/{pid}/forms/import_invoice_financing/draft",
                json={"values": {"Name of Applicant": "ABC Co", "__not_in_form__": "x"}},
            )
            result.check("PATCH /forms/.../draft returns 200", draft.status_code == 200)
            saved_draft = client.get(
                f"{API}/packages/{pid}/forms/import_invoice_financing/draft"
            ).json()
            result.check(
                "official-form draft persists only registry-whitelisted fields",
                saved_draft["values"] == {"Name of Applicant": "ABC Co"},
                json.dumps(saved_draft["values"], ensure_ascii=False),
            )

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
            resumed_draft = client.get(
                f"{API}/packages/{pid}/forms/import_invoice_financing/draft"
            ).json()
            result.check(
                "official-form draft persists across resume",
                resumed_draft["values"] == {"Name of Applicant": "ABC Co"},
                json.dumps(resumed_draft["values"], ensure_ascii=False),
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
            reset_draft = client.get(
                f"{API}/packages/{pid}/forms/import_invoice_financing/draft"
            ).json()
            result.check("reset clears official-form drafts", reset_draft["values"] == {})
            result.check(
                "reset keeps trade-terms acceptance (keyed by SME, not package)",
                after_reset["trade_terms"]["accepted"] is True,
            )
            result.check("reset clears overlay progress", _checked_overlay_codes(after_reset) == [])

            printed = client.post(f"{API}/packages/{pid}/printed")
            result.check("POST /printed returns 200", printed.status_code == 200)
            exported_form = client.post(
                f"{API}/packages/{pid}/forms/import_invoice_financing/exported"
            )
            result.check("POST /forms/.../exported returns 200", exported_form.status_code == 200)
            printed_form = client.post(
                f"{API}/packages/{pid}/forms/import_invoice_financing/printed"
            )
            result.check("POST /forms/.../printed returns 200", printed_form.status_code == 200)

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
            exp_forms = [f["form_id"] for f in exp.json()["official_forms"]]
            result.check(
                "export package exposes the official export-scenario forms",
                set(exp_forms)
                == {
                    "export_invoice_discounting",
                    "processing_export_documents",
                    "packing_loan",
                },
                json.dumps(exp_forms),
            )
            result.check(
                "the product-exact export form is ranked first",
                exp_forms[0] == "export_invoice_discounting",
                json.dumps(exp_forms),
            )

            # ---- submission-readiness (Function 3 submit gate; F2 is the source of truth) ----
            rp = client.post(
                f"{API}/packages",
                json={"sme_id": "demo_ready_001", "scenario_code": "import_payment"},
            ).json()
            rpid = rp["id"]
            tt_bind = next(
                f["validation_bindings"]
                for f in rp["official_forms"]
                if f["form_id"] == "tt_remittance"
            )

            def _readiness(pkg_id: str = rpid) -> dict:
                return client.get(f"{API}/packages/{pkg_id}/submission-readiness").json()

            empty = _readiness()
            empty_codes = {b["code"] for b in empty["blocking"]}
            result.check(
                "readiness: empty package is not ready (core_fields + charge_bearer block)",
                empty["ready"] is False
                and "core_fields" in empty_codes
                and "charge_bearer" in empty_codes,
                json.dumps(empty["blocking"]),
            )

            good_values = {
                tt_bind["swift_bic"]: "HSBCHKHH",
                tt_bind["beneficiary_account_name"]: "ACME LTD",
                tt_bind["payment_amount"]: "1000",
                tt_bind["payment_currency"]: "USD",
                tt_bind["charge_bearer"]: "OUR",
            }
            client.patch(
                f"{API}/packages/{rpid}/forms/tt_remittance/draft",
                json={"values": good_values},
            )
            ready = _readiness()
            result.check(
                "readiness: complete consistent form is ready to submit",
                ready["ready"] is True and ready["blocking"] == [],
                json.dumps(ready),
            )
            result.check(
                "readiness: unaccepted trade terms surface as a non-blocking warning",
                any(w["code"] == "trade_terms" for w in ready["warnings"]),
                json.dumps(ready["warnings"]),
            )

            client.patch(
                f"{API}/packages/{rpid}/forms/tt_remittance/draft",
                json={"values": dict(good_values, **{tt_bind["swift_bic"]: "BAD"})},
            )
            r_bic = _readiness()
            result.check(
                "readiness: malformed SWIFT/BIC blocks submission",
                r_bic["ready"] is False
                and any(b["code"] == "swift_bic" for b in r_bic["blocking"]),
                json.dumps(r_bic["blocking"]),
            )

            client.patch(
                f"{API}/packages/{rpid}/forms/tt_remittance/draft",
                json={
                    "values": dict(
                        good_values, **{tt_bind["charge_bearer"]: "PENDING_CONFIRMATION"}
                    )
                },
            )
            r_cb = _readiness()
            result.check(
                "readiness: pending charge bearer blocks submission",
                r_cb["ready"] is False
                and any(b["code"] == "charge_bearer" for b in r_cb["blocking"]),
                json.dumps(r_cb["blocking"]),
            )

            # published product materials: an overlay with unchecked required items blocks.
            overlays = client.get(f"{API}/catalog").json()["product_overlays"]
            import_overlay = next(
                ov
                for ov in overlays.values()
                if "import_payment" in ov.get("scenarios", []) and ov.get("checklist_items")
            )
            pub = client.post(
                f"{API}/packages",
                json={
                    "sme_id": "demo_ready_002",
                    "scenario_code": "import_payment",
                    "selected_product_id": import_overlay["product_id"],
                },
            ).json()
            pub_id = pub["id"]
            pub_before = {b["code"] for b in _readiness(pub_id)["blocking"]}
            result.check(
                "readiness: unchecked published product materials block submission",
                "published_documents" in pub_before,
                json.dumps(sorted(pub_before)),
            )
            for item in pub["product_overlay"]["checklist_items"]:
                client.patch(
                    f"{API}/packages/{pub_id}/checklist",
                    json={"item_code": item["code"], "checked": True},
                )
            pub_after = {b["code"] for b in _readiness(pub_id)["blocking"]}
            result.check(
                "readiness: checking all published materials clears that block",
                "published_documents" not in pub_after,
                json.dumps(sorted(pub_after)),
            )

            unknown = client.post(
                f"{API}/packages",
                json={"sme_id": "demo_sme_003", "scenario_code": "import_payment"},
            )
            result.check("unrelated SME gets its own package", unknown.json()["id"] != pid)
        official_forms_module.FORM_CACHE_DIR = original_form_cache_dir

        engine = build_engine(database_url)
        session = build_session_factory(engine)()
        try:
            audit_count = session.query(DocumentAuditEvent).count()
            audit_event_types = {
                event.event_type for event in session.query(DocumentAuditEvent).all()
            }
        finally:
            session.close()
        result.check("document audit events are recorded", audit_count >= 8, str(audit_count))
        result.check(
            "reset, printed, terms-acceptance and official-form audit records are present",
            {
                "document_package_reset",
                "document_package_printed",
                "document_trade_terms_accepted",
                "document_official_form_draft_saved",
                "document_official_form_exported",
                "document_official_form_printed",
            }
            <= audit_event_types,
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

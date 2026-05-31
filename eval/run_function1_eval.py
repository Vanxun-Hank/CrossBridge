#!/usr/bin/env python3
"""Function 1 eval: trigger, clarification, matching, memory, and migrations."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select

from server.business.app import create_app
from server.business.catalog import DEMO_PRODUCTS
from server.business.db import run_migrations
from server.business.matching import ClarifierResult, parse_clarifier_payload
from server.business.models import AuditEvent, MatchingSession, SmeProfile

REPORTS_DIR = ROOT / "eval" / "reports"


TRIGGER_CASES = [
    ("帮我找适合海外采购的贷款", "action"),
    ("我们年营业额 800 万，要付越南供应商 120 万，适合什么贷款？", "action"),
    ("我想申请跨境采购融资", "action"),
    ("推荐一个跨境电商备货融资方案", "action"),
    ("出口订单需要贷款，有什么产品？", "action"),
    ("需要融资支付供应商", "action"),
    ("想要贷款做海外采购", "action"),
    ("帮我匹配融资产品", "action"),
    ("有没有适合我公司的贷款方案", "action"),
    ("申请贷款用于日常周转", "action"),
    ("I want loan options for supplier payment", "action"),
    ("Recommend a financing product for inventory", "action"),
    ("I need a loan for export order fulfillment", "action"),
    ("Help me find financing for procurement", "action"),
    ("Which loan product is suitable for my SME?", "action"),
    ("SFGS 是什么？", "informational"),
    ("申请 SFGS 要什么文件？", "informational"),
    ("跨境付款有什么合规风险？", "informational"),
    ("贷款利率怎么算？", "informational"),
    ("解释一下贸易融资", "informational"),
    ("海外采购需要哪些材料？", "informational"),
    ("出口退税政策是什么？", "informational"),
    ("香港外汇政策有什么要求？", "informational"),
    ("供应商付款的流程是什么？", "informational"),
    ("What is trade finance?", "informational"),
    ("Explain SFGS requirements", "informational"),
    ("Which documents are required for export trade?", "informational"),
    ("What are the compliance risks for Vietnam payment?", "informational"),
    ("Explain the loan interest policy", "informational"),
    ("What is a working capital loan?", "informational"),
    ("融资", "ambiguous"),
    ("贷款", "ambiguous"),
    ("越南供应商", "ambiguous"),
    ("cross-border finance", "ambiguous"),
    ("我想了解一下", "ambiguous"),
]


class FakeValidClarifier:
    def clarify(self, profile, message: str, target_field: str | None = None) -> ClarifierResult:
        return ClarifierResult(
            parse_clarifier_payload(
                {
                    "extracted_updates": {
                        "business_scenario": "cross_border_ecommerce",
                        "annual_turnover_hkd": 20_000_000,
                        "financing_purpose": "stocking",
                        "requested_amount_hkd": 1_000_000,
                        "target_market": "东南亚",
                    },
                    "ready_to_match": True,
                    "missing_slot": None,
                    "question_to_user": None,
                }
            ),
            "llm",
        )


class FakeUnavailableClarifier:
    def clarify(self, profile, message: str, target_field: str | None = None) -> ClarifierResult:
        return ClarifierResult(None, "manual_fallback", "simulated LLM outage")


class Eval:
    def __init__(self) -> None:
        self.sections: dict[str, list[dict[str, Any]]] = {}

    def check(self, section: str, name: str, condition: bool, detail: str = "") -> None:
        self.sections.setdefault(section, []).append(
            {"name": name, "passed": bool(condition), "detail": detail}
        )

    @property
    def passed(self) -> int:
        return sum(case["passed"] for cases in self.sections.values() for case in cases)

    @property
    def total(self) -> int:
        return sum(len(cases) for cases in self.sections.values())

    def summary(self) -> dict[str, Any]:
        return {
            section: {
                "passed": sum(case["passed"] for case in cases),
                "total": len(cases),
            }
            for section, cases in self.sections.items()
        }


def count_rows(session_factory, model) -> int:
    with session_factory() as db:
        return db.scalar(select(func.count()).select_from(model)) or 0


def run_trigger_eval(client: TestClient, app, result: Eval) -> None:
    before_sessions = count_rows(app.state.SessionLocal, MatchingSession)
    before_profiles = count_rows(app.state.SessionLocal, SmeProfile)
    action_total = action_hit = info_total = info_false_trigger = 0
    for query, label in TRIGGER_CASES:
        response = client.post(
            "/crossbridge/v1/loan-matching/route-intent", json={"message": query}
        )
        payload = response.json()
        if label == "action":
            action_total += 1
            action_hit += int(payload["show_cta"])
        elif label == "informational":
            info_total += 1
            info_false_trigger += int(payload["show_cta"])
    result.check(
        "trigger",
        "at least 30 labelled trigger queries",
        len(TRIGGER_CASES) >= 30,
        f"{len(TRIGGER_CASES)} cases",
    )
    result.check(
        "trigger",
        "obvious financing action CTA recall is 100%",
        action_hit == action_total,
        f"{action_hit}/{action_total}",
    )
    result.check(
        "trigger",
        "informational policy QA false-trigger rate is 0%",
        info_false_trigger == 0,
        f"{info_false_trigger}/{info_total}",
    )
    result.check(
        "trigger",
        "router does not create sessions or profiles",
        before_sessions == count_rows(app.state.SessionLocal, MatchingSession)
        and before_profiles == count_rows(app.state.SessionLocal, SmeProfile),
    )
    sample = client.post(
        "/crossbridge/v1/loan-matching/route-intent",
        json={"message": "我们年营业额 800 万，要付越南供应商 120 万，适合什么贷款？"},
    ).json()
    result.check(
        "trigger",
        "Vietnam supplier sample prefill is accurate",
        sample["prefill"]
        == {
            "business_scenario": "overseas_procurement",
            "annual_turnover_hkd": 8_000_000,
            "financing_purpose": "procurement_payment",
            "requested_amount_hkd": 1_200_000,
            "target_market": "越南",
        },
        json.dumps(sample["prefill"], ensure_ascii=False),
    )


def run_clarification_eval(database_url: str, result: Eval) -> None:
    valid = parse_clarifier_payload(
        {
            "extracted_updates": {"annual_turnover_hkd": 20_000_000},
            "ready_to_match": False,
            "missing_slot": "financing_purpose",
            "question_to_user": "融资用途是什么？",
        }
    )
    result.check(
        "clarification",
        "valid structured extraction passes Pydantic",
        valid.extracted_updates.annual_turnover_hkd == 20_000_000,
    )
    for name, payload in [
        ("malformed JSON rejected", "{"),
        (
            "illegal enum rejected",
            {
                "extracted_updates": {"business_scenario": "invented_scenario"},
                "ready_to_match": False,
            },
        ),
        (
            "negative number rejected",
            {
                "extracted_updates": {"annual_turnover_hkd": -1},
                "ready_to_match": False,
            },
        ),
    ]:
        rejected = False
        try:
            parse_clarifier_payload(payload)
        except (json.JSONDecodeError, ValidationError):
            rejected = True
        result.check("clarification", name, rejected)

    app = create_app(
        database_url=database_url,
        clarifier=FakeUnavailableClarifier(),
        catalog_mode="demo",
    )
    with TestClient(app) as client:
        session = client.post("/crossbridge/v1/loan-matching/sessions", json={}).json()
        response = client.post(
            f"/crossbridge/v1/loan-matching/sessions/{session['id']}/clarify",
            json={"message": "两千万港币"},
        ).json()
        result.check(
            "clarification",
            "LLM outage keeps draft unchanged and returns manual fallback",
            response["clarifier_mode"] == "manual_fallback"
            and response["draft_profile"]["annual_turnover_hkd"] is None,
        )
        for _ in range(3):
            response = client.post(
                f"/crossbridge/v1/loan-matching/sessions/{session['id']}/clarify",
                json={"message": "继续"},
            ).json()
        result.check(
            "clarification",
            "clarification stops at maximum of 3 attempts",
            response["clarification_count"] == 3,
            str(response["clarification_count"]),
        )
        blocked = client.post(
            f"/crossbridge/v1/loan-matching/sessions/{session['id']}/match"
        )
        result.check(
            "clarification",
            "matching is blocked while required fields are missing",
            blocked.status_code == 422,
            str(blocked.status_code),
        )


def run_matching_and_memory_eval(database_url: str, result: Eval) -> None:
    app = create_app(
        database_url=database_url,
        clarifier=FakeValidClarifier(),
        catalog_mode="demo",
    )
    with TestClient(app) as client:
        result.check(
            "matching",
            "mock catalog contains exactly three products",
            len(DEMO_PRODUCTS) == 3,
        )
        session = client.post(
            "/crossbridge/v1/loan-matching/sessions",
            json={
                "prefill": {
                    "business_scenario": "overseas_procurement",
                    "annual_turnover_hkd": 8_000_000,
                    "financing_purpose": "procurement_payment",
                    "requested_amount_hkd": 1_200_000,
                    "target_market": "越南",
                }
            },
        ).json()
        result.check(
            "memory",
            "draft creation does not write long-term profile",
            client.get("/crossbridge/v1/sme-profiles/demo_sme_001").json()["profile"] is None,
        )
        first = client.post(
            f"/crossbridge/v1/loan-matching/sessions/{session['id']}/match"
        ).json()
        second = client.post(
            f"/crossbridge/v1/loan-matching/sessions/{session['id']}/match"
        ).json()
        result.check(
            "matching",
            "procurement scenario deterministically matches one expected product",
            [item["product"]["product_id"] for item in first["match_results"]]
            == ["demo_overseas_procurement_working_capital"],
        )
        result.check(
            "matching",
            "repeated matching returns identical product cards",
            first["match_results"] == second["match_results"],
        )
        card = first["match_results"][0]["product"]
        catalog = next(
            item
            for item in DEMO_PRODUCTS
            if item["id"] == "demo_overseas_procurement_working_capital"
        )
        result.check(
            "matching",
            "product numeric terms come directly from catalog snapshot",
            card["loan_limit_text"] == catalog["loan_limit_text"]
            and card["tenor_text"] == catalog["tenor_text"]
            and card["repayment_method_text"] == catalog["repayment_method_text"],
        )
        result.check(
            "matching",
            "all product cards carry DEMO ONLY disclaimer",
            all(
                item["product"]["demo_only"]
                and "DEMO ONLY" in item["product"]["disclaimer"]
                for item in first["match_results"]
            ),
        )
        english_product = card["localization"]["en"]
        english_values = json.dumps(english_product, ensure_ascii=False)
        result.check(
            "i18n",
            "matched product snapshot includes English card text",
            english_product["product_name"] == "Overseas Procurement Working Capital Plan",
        )
        result.check(
            "i18n",
            "English product localization contains no Chinese fallback text",
            re.search(r"[\u4e00-\u9fff]", english_values) is None,
            english_values,
        )
        client.post(
            f"/crossbridge/v1/loan-matching/sessions/{session['id']}/save-profile"
        )
        saved = client.get("/crossbridge/v1/sme-profiles/demo_sme_001").json()["profile"]
        result.check(
            "memory",
            "explicit confirmation saves long-term profile",
            saved["annual_turnover_hkd"] == 8_000_000,
        )
        new_session = client.post(
            "/crossbridge/v1/loan-matching/sessions", json={}
        ).json()
        result.check(
            "memory",
            "new session loads confirmed profile",
            new_session["draft_profile"]["annual_turnover_hkd"] == 8_000_000,
        )
        client.delete("/crossbridge/v1/sme-profiles/demo_sme_001")
        result.check(
            "memory",
            "clear endpoint removes long-term profile",
            client.get("/crossbridge/v1/sme-profiles/demo_sme_001").json()["profile"] is None,
        )
        with app.state.SessionLocal() as db:
            event_types = list(db.scalars(select(AuditEvent.event_type)))
        result.check(
            "memory",
            "save and clear append audit events",
            "sme_profile_saved" in event_types and "sme_profile_cleared" in event_types,
        )


def run_ui_i18n_static_eval(result: Eval) -> None:
    app_source = (ROOT / "chatraw-fork" / "backend" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    html_source = (
        ROOT / "chatraw-fork" / "backend" / "static" / "index.html"
    ).read_text(encoding="utf-8")
    keys = [
        "cbLoanMatching",
        "cbWorkspaceTitle",
        "cbDraftTitle",
        "cbClarifierTitle",
        "cbCurrentQuestion",
        "cbStillNeeded",
        "cbMatchCandidates",
        "cbCandidatesTitle",
        "cbDemoCardDisclaimer",
        "cbOfficialTag",
        "cbOfficialCardDisclaimer",
        "cbInterestRate",
        "cbFee",
        "cbPublicGuidance",
        "cbRequiredDocuments",
        "cbThresholds",
        "cbOfficialSource",
        "cbSourceCheckedAt",
        "cbReviewStatus",
        "cbReviewPending",
        "cbReasonAmountConfirm",
        "cbReasonTurnoverConfirm",
        "cbReasonOfficialSource",
        "cbFieldLoanLimit",
        "cbFieldInterestRate",
        "cbFieldCatalogReview",
        "cbSaveProfile",
        "cbQuestionScenario",
        "cbReasonScenario",
    ]
    result.check(
        "i18n",
        "Function 1 UI keys exist in both English and Chinese dictionaries",
        all(app_source.count(f"{key}:") == 2 for key in keys),
    )
    workspace = html_source.split(
        "<!-- Function 1: SME loan-matching workspace -->", 1
    )[1].split("</section>\n    </main>", 1)[0]
    visible_text_nodes = " ".join(
        text.strip()
        for text in re.findall(r">([^<{]+)<", workspace)
        if text.strip() and not text.strip().startswith("<!--")
    )
    result.check(
        "i18n",
        "Function 1 workspace has no hard-coded Chinese visible text nodes",
        re.search(r"[\u4e00-\u9fff]", visible_text_nodes) is None,
        visible_text_nodes,
    )
    result.check(
        "i18n",
        "product cards render localized fields and reason codes",
        "loanLocalizedProduct(result.product, 'product_name')" in workspace
        and "loanReasonLabel(reason)" in workspace
        and "loanFieldLabel(field)" in workspace,
    )
    result.check(
        "i18n",
        "official-source cards render dynamic disclaimer, source link and review status",
        "loanCardDisclaimer(result.product)" in workspace
        and ':href="sourceRef.source_url"' in workspace
        and "loanReviewStatusLabel(result.product)" in workspace,
    )


def run_migration_eval(result: Eval) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "migration.db"
        database_url = f"sqlite:///{db_path}"
        run_migrations(database_url)
        run_migrations(database_url)
        conn = sqlite3.connect(db_path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        expected = {
            "alembic_version",
            "audit_events",
            "loan_products",
            "match_results",
            "matching_sessions",
            "sme_profiles",
        }
        result.check(
            "migration",
            "empty SQLite upgrades to expected schema",
            expected.issubset(tables),
            ", ".join(sorted(tables)),
        )
        conn.execute(
            "INSERT INTO sme_profiles VALUES (?, ?, ?, ?)",
            ("preserved", "{}", "2026-05-30", "2026-05-30"),
        )
        conn.commit()
        run_migrations(database_url)
        preserved = conn.execute(
            "SELECT COUNT(*) FROM sme_profiles WHERE sme_id = 'preserved'"
        ).fetchone()[0]
        result.check(
            "migration",
            "repeated migration preserves existing rows",
            preserved == 1,
        )
        conn.close()


def write_report(result: Eval) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "passed": result.passed,
        "total": result.total,
        "sections": result.sections,
        "summary": result.summary(),
    }
    json_path = REPORTS_DIR / f"function1_eval_{timestamp}.json"
    md_path = REPORTS_DIR / f"function1_eval_{timestamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Function 1 Eval Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Result: **{result.passed}/{result.total} passed**",
        "",
    ]
    for section, cases in result.sections.items():
        lines.extend([f"## {section.title()}", ""])
        for case in cases:
            status = "PASS" if case["passed"] else "FAIL"
            detail = f" - {case['detail']}" if case["detail"] else ""
            lines.append(f"- `{status}` {case['name']}{detail}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> int:
    result = Eval()
    run_migration_eval(result)
    run_ui_i18n_static_eval(result)
    with tempfile.TemporaryDirectory() as temp_dir:
        trigger_db = f"sqlite:///{Path(temp_dir) / 'trigger.db'}"
        app = create_app(
            database_url=trigger_db,
            clarifier=FakeValidClarifier(),
            catalog_mode="demo",
        )
        with TestClient(app) as client:
            run_trigger_eval(client, app, result)
    with tempfile.TemporaryDirectory() as temp_dir:
        run_clarification_eval(f"sqlite:///{Path(temp_dir) / 'clarify.db'}", result)
    with tempfile.TemporaryDirectory() as temp_dir:
        run_matching_and_memory_eval(f"sqlite:///{Path(temp_dir) / 'matching.db'}", result)
    report = write_report(result)
    print(json.dumps({"passed": result.passed, "total": result.total, "report": str(report)}, ensure_ascii=False))
    return 0 if result.passed == result.total else 1


if __name__ == "__main__":
    raise SystemExit(main())

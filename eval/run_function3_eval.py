#!/usr/bin/env python3
"""Function 3 eval - loan-application progress timeline (port 8083 service).

Mirrors the Function 1/2 eval harness: temp SQLite + own migrations + TestClient,
flat case list, markdown/json report under eval/reports/, exit 0/1.

Function 3 is fully independent at runtime (its own DB, own Alembic env). It delegates
submission-readiness to Function 2 over HTTP; here that dependency is injected as a
stub (``readiness_checker``) so the test is hermetic and never starts Function 2.
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

from server.application_timeline.app import compute_sse_events, create_app
from server.application_timeline.db import build_engine, build_session_factory, run_migrations
from server.application_timeline.models import TimelineAuditEvent, TimelineNode

REPORTS_DIR = ROOT / "eval" / "reports"

API = "/crossbridge-timeline/v1"
ADMIN = "/crossbridge-timeline-admin/v1"


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


class StubReadiness:
    """Injected stand-in for the Function 2 readiness call."""

    def __init__(self) -> None:
        self.ready = True
        self.blocking: list[dict] = []

    def __call__(self, origin_package_id: str) -> dict:
        return {"ready": self.ready, "blocking": self.blocking, "warnings": []}


def _states(application: dict) -> dict[str, str]:
    return {n["node_code"]: n["state"] for n in application["nodes"]}


def _create(client: TestClient, origin_package_id: str, **extra) -> "object":
    body = {
        "sme_id": extra.get("sme_id", "demo_sme_001"),
        "origin_package_id": origin_package_id,
        "product_id": extra.get("product_id", "bochk_tt"),
        "product_label_zh": extra.get("product_label_zh", "跨境汇款"),
        "product_label_en": extra.get("product_label_en", "Cross-border TT"),
        "scenario_code": extra.get("scenario_code", "import_payment"),
    }
    return client.post(f"{API}/applications", json=body)


def _patch(client: TestClient, app_id: str, node_code: str, **body) -> "object":
    return client.patch(f"{ADMIN}/applications/{app_id}/nodes/{node_code}", json=body)


def run_checks() -> Checks:
    result = Checks()

    # SSE poll diff is a pure function — test it directly (live SSE is browser-verified).
    seen: dict[str, str] = {}
    first = compute_sse_events([("a", "t1"), ("b", "t1")], seen)
    second = compute_sse_events([("a", "t1"), ("b", "t1")], seen)
    third = compute_sse_events([("a", "t2"), ("b", "t1")], seen)
    result.check(
        "SSE diff emits new+changed applications only",
        sorted(x[0] for x in first) == ["a", "b"]
        and second == []
        and third == [("a", "t2")],
        json.dumps({"first": first, "second": second, "third": third}),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        database_url = f"sqlite:///{Path(temp_dir) / 'f3.db'}"
        run_migrations(database_url)
        run_migrations(database_url)  # repeatable: running head twice is a no-op
        result.check("migrations run repeatably", True)

        stub = StubReadiness()
        app = create_app(
            database_url=database_url, migrate_on_startup=False, readiness_checker=stub
        )
        with TestClient(app) as client:
            result.check("GET /healthz ok", client.get("/healthz").json().get("status") == "ok")

            # --- not ready -> 422 (no application created) -----------------
            stub.ready = False
            stub.blocking = [{"code": "swift_bic"}]
            blocked = _create(client, "PKG-NR")
            result.check(
                "unready materials are rejected with 422 + blocking reasons",
                blocked.status_code == 422
                and any(b["code"] == "swift_bic" for b in blocked.json()["detail"]["blocking"]),
                json.dumps(blocked.json()),
            )

            # --- ready -> 201 with correct initial node states -------------
            stub.ready = True
            stub.blocking = []
            created = _create(client, "PKG-1")
            cj = created.json()
            app_id = cj["id"]
            result.check("ready submission creates application (201)", created.status_code == 201)
            result.check(
                "six fixed nodes initialised (submitted=completed, material_review=in_progress)",
                _states(cj)
                == {
                    "submitted": "completed",
                    "material_review": "in_progress",
                    "credit_assessment": "pending",
                    "approval_result": "pending",
                    "signing": "pending",
                    "disbursement": "pending",
                }
                and cj["current_node_code"] == "material_review"
                and cj["status"] == "in_progress",
                json.dumps(_states(cj)),
            )
            result.check(
                "SME serialization never exposes internal_note",
                all("internal_note" not in n for n in cj["nodes"]),
            )

            # --- idempotency: same package returns the original application -
            again = _create(client, "PKG-1")
            result.check(
                "second submit of the same package is idempotent",
                again.status_code == 200
                and again.json()["id"] == app_id
                and again.json()["resumed"] is True,
                json.dumps({"status": again.status_code, "resumed": again.json().get("resumed")}),
            )

            # --- list + detail --------------------------------------------
            listing = client.get(f"{API}/applications", params={"sme_id": "demo_sme_001"})
            result.check(
                "GET /applications lists the SME's application",
                any(a["id"] == app_id for a in listing.json()["applications"]),
            )
            detail = client.get(f"{API}/applications/{app_id}")
            result.check("GET /applications/{id} returns 200", detail.status_code == 200)

            # --- illegal skip: cannot change a non-current node ------------
            skip = _patch(client, app_id, "credit_assessment", state="completed")
            result.check("advancing a non-current node is rejected (409)", skip.status_code == 409)

            # --- ordered advance: complete current -> next becomes active --
            adv = _patch(client, app_id, "material_review", state="completed")
            aj = adv.json()
            result.check(
                "completing the current node advances to the next",
                adv.status_code == 200
                and aj["current_node_code"] == "credit_assessment"
                and _states(aj)["material_review"] == "completed"
                and _states(aj)["credit_assessment"] == "in_progress",
                json.dumps(_states(aj)),
            )
            result.check(
                "admin serialization includes internal_note",
                all("internal_note" in n for n in aj["nodes"]),
            )

            # --- internal note stays bank-private -------------------------
            _patch(client, app_id, "credit_assessment", internal_note="pull CRA report")
            sme_view = client.get(f"{API}/applications/{app_id}").json()
            result.check(
                "internal_note written by admin is absent from the SME view",
                all("internal_note" not in n for n in sme_view["nodes"]),
            )

            # --- SSE source-of-truth: any admin write bumps updated_at -----
            before = client.get(f"{API}/applications/{app_id}").json()["updated_at"]
            _patch(client, app_id, "credit_assessment", customer_note_zh="审核中", customer_note_en="reviewing")
            after = client.get(f"{API}/applications/{app_id}").json()["updated_at"]
            result.check(
                "an admin update bumps application.updated_at (drives SSE)",
                after != before
                and compute_sse_events([(app_id, after)], {app_id: before}) == [(app_id, after)],
                json.dumps({"before": before, "after": after}),
            )

            # --- rejected / supplement_required require bilingual notes ----
            rej = _create(client, "PKG-REJ").json()
            rej_id = rej["id"]
            missing = _patch(client, rej_id, "material_review", state="rejected")
            result.check(
                "rejecting without bilingual customer notes is rejected (422)",
                missing.status_code == 422,
            )
            ok_rej = _patch(
                client, rej_id, "material_review",
                state="rejected", customer_note_zh="资料不足", customer_note_en="insufficient",
            )
            result.check(
                "rejecting with bilingual notes sets application status rejected",
                ok_rej.status_code == 200 and ok_rej.json()["status"] == "rejected",
                json.dumps(ok_rej.json().get("status")),
            )

            sup = _create(client, "PKG-SUP").json()
            sup_id = sup["id"]
            sup_missing = _patch(client, sup_id, "material_review", state="supplement_required")
            result.check(
                "supplement_required without bilingual notes is rejected (422)",
                sup_missing.status_code == 422,
            )
            sup_ok = _patch(
                client, sup_id, "material_review",
                state="supplement_required", customer_note_zh="请补合同", customer_note_en="add contract",
            )
            sj = sup_ok.json()
            result.check(
                "supplement_required keeps the node current and application in progress",
                sup_ok.status_code == 200
                and sj["current_node_code"] == "material_review"
                and _states(sj)["material_review"] == "supplement_required"
                and sj["status"] == "in_progress",
                json.dumps({"current": sj["current_node_code"], "status": sj["status"]}),
            )

            # --- completing the final node completes the application -------
            full = _create(client, "PKG-FULL").json()
            full_id = full["id"]
            for code in ("material_review", "credit_assessment", "approval_result", "signing", "disbursement"):
                last = _patch(client, full_id, code, state="completed")
            fj = last.json()
            result.check(
                "completing the last node marks the application completed",
                fj["status"] == "completed"
                and all(s == "completed" for s in _states(fj).values()),
                json.dumps(_states(fj)),
            )

            # --- reset restores the initial node states -------------------
            rst = client.post(f"{ADMIN}/applications/{full_id}/reset")
            rstj = rst.json()
            result.check(
                "reset restores initial node states and status",
                rst.status_code == 200
                and rstj["current_node_code"] == "material_review"
                and rstj["status"] == "in_progress"
                and _states(rstj)["submitted"] == "completed"
                and _states(rstj)["material_review"] == "in_progress"
                and _states(rstj)["credit_assessment"] == "pending",
                json.dumps(_states(rstj)),
            )

            # --- admin console + admin list -------------------------------
            result.check(
                "hidden admin page is served",
                client.get("/crossbridge-admin/timeline").status_code == 200,
            )
            admin_list = client.get(f"{ADMIN}/applications")
            result.check(
                "admin list returns all applications with internal_note",
                admin_list.status_code == 200
                and len(admin_list.json()["applications"]) >= 4
                and all(
                    "internal_note" in n
                    for a in admin_list.json()["applications"]
                    for n in a["nodes"]
                ),
            )

            # --- admin delete: row gone, list shrinks, package resubmittable
            dele = client.delete(f"{ADMIN}/applications/{full_id}")
            after_list = client.get(f"{ADMIN}/applications").json()["applications"]
            result.check(
                "admin delete removes the application from detail and list",
                dele.status_code == 200
                and dele.json().get("deleted") is True
                and client.get(f"{API}/applications/{full_id}").status_code == 404
                and all(a["id"] != full_id for a in after_list),
            )
            result.check(
                "admin delete on unknown id returns 404",
                client.delete(f"{ADMIN}/applications/{full_id}").status_code == 404,
            )
            recreated = _create(client, "PKG-FULL")
            result.check(
                "deleting frees the origin_package_id for a fresh submission",
                recreated.status_code == 201
                and recreated.json()["resumed"] is False
                and recreated.json()["id"] != full_id,
            )

        # --- audit trail --------------------------------------------------
        session = build_session_factory(build_engine(database_url))()
        try:
            audit_types = {e.event_type for e in session.query(TimelineAuditEvent).all()}
            orphan_nodes = (
                session.query(TimelineNode)
                .filter(TimelineNode.application_id == full_id)
                .count()
            )
        finally:
            session.close()
        result.check(
            "audit events recorded for create, node update, reset and delete",
            {
                "timeline_application_created",
                "timeline_node_updated",
                "timeline_application_reset",
                "timeline_application_deleted",
            }
            <= audit_types,
            json.dumps(sorted(audit_types)),
        )
        result.check(
            "admin delete leaves no orphan timeline_nodes rows",
            orphan_nodes == 0,
            f"orphan_nodes={orphan_nodes}",
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
    json_path = REPORTS_DIR / f"function3_eval_{timestamp}.json"
    md_path = REPORTS_DIR / f"function3_eval_{timestamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Function 3 Application Timeline Eval Report",
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

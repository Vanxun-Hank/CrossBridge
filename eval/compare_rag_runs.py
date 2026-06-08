#!/usr/bin/env python3
"""Compare two cached CrossBridge RAG/RAGAS runs.

This is API-free. It is intended for iteration acceptance checks after a new
subset or full RAGAS run is available:

  - metric movement versus the accepted baseline
  - no accepted-baseline metric drops by more than the configured tolerance
  - context-ID additions/removals for weak samples
  - expected/off-target document movement
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

METRICS = [
    "faithfulness",
    "answer_relevancy",
    "id_based_context_precision",
    "id_based_context_recall",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric != numeric:
        return None
    return numeric


def by_id(report: dict) -> dict[str, dict]:
    return {row["id"]: row for row in report.get("per_question", [])}


def mean_metric(rows: list[dict], metric: str) -> float | None:
    values = [as_float(row.get(metric)) for row in rows]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def context_ids(row: dict) -> list[str]:
    return [str(item) for item in row.get("context_ids", []) if item]


def expected_ids(row: dict) -> set[str]:
    return set(str(item) for item in row.get("reference_context_ids", []) if item)


def unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def set_delta(candidate: list[str], baseline: list[str]) -> dict:
    candidate_set = set(candidate)
    baseline_set = set(baseline)
    return {
        "added": sorted(candidate_set - baseline_set),
        "removed": sorted(baseline_set - candidate_set),
        "kept": sorted(candidate_set & baseline_set),
    }


def compare_reports(args: argparse.Namespace) -> dict:
    baseline = load_json(Path(args.baseline_ragas))
    candidate = load_json(Path(args.candidate_ragas))
    base_rows = by_id(baseline)
    cand_rows = by_id(candidate)
    common_ids = sorted(set(base_rows) & set(cand_rows))

    common_base = [base_rows[qid] for qid in common_ids]
    common_cand = [cand_rows[qid] for qid in common_ids]

    metric_summary = {}
    improved_metrics = []
    regressions = []
    missing_candidate_metrics = []
    for metric in METRICS:
        base_mean = mean_metric(common_base, metric)
        cand_mean = mean_metric(common_cand, metric)
        delta = None
        if base_mean is not None and cand_mean is not None:
            delta = round(cand_mean - base_mean, 4)
            if delta > 0:
                improved_metrics.append(metric)
            if delta < -abs(args.max_metric_drop):
                regressions.append(metric)
        elif base_mean is not None and cand_mean is None:
            missing_candidate_metrics.append(metric)
        metric_summary[metric] = {
            "baseline_mean": base_mean,
            "candidate_mean": cand_mean,
            "delta": delta,
        }

    per_question = []
    for qid in common_ids:
        base = base_rows[qid]
        cand = cand_rows[qid]
        base_contexts = context_ids(base)
        cand_contexts = context_ids(cand)
        expected = expected_ids(cand) or expected_ids(base)
        base_unique = unique_keep_order(base_contexts)
        cand_unique = unique_keep_order(cand_contexts)

        metric_deltas = {}
        for metric in METRICS:
            b = as_float(base.get(metric))
            c = as_float(cand.get(metric))
            metric_deltas[metric] = {
                "baseline": b,
                "candidate": c,
                "delta": None if b is None or c is None else round(c - b, 4),
            }

        base_off_target = sorted(set(base_unique) - expected)
        cand_off_target = sorted(set(cand_unique) - expected)
        base_missing_expected = sorted(expected - set(base_unique))
        cand_missing_expected = sorted(expected - set(cand_unique))

        per_question.append({
            "id": qid,
            "scenario": cand.get("scenario") or base.get("scenario"),
            "metric_deltas": metric_deltas,
            "context_delta": set_delta(cand_unique, base_unique),
            "baseline_context_ids": base_contexts,
            "candidate_context_ids": cand_contexts,
            "off_target_delta": set_delta(cand_off_target, base_off_target),
            "missing_expected_delta": set_delta(cand_missing_expected, base_missing_expected),
            "baseline_off_target_count": len(base_off_target),
            "candidate_off_target_count": len(cand_off_target),
            "baseline_missing_expected_count": len(base_missing_expected),
            "candidate_missing_expected_count": len(cand_missing_expected),
        })

    preliminary_passes_available_metrics = bool(improved_metrics) and not regressions
    acceptance_gate = {
        "max_metric_drop": args.max_metric_drop,
        "has_any_metric_improvement": bool(improved_metrics),
        "improved_metrics": improved_metrics,
        "regressions_over_threshold": regressions,
        "missing_candidate_metrics": missing_candidate_metrics,
        "complete_metric_coverage": not missing_candidate_metrics,
        "preliminary_passes_available_metrics": preliminary_passes_available_metrics,
        "passes": preliminary_passes_available_metrics and not missing_candidate_metrics,
    }

    return {
        "summary": {
            "baseline_ragas": str(Path(args.baseline_ragas)),
            "candidate_ragas": str(Path(args.candidate_ragas)),
            "common_question_count": len(common_ids),
            "metric_summary": metric_summary,
            "acceptance_gate": acceptance_gate,
        },
        "per_question": per_question,
    }


def write_reports(payload: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    json_path = out_dir / f"rag_run_comparison_{ts}.json"
    md_path = out_dir / f"rag_run_comparison_{ts}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    gate = payload["summary"]["acceptance_gate"]
    lines = [
        "# RAG Run Comparison",
        "",
        f"- Baseline: `{payload['summary']['baseline_ragas']}`",
        f"- Candidate: `{payload['summary']['candidate_ragas']}`",
        f"- Common questions: {payload['summary']['common_question_count']}",
        f"- Acceptance gate: {'PASS' if gate['passes'] else 'FAIL'}",
        f"- Improved metrics: {', '.join(gate['improved_metrics']) or 'none'}",
        f"- Regressions over {gate['max_metric_drop']}: {', '.join(gate['regressions_over_threshold']) or 'none'}",
        f"- Missing candidate metrics: {', '.join(gate['missing_candidate_metrics']) or 'none'}",
        "",
        "## Metric Means",
        "",
        "| Metric | baseline | candidate | delta |",
        "|---|---:|---:|---:|",
    ]
    for metric, item in payload["summary"]["metric_summary"].items():
        lines.append(
            f"| `{metric}` | {item['baseline_mean']} | {item['candidate_mean']} | {item['delta']} |"
        )

    lines.extend([
        "",
        "## Per-Question Context Movement",
        "",
        "| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |",
        "|---|---|---|---|---|---|",
    ])
    for row in payload["per_question"]:
        metric_bits = []
        for metric, item in row["metric_deltas"].items():
            if item["delta"] not in (None, 0):
                metric_bits.append(f"{metric}:{item['delta']:+.4f}")
        metric_text = ", ".join(metric_bits) or "0"
        off_target = (
            f"{row['baseline_off_target_count']} -> {row['candidate_off_target_count']} "
            f"(+{len(row['off_target_delta']['added'])}/-{len(row['off_target_delta']['removed'])})"
        )
        missing = (
            f"{row['baseline_missing_expected_count']} -> {row['candidate_missing_expected_count']} "
            f"(+{len(row['missing_expected_delta']['added'])}/-{len(row['missing_expected_delta']['removed'])})"
        )
        context_changes = (
            f"+{len(row['context_delta']['added'])}/-{len(row['context_delta']['removed'])}"
        )
        lines.append(
            f"| {row['id']} | {row.get('scenario') or ''} | {metric_text} | "
            f"{off_target} | {missing} | {context_changes} |"
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline-ragas",
        default=str(PROJECT_ROOT / "eval/reports/ragas_full_20260601_180627.json"),
    )
    parser.add_argument(
        "--candidate-ragas",
        default=str(PROJECT_ROOT / "eval/reports/ragas_full_20260601_180627.json"),
    )
    parser.add_argument("--max-metric-drop", type=float, default=0.03)
    parser.add_argument(
        "--out-dir",
        default=str(PROJECT_ROOT / "eval/reports"),
    )
    args = parser.parse_args()
    payload = compare_reports(args)
    json_path, md_path = write_reports(payload, Path(args.out_dir))
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"[rag-compare] reports: {json_path}, {md_path}")


if __name__ == "__main__":
    main()

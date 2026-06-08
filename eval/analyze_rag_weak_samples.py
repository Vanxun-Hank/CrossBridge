#!/usr/bin/env python3
"""Offline weak-sample analyzer for CrossBridge Policy RAG.

This script needs no LLM/API access. It reads cached RAGAS reports and cached
RAG outputs, applies the goal thresholds, and classifies likely root causes so
each iteration starts from evidence rather than ad hoc inspection.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGETS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.85,
    "id_based_context_precision": 0.80,
    "id_based_context_recall": 0.80,
}

ROOT_CAUSES = {
    "missing_source_coverage",
    "outdated_source",
    "wrong_source_retrieved",
    "insufficient_chunk_granularity",
    "weak_citation_mapping",
    "incomplete_answer_synthesis",
    "overly_technical_explanation",
    "hallucinated_claim",
    "poor_query_expansion",
}

UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\busually\b",
        r"\bgenerally\b",
        r"industry practice",
        r"reasonable inference",
        r"可合理推断",
        r"行业惯例",
        r"行业通用",
        r"通常",
        r"一般",
        r"供参考",
        r"不构成承诺",
        r"T\+\d",
        r"交易编码",
        r"BIR\d+",
        r"1[–-]2\s*年",
        r"6[–-]12\s*个月",
        r"Vietcombank|BIDV|Sacombank|Techcombank|VPBank|ACB|Eximbank",
    ]
]

JARGON_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bCDD\b|\bEDD\b|\bKYB\b|\bAML\b|\bCFT\b|\bODI\b|\bRCPMIS?\b",
        r"资本项目|经常项目|展业原则|跨境担保|涉外收付款申报",
    ]
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_questions(path: Path) -> dict[str, dict]:
    questions: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                q = json.loads(line)
                questions[q["id"]] = q
    return questions


def load_chunks_doc_ids(path: Path) -> set[str]:
    doc_ids: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            if chunk.get("doc_id"):
                doc_ids.add(chunk["doc_id"])
    return doc_ids


def metadata_by_id(path: Path) -> dict[str, dict]:
    return {item["id"]: item for item in load_json(path)}


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


def unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def contains_pattern(patterns: list[re.Pattern], text: str) -> bool:
    return any(pattern.search(text or "") for pattern in patterns)


def source_family(meta: dict | None) -> str:
    if not meta:
        return "unknown"
    authority = str(meta.get("authority_level") or "")
    issuer = str(meta.get("issuer") or "")
    if "bank" in authority:
        return "bank"
    if authority in {"regulator", "regulator_research", "tax_authority"}:
        return "regulator"
    if authority == "central_bank":
        return "central_bank"
    if authority.startswith("government"):
        return "government"
    if "HKMC" in issuer:
        return "scheme_operator"
    return authority or "unknown"


def classify_row(
    row: dict,
    question: dict,
    metadata: dict[str, dict],
    chunk_doc_ids: set[str],
) -> tuple[list[str], list[str], str]:
    causes: set[str] = set()
    evidence: list[str] = []

    expected = set(row.get("reference_context_ids") or question.get("expected_doc_ids") or [])
    retrieved = [item for item in row.get("context_ids", []) if item]
    retrieved_unique = unique_keep_order(retrieved)
    retrieved_set = set(retrieved_unique)
    off_target = sorted(retrieved_set - expected)
    missing_expected = sorted(expected - retrieved_set)

    missing_from_corpus = sorted(doc_id for doc_id in expected if doc_id not in chunk_doc_ids)
    if missing_from_corpus:
        causes.add("missing_source_coverage")
        evidence.append(f"expected docs absent from chunks: {', '.join(missing_from_corpus)}")

    precision = as_float(row.get("id_based_context_precision"))
    recall = as_float(row.get("id_based_context_recall"))
    faithfulness = as_float(row.get("faithfulness"))
    relevancy = as_float(row.get("answer_relevancy"))

    if recall is not None and recall < TARGETS["id_based_context_recall"]:
        if missing_expected:
            causes.add("wrong_source_retrieved")
            evidence.append(f"missing expected docs in prompt contexts: {', '.join(missing_expected)}")
    if precision is not None and precision < TARGETS["id_based_context_precision"]:
        if off_target:
            causes.add("wrong_source_retrieved")
            evidence.append(f"off-target prompt docs: {', '.join(off_target)}")

    duplicate_count = len(retrieved) - len(retrieved_unique)
    if duplicate_count > 0:
        causes.add("insufficient_chunk_granularity")
        evidence.append(f"duplicate parent doc IDs in prompt contexts: {duplicate_count}")

    if not retrieved:
        causes.add("weak_citation_mapping")
        evidence.append("no context IDs captured for evaluation")

    answer = row.get("answer") or ""
    if contains_pattern(UNSUPPORTED_CLAIM_PATTERNS, answer):
        causes.add("hallucinated_claim")
        evidence.append("answer contains unsupported-claim cue words or examples")

    if faithfulness is not None and faithfulness < TARGETS["faithfulness"]:
        if expected & retrieved_set:
            causes.add("incomplete_answer_synthesis")
            evidence.append("faithfulness below target despite at least one expected context")
        else:
            causes.add("wrong_source_retrieved")

    if relevancy is not None and relevancy < TARGETS["answer_relevancy"]:
        causes.add("incomplete_answer_synthesis")
        evidence.append("answer relevancy below target")

    if contains_pattern(JARGON_PATTERNS, answer) and len(answer) > 1600:
        causes.add("overly_technical_explanation")
        evidence.append("long answer contains dense regulatory jargon")

    q_text = question.get("question", row.get("question", ""))
    q_mentions_fee_time = any(term in q_text for term in ["费用", "收费", "到账", "多久"])
    q_mentions_product = any(term in q_text for term in ["产品", "贷款", "融资"])
    if off_target:
        families = Counter(source_family(metadata.get(doc_id)) for doc_id in off_target)
        if q_mentions_fee_time and (families["regulator"] or families["central_bank"]):
            causes.add("poor_query_expansion")
            evidence.append("fee/time query retrieved regulatory source families")
        if q_mentions_product and families["bank"]:
            regions = {
                doc_id: metadata.get(doc_id, {}).get("region")
                for doc_id in off_target
                if metadata.get(doc_id)
            }
            if regions:
                evidence.append(f"off-target bank/product source regions: {regions}")

    if not causes:
        causes.add("incomplete_answer_synthesis")
        evidence.append("weak metrics without a deterministic retrieval cause")

    next_action = choose_next_action(causes)
    return sorted(causes), evidence, next_action


def choose_next_action(causes: set[str]) -> str:
    if "missing_source_coverage" in causes:
        return "crawl_or_ingest_missing_official_source"
    if "wrong_source_retrieved" in causes or "poor_query_expansion" in causes:
        return "tune_retrieval_rerank_or_prompt_source_filter"
    if "insufficient_chunk_granularity" in causes or "weak_citation_mapping" in causes:
        return "adjust_chunk_or_prompt_context_selection"
    if "hallucinated_claim" in causes or "incomplete_answer_synthesis" in causes:
        return "tighten_prompt_grounding_or_answer_contract"
    if "overly_technical_explanation" in causes:
        return "improve_borrower_friendly_prompt_style"
    return "manual_review"


def analyze(args: argparse.Namespace) -> tuple[dict, str]:
    ragas = load_json(Path(args.ragas_report))
    questions = load_questions(Path(args.questions))
    metadata = metadata_by_id(Path(args.metadata_index))
    chunk_doc_ids = load_chunks_doc_ids(Path(args.chunks))

    per_question = []
    cause_counts: Counter[str] = Counter()
    weak_count = 0

    for row in ragas.get("per_question", []):
        qid = row["id"]
        question = questions.get(qid, {})
        metric_gaps = {}
        weak = False
        for metric, target in TARGETS.items():
            value = as_float(row.get(metric))
            if value is None or value < target:
                weak = True
                metric_gaps[metric] = {"value": value, "target": target}

        if not weak:
            continue

        weak_count += 1
        causes, evidence, next_action = classify_row(row, question, metadata, chunk_doc_ids)
        cause_counts.update(causes)
        expected = row.get("reference_context_ids") or question.get("expected_doc_ids") or []
        contexts = row.get("context_ids", [])
        per_question.append({
            "id": qid,
            "scenario": row.get("scenario") or question.get("scenario"),
            "question": row.get("question") or question.get("question"),
            "metric_gaps": metric_gaps,
            "root_causes": causes,
            "evidence": evidence,
            "expected_doc_ids": expected,
            "context_ids": contexts,
            "next_action": next_action,
        })

    summary = {
        "ragas_report": args.ragas_report,
        "n_questions": len(ragas.get("per_question", [])),
        "n_weak_questions": weak_count,
        "targets": TARGETS,
        "root_cause_counts": dict(cause_counts.most_common()),
    }
    payload = {"summary": summary, "weak_samples": per_question}
    return payload, write_reports(payload, Path(args.out_dir))


def write_reports(payload: dict, out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"weak_sample_analysis_{ts}.json"
    md_path = out_dir / f"weak_sample_analysis_{ts}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# RAG Weak-Sample Analysis",
        "",
        f"- RAGAS report: `{payload['summary']['ragas_report']}`",
        f"- Questions: {payload['summary']['n_questions']}",
        f"- Weak questions: {payload['summary']['n_weak_questions']}",
        "",
        "## Root Cause Counts",
        "",
        "| Root cause | Count |",
        "|---|---:|",
    ]
    for cause, count in payload["summary"]["root_cause_counts"].items():
        lines.append(f"| `{cause}` | {count} |")

    lines.extend([
        "",
        "## Weak Samples",
        "",
        "| ID | scenario | metric gaps | root causes | next action | evidence |",
        "|---|---|---|---|---|---|",
    ])
    for item in payload["weak_samples"]:
        gaps = ", ".join(
            f"{metric}={gap['value']} < {gap['target']}"
            for metric, gap in item["metric_gaps"].items()
        )
        causes = ", ".join(f"`{cause}`" for cause in item["root_causes"])
        evidence = "<br>".join(item["evidence"])[:1200]
        lines.append(
            f"| {item['id']} | {item.get('scenario') or ''} | {gaps} | "
            f"{causes} | `{item['next_action']}` | {evidence} |"
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return str(md_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ragas-report",
        default=str(PROJECT_ROOT / "eval/reports/ragas_full_20260601_180627.json"),
    )
    parser.add_argument(
        "--questions",
        default=str(PROJECT_ROOT / "eval/questions.jsonl"),
    )
    parser.add_argument(
        "--metadata-index",
        default=str(PROJECT_ROOT / "data/metadata_index.json"),
    )
    parser.add_argument(
        "--chunks",
        default=str(PROJECT_ROOT / "data/processed/chunks.jsonl"),
    )
    parser.add_argument(
        "--out-dir",
        default=str(PROJECT_ROOT / "eval/reports"),
    )
    args = parser.parse_args()
    payload, md_path = analyze(args)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"[weak-analysis] report: {md_path}")


if __name__ == "__main__":
    main()

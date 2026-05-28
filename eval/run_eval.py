"""
CrossBridge AI - Step 4a Eval Tier 1
=====================================
跑 retrieval 硬指标：recall@5 / recall@10 / citation_hit_rate。

支持三种 variant，diff 可以直接讲 pitch 故事：
  - baseline: 关 BM25 / 关 rerank / 关 multi-query / 关 citation filter
              （等于"裸 dense + 简单 query"）
  - step3:    Step 3 完整（BM25 + rerank + multi-query），但**关** citation filter
  - full:     Step 3.5 完整（含 citation gating，pitch 推荐配置）

用法:
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  .venv/bin/python eval/run_eval.py --variant full
  .venv/bin/python eval/run_eval.py --variant baseline
  .venv/bin/python eval/run_eval.py --variant step3
  # 三个 variant 一起跑（diff 表）：
  .venv/bin/python eval/run_eval.py --variant all

输出:
  eval/reports/eval_<variant>_<timestamp>.json     # 原始数据
  eval/reports/eval_<variant>_<timestamp>.md       # markdown 表（pitch slides 可粘）
  当 variant=all 时额外输出 eval_diff_<ts>.md      # 三个 variant 对比表
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 让 eval/ 下的脚本能 import files/ 里的模块
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "files"))


def load_questions(path: Path) -> list[dict]:
    qs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                qs.append(json.loads(line))
    return qs


def _disable_baseline_features(rag) -> None:
    """variant=baseline: 关 BM25 / 关 rerank / 关 query transformation。
    citation filter 也关掉（让 retrieval 召回直接进 citation 用于公平对比）。"""
    rag.retriever.bm25_index = None
    rag.retriever.reranker = None
    rag.bm25_index = None
    rag.reranker = None
    # query transformation 通过修改 mode 让 _forced_query_type 返回 "simple"
    rag.retriever.mode = "simple"
    # citation filter 通过 monkey-patch 旁路掉
    import rag_engine
    rag_engine.TRUSTED_TIERS_FOR_CITATION = frozenset(
        {"government", "regulator", "central_bank", "official_dev",
         "bank", "industry", "non_official", ""}
    )
    rag_engine.NON_CITABLE_DOCUMENT_TYPES = frozenset()


def _disable_citation_filter_only(rag) -> None:
    """variant=step3: BM25 + rerank + multi-query 都开，只关 citation filter。"""
    import rag_engine
    rag_engine.TRUSTED_TIERS_FOR_CITATION = frozenset(
        {"government", "regulator", "central_bank", "official_dev",
         "bank", "industry", "non_official", ""}
    )
    rag_engine.NON_CITABLE_DOCUMENT_TYPES = frozenset()


def run_one_variant(variant: str, questions: list[dict], top_k: int = 10) -> dict:
    """跑一个 variant，返回 per-question 结果 + 聚合指标。"""
    # rag_engine 模块状态会被 monkey-patch 修改，每个 variant 都需要重 import
    # 删除 sys.modules 强制重 import
    for mod in list(sys.modules):
        if mod in ("rag_engine", "bm25_index", "reranker"):
            del sys.modules[mod]

    from rag_engine import CrossBridgeRAG  # noqa: E402

    rag = CrossBridgeRAG(
        chunks_path=str(PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"),
        persist_directory=str(PROJECT_ROOT / "data" / "chroma"),
    )

    if variant == "baseline":
        _disable_baseline_features(rag)
    elif variant == "step3":
        _disable_citation_filter_only(rag)
    # variant == "full": 不动，跑默认 Step 3.5 全栈

    results = []
    n_recall5_hit = 0
    n_recall10_hit = 0
    n_citation_hit = 0
    n_filter_applied = 0
    elapsed_total = 0.0

    for q in questions:
        t0 = time.time()
        try:
            out = rag.ask(
                q["question"],
                # 故意不传 region/topic 过滤 —— eval 时让模型自己处理
                top_k=top_k,
                debug=True,
            )
        except Exception as e:
            print(f"  [{q['id']}] ERROR: {type(e).__name__}: {e}")
            results.append({"id": q["id"], "error": str(e)})
            continue
        elapsed = time.time() - t0
        elapsed_total += elapsed

        trace = out.get("retrieval_trace", {})
        retrieved_ids = trace.get("retrieved_doc_ids", []) or []
        citation_ids = trace.get("retrieved_citation_doc_ids", []) or []
        filter_applied = trace.get("citation_filter_applied", False)

        expected = set(q.get("expected_doc_ids", []))
        recall5 = bool(expected & set(retrieved_ids[:5]))
        recall10 = bool(expected & set(retrieved_ids[:10]))
        citation_hit = bool(expected & set(citation_ids))

        if recall5:
            n_recall5_hit += 1
        if recall10:
            n_recall10_hit += 1
        if citation_hit:
            n_citation_hit += 1
        if filter_applied:
            n_filter_applied += 1

        results.append({
            "id": q["id"],
            "scenario": q["scenario"],
            "question": q["question"],
            "expected_doc_ids": sorted(expected),
            "retrieved_doc_ids_top5": retrieved_ids[:5],
            "retrieved_doc_ids_top10": retrieved_ids[:10],
            "citation_doc_ids": citation_ids,
            "recall@5": recall5,
            "recall@10": recall10,
            "citation_hit": citation_hit,
            "citation_filter_applied": filter_applied,
            "rerank_used": trace.get("rerank_used", False),
            "query_variants_count": len(trace.get("query_variants", [])),
            "elapsed_sec": round(elapsed, 2),
        })
        print(
            f"  [{q['id']}] r5={int(recall5)} r10={int(recall10)} "
            f"cite={int(citation_hit)} filt={int(filter_applied)} "
            f"top5={retrieved_ids[:3]}{'...' if len(retrieved_ids) > 3 else ''} "
            f"({elapsed:.1f}s)"
        )

    n = len(questions)
    summary = {
        "variant": variant,
        "n_questions": n,
        "recall@5": round(n_recall5_hit / n, 4) if n else 0.0,
        "recall@10": round(n_recall10_hit / n, 4) if n else 0.0,
        "citation_hit_rate": round(n_citation_hit / n, 4) if n else 0.0,
        "citation_filter_applied_rate": round(n_filter_applied / n, 4) if n else 0.0,
        "avg_elapsed_sec": round(elapsed_total / n, 2) if n else 0.0,
    }
    return {"summary": summary, "per_question": results}


def write_report(variant: str, payload: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"eval_{variant}_{ts}.json"
    md_path = out_dir / f"eval_{variant}_{ts}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    s = payload["summary"]
    lines = [
        f"# Eval Tier 1 Report — variant={variant}",
        f"",
        f"- 时间: {ts}",
        f"- 题数: {s['n_questions']}",
        f"- **recall@5**: {s['recall@5']:.2%}",
        f"- **recall@10**: {s['recall@10']:.2%}",
        f"- **citation_hit_rate**: {s['citation_hit_rate']:.2%}",
        f"- citation_filter_applied_rate: {s['citation_filter_applied_rate']:.2%}",
        f"- 平均耗时: {s['avg_elapsed_sec']}s / 题",
        f"",
        f"## Per-question 明细",
        f"",
        f"| ID | scenario | r@5 | r@10 | cite | filt | retrieved_top3 |",
        f"|---|---|---|---|---|---|---|",
    ]
    for r in payload["per_question"]:
        if "error" in r:
            lines.append(f"| {r['id']} | (error) | - | - | - | - | {r['error'][:60]} |")
            continue
        top3 = ", ".join(r["retrieved_doc_ids_top5"][:3])
        lines.append(
            f"| {r['id']} | {r['scenario']} | "
            f"{'✅' if r['recall@5'] else '❌'} | "
            f"{'✅' if r['recall@10'] else '❌'} | "
            f"{'✅' if r['citation_hit'] else '❌'} | "
            f"{'Y' if r['citation_filter_applied'] else 'N'} | "
            f"{top3} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def write_diff_report(variant_payloads: dict[str, dict], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = out_dir / f"eval_diff_{ts}.md"

    variants = list(variant_payloads.keys())
    summaries = {v: variant_payloads[v]["summary"] for v in variants}

    lines = [
        f"# Eval Tier 1 — Variant Diff Report",
        f"",
        f"- 时间: {ts}",
        f"- 题数: {summaries[variants[0]]['n_questions']}",
        f"",
        f"## 聚合指标对比",
        f"",
        f"| 指标 | " + " | ".join(variants) + " |",
        f"|---|" + "|".join(["---"] * len(variants)) + "|",
    ]
    for metric in ["recall@5", "recall@10", "citation_hit_rate", "avg_elapsed_sec"]:
        row = f"| **{metric}** |"
        for v in variants:
            val = summaries[v][metric]
            if isinstance(val, float) and metric != "avg_elapsed_sec":
                row += f" {val:.2%} |"
            else:
                row += f" {val} |"
        lines.append(row)

    # 每题对比
    lines.extend(["", "## Per-question diff (recall@5)", "", "| ID | " + " | ".join(variants) + " |",
                  "|---|" + "|".join(["---"] * len(variants)) + "|"])
    qids = [r["id"] for r in variant_payloads[variants[0]]["per_question"]]
    for qid in qids:
        row = f"| {qid} |"
        for v in variants:
            r = next(r for r in variant_payloads[v]["per_question"] if r["id"] == qid)
            if "error" in r:
                row += " err |"
            else:
                row += f" {'✅' if r['recall@5'] else '❌'} |"
        lines.append(row)

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["baseline", "step3", "full", "all"],
                    default="full")
    ap.add_argument("--questions", default=str(PROJECT_ROOT / "eval" / "questions.jsonl"))
    ap.add_argument("--top-k", type=int, default=10,
                    help="ask() 的 top_k，influences recall@10 上限")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "eval" / "reports"
    questions = load_questions(Path(args.questions))
    print(f"[eval] loaded {len(questions)} questions from {args.questions}")

    if args.variant == "all":
        variant_payloads = {}
        for v in ["baseline", "step3", "full"]:
            print(f"\n========== variant={v} ==========")
            payload = run_one_variant(v, questions, top_k=args.top_k)
            jp, mp = write_report(v, payload, out_dir)
            print(f"  → {jp.name} / {mp.name}")
            print(f"  summary: {payload['summary']}")
            variant_payloads[v] = payload
        diff_path = write_diff_report(variant_payloads, out_dir)
        print(f"\n[eval] diff report: {diff_path}")
    else:
        print(f"\n========== variant={args.variant} ==========")
        payload = run_one_variant(args.variant, questions, top_k=args.top_k)
        jp, mp = write_report(args.variant, payload, out_dir)
        print(f"\n[eval] reports written: {jp}, {mp}")
        print(f"[eval] summary: {payload['summary']}")


if __name__ == "__main__":
    main()

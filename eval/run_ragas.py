"""
CrossBridge AI - Step 4b Tier 2 (RAGAS)
========================================
跑业界标准的 RAGAS 4 维评估：
  - faithfulness:       答案是否忠于检索的 context（不幻觉）
  - answer_relevancy:   答案与问题的相关性
  - context_precision:  检索到的 doc ID 有多少属于预期权威来源
  - context_recall:     预期权威来源有多少被检索到

跟 4a 用同一份 eval/questions.jsonl。faithfulness / answer_relevancy 用 LLM judge；
context_precision / context_recall 用 RAGAS 官方 ID-based metrics，对照 expected_doc_ids。

用法:
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  .venv/bin/python eval/run_ragas.py --variant full

输出:
  eval/reports/ragas_<variant>_<timestamp>.json
  eval/reports/ragas_<variant>_<timestamp>.md

成本估算: 24 题 × 2 个 LLM 指标 × ~3 调用 ≈ 150 次 Qwen chat ≈ ¥3-5 / variant
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from datetime import datetime
from pathlib import Path

# RAGAS 0.4.3 在 import 时硬依赖 langchain_community.chat_models.vertexai,
# 但 langchain-community>=0.2 已经把它移到 langchain_google_vertexai 独立包,
# 留下断链 import 让 ragas 启动就崩。我们不用 Vertex AI, 注入一个 stub 模块即可。
def _stub_vertexai_module():
    try:
        import langchain_community.chat_models.vertexai  # noqa
        return  # 已存在不动
    except Exception:
        pass
    stub = types.ModuleType("langchain_community.chat_models.vertexai")
    class _ChatVertexAIStub:  # ragas 只是 import, 不实际调用
        def __init__(self, *a, **kw): raise NotImplementedError("Vertex AI 不可用; 这是 RAGAS 兼容 stub")
    stub.ChatVertexAI = _ChatVertexAIStub
    sys.modules["langchain_community.chat_models.vertexai"] = stub
_stub_vertexai_module()

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


def filter_questions_by_ids(questions: list[dict], ids_csv: str | None) -> tuple[list[dict], str]:
    if not ids_csv:
        return questions, "full"
    requested = [item.strip() for item in ids_csv.split(",") if item.strip()]
    if not requested:
        return questions, "full"

    by_id = {q["id"]: q for q in questions}
    missing = [qid for qid in requested if qid not in by_id]
    if missing:
        raise RuntimeError(f"Unknown question IDs for --ids: {', '.join(missing)}")

    filtered = [by_id[qid] for qid in requested]
    label = "ids_" + "-".join(requested)
    safe_label = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in label)
    return filtered, safe_label


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _disable_baseline_features(rag) -> None:
    rag.retriever.bm25_index = None
    rag.retriever.reranker = None
    rag.bm25_index = None
    rag.reranker = None
    rag.retriever.mode = "simple"
    import rag_engine
    rag_engine.TRUSTED_TIERS_FOR_CITATION = frozenset(
        {"government", "regulator", "central_bank", "official_dev",
         "bank", "industry", "non_official", ""}
    )
    rag_engine.NON_CITABLE_DOCUMENT_TYPES = frozenset()


def _disable_citation_filter_only(rag) -> None:
    import rag_engine
    rag_engine.TRUSTED_TIERS_FOR_CITATION = frozenset(
        {"government", "regulator", "central_bank", "official_dev",
         "bank", "industry", "non_official", ""}
    )
    rag_engine.NON_CITABLE_DOCUMENT_TYPES = frozenset()


def collect_rag_outputs(variant: str, questions: list[dict]) -> list[dict]:
    """收集 (question, answer, contexts) 三元组。contexts 用真实 chunk content。"""
    for mod in list(sys.modules):
        if mod in ("rag_engine", "bm25_index", "reranker"):
            del sys.modules[mod]

    from rag_engine import CrossBridgeRAG  # noqa

    rag = CrossBridgeRAG(
        chunks_path=str(PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"),
        persist_directory=str(PROJECT_ROOT / "data" / "chroma"),
    )
    if variant == "baseline":
        _disable_baseline_features(rag)
    elif variant == "step3":
        _disable_citation_filter_only(rag)

    # Monkey-patch _format_output，让 eval 拿到实际喂给 LLM 的 context 和 doc ID。
    # citation docs 与 context-only docs 都会进入 prompt，因此两类都必须计入。
    original_format = rag._format_output
    def _format_with_contexts(state):
        result = original_format(state)
        prompt_docs = list(
            state.get("retrieved_for_citation", state.get("retrieved", []))
        ) + list(state.get("context_only", []))
        result["_contexts"] = [doc["content"] for doc, _ in prompt_docs]
        result["_context_ids"] = [
            doc.get("doc_id") or doc.get("id") for doc, _ in prompt_docs
        ]
        return result
    rag._format_output = _format_with_contexts
    rag.chain = rag._build_langchain_chain()

    rows = []
    failures = []
    max_output_retries = max(1, _env_int("RAG_OUTPUT_MAX_RETRIES", 3))
    retry_sleep_seconds = max(1, _env_int("RAG_OUTPUT_RETRY_SLEEP_SECONDS", 5))
    for q in questions:
        t0 = time.time()
        out = None
        last_error = None
        for attempt in range(1, max_output_retries + 1):
            try:
                out = rag.ask(q["question"], top_k=5, debug=True)
                break
            except Exception as e:
                last_error = e
                if attempt >= max_output_retries:
                    break
                print(
                    f"  [{q['id']}] retry {attempt}/{max_output_retries} "
                    f"after {type(e).__name__}: {e}"
                )
                time.sleep(retry_sleep_seconds * attempt)
        if out is None:
            print(
                f"  [{q['id']}] ERROR: {type(last_error).__name__}: {last_error}"
            )
            failures.append((q["id"], type(last_error).__name__, str(last_error)))
            continue
        elapsed = time.time() - t0
        rows.append({
            "id": q["id"],
            "scenario": q["scenario"],
            "question": q["question"],
            "answer": out.get("answer", ""),
            "contexts": out.get("_contexts", []),
            "context_ids": out.get("_context_ids", []),
            "reference_context_ids": q.get("expected_doc_ids", []),
            "elapsed_sec": round(elapsed, 2),
        })
        print(f"  [{q['id']}] ans={len(out.get('answer','')):4d}chars ctx={len(out.get('_contexts',[]))} ({elapsed:.1f}s)")
    if failures:
        failure_text = "; ".join(
            f"{qid}: {err_type}: {message}" for qid, err_type, message in failures
        )
        raise RuntimeError(
            "RAG output collection failed for one or more questions; "
            "refusing to write a partial cache. "
            + failure_text
        )
    if len(rows) != len(questions):
        raise RuntimeError(
            "RAG output collection produced an unexpected row count; "
            f"expected {len(questions)}, got {len(rows)}. Refusing to write cache."
        )
    return rows


def validate_scoring_rows(rows: list[dict]) -> None:
    required = {"question", "answer", "contexts", "context_ids", "reference_context_ids"}
    for row in rows:
        missing = sorted(required - set(row))
        if missing:
            raise RuntimeError(
                "RAGAS cache is stale and missing required fields "
                f"{missing} for row {row.get('id', '?')}. "
                "Re-run without --use-cache to collect four-metric inputs."
            )


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def load_cached_rag_rows(
    cache_path: Path,
    fallback_full_cache_path: Path | None,
    question_ids: list[str],
) -> list[dict] | None:
    """Load exact subset cache, or slice the full cache for API-free subset checks."""
    def _validate_cache_rows(rows: list[dict], source_path: Path) -> None:
        if not isinstance(rows, list):
            raise RuntimeError(f"RAG output cache is not a row list: {source_path}")
        by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
        missing = [qid for qid in question_ids if qid not in by_id]
        extra = sorted(set(by_id) - set(question_ids))
        if missing or extra or len(rows) != len(question_ids):
            details = []
            if missing:
                details.append("missing IDs: " + ", ".join(missing))
            if extra:
                details.append("extra IDs: " + ", ".join(extra))
            if len(rows) != len(question_ids):
                details.append(f"row count {len(rows)} != expected {len(question_ids)}")
            raise RuntimeError(
                f"RAG output cache does not match requested subset: {source_path}; "
                + "; ".join(details)
            )
        validate_scoring_rows(rows)

    if cache_path.exists():
        print(f"[ragas] reusing cached RAG outputs from {cache_path}")
        rows = json.loads(cache_path.read_text(encoding="utf-8"))
        _validate_cache_rows(rows, cache_path)
        return rows

    if fallback_full_cache_path and fallback_full_cache_path.exists():
        print(
            "[ragas] subset cache missing; slicing full cached RAG outputs from "
            f"{fallback_full_cache_path}"
        )
        full_rows = json.loads(fallback_full_cache_path.read_text(encoding="utf-8"))
        by_id = {row.get("id"): row for row in full_rows}
        missing = [qid for qid in question_ids if qid not in by_id]
        if missing:
            raise RuntimeError(
                "Full RAG output cache is missing requested IDs for --use-cache: "
                + ", ".join(missing)
            )
        rows = [by_id[qid] for qid in question_ids]
        _validate_cache_rows(rows, fallback_full_cache_path)
        write_json_atomic(cache_path, rows)
        print(f"[ragas] wrote sliced subset cache to {cache_path}")
        return rows

    return None


def write_json_atomic(path: Path, payload) -> None:
    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def _minimal_citation_source(context_ids: list[str]) -> list[tuple[dict, float]]:
    """Build enough citation metadata for deterministic template regeneration."""
    return [
        (
            {
                "id": doc_id,
                "doc_id": doc_id,
                "title": doc_id,
                "source_name": doc_id,
                "source_url": "",
                "region": "",
            },
            1.0,
        )
        for doc_id in context_ids
        if doc_id
    ]


def regenerate_template_answers_from_cache(rows: list[dict]) -> list[dict]:
    """Regenerate deterministic RAG answers from cached retrieval rows.

    This is intentionally API-free. It is useful when retrieval/context
    selection has already been cached but live model credentials are unavailable
    and the changed behavior is a deterministic template path.
    """
    import rag_engine

    builders = [
        ("exact_identifier_template", rag_engine._build_exact_identifier_answer),
        ("fps_limit_template", rag_engine._build_fps_limit_answer),
        ("sme_collateral_template", rag_engine._build_sme_collateral_answer),
        ("sme_loan_docs_template", rag_engine._build_sme_loan_docs_answer),
        ("sfgs_amount_docs_template", rag_engine._build_sfgs_amount_docs_answer),
        (
            "china_vietnam_supplier_payment_template",
            rag_engine._build_china_vietnam_supplier_payment_answer,
        ),
    ]

    regenerated = []
    for row in rows:
        item = dict(row)
        citation_source = _minimal_citation_source([
            str(doc_id) for doc_id in item.get("context_ids", []) if doc_id
        ])
        generation_mode = None
        answer = ""
        for mode, builder in builders:
            answer = builder(item["question"], citation_source, "zh")
            if answer:
                generation_mode = mode
                break
        if not answer:
            raise RuntimeError(
                "No deterministic template matched cached row "
                f"{item.get('id')}; cannot regenerate without model credentials."
            )
        item["answer"] = answer
        item["answer_generation_mode"] = generation_mode
        item["template_regenerated_from_cache"] = True
        regenerated.append(item)
    validate_scoring_rows(regenerated)
    return regenerated


def run_id_context_scoring(rows: list[dict]) -> dict:
    """Score ID-based context precision/recall without an LLM judge.

    RAGAS IDBasedContextPrecision/Recall operates on document IDs, not text
    embeddings. Keeping this path API-free makes each retrieval/context
    selection experiment quickly checkable before spending judge calls.
    """
    validate_scoring_rows(rows)

    precision_scores: list[float] = []
    recall_scores: list[float] = []
    for row in rows:
        retrieved = _unique_keep_order([
            str(item) for item in row.get("context_ids", []) if item
        ])
        expected = {
            str(item) for item in row.get("reference_context_ids", []) if item
        }
        hits = set(retrieved) & expected

        precision_scores.append(
            (len(hits) / len(retrieved)) if retrieved else 0.0
        )
        recall_scores.append(
            (len(hits) / len(expected)) if expected else 0.0
        )

    return {
        "id_based_context_precision": precision_scores,
        "id_based_context_recall": recall_scores,
    }


def run_ragas_scoring(rows: list[dict]) -> dict:
    """调 RAGAS 0.4 API 给每行打 metric 分。

    RAGAS 0.4 关键变化：
      - 数据结构改成 EvaluationDataset + SingleTurnSample
      - 列名改成 user_input / response / retrieved_contexts（不是 question/answer/contexts）
      - 老 datasets.Dataset 传进去会被静默丢弃 → samples 为空 → IndexError
    """
    validate_scoring_rows(rows)

    from ragas import EvaluationDataset, SingleTurnSample
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        IDBasedContextPrecision,
        IDBasedContextRecall,
        answer_relevancy,
        faithfulness,
    )
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.run_config import RunConfig
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    run_config = RunConfig(
        timeout=_env_int("RAGAS_JUDGE_TIMEOUT_SECONDS", 300),
        max_retries=_env_int("RAGAS_JUDGE_MAX_RETRIES", 3),
        max_workers=_env_int("RAGAS_JUDGE_MAX_WORKERS", 4),
    )
    llm = LangchainLLMWrapper(ChatOpenAI(
        model=os.environ.get("QWEN_MODEL", "qwen-plus"),
        openai_api_key=os.environ["DASHSCOPE_API_KEY"],
        openai_api_base=os.environ.get(
            "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        temperature=0,
    ))
    embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
        model=os.environ.get("QWEN_EMBEDDING_MODEL", "text-embedding-v4"),
        openai_api_key=os.environ["DASHSCOPE_API_KEY"],
        openai_api_base=os.environ.get(
            "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        check_embedding_ctx_length=False,
        chunk_size=10,
    ))

    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"] or [""],
            retrieved_context_ids=r["context_ids"],
            reference_context_ids=r["reference_context_ids"],
        )
        for r in rows
    ]
    ds = EvaluationDataset(samples=samples)

    metrics = [
        faithfulness,
        answer_relevancy,
        IDBasedContextPrecision(),
        IDBasedContextRecall(),
    ]

    result = ragas_evaluate(
        ds,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        run_config=run_config,
    )
    # 用 to_pandas() 抽 metric 列
    df = result.to_pandas()
    out: dict = {}
    skip_cols = {"question", "answer", "contexts", "user_input", "response",
                 "retrieved_contexts", "retrieved_context_ids",
                 "reference_context_ids", "reference", "rubrics"}
    for col in df.columns:
        if col in skip_cols:
            continue
        out[col] = [None if (v is None or (isinstance(v, float) and v != v)) else float(v)
                    for v in df[col].tolist()]
    return out


def write_ragas_report(variant: str, rows: list[dict], ragas_scores: dict,
                       out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"ragas_{variant}_{ts}.json"
    md_path = out_dir / f"ragas_{variant}_{ts}.md"

    # 防止 RAGAS 中间任何 metric output 解析失败导致 None — write 阶段不再二次抛
    def _fmt(v):
        if v is None:
            return None
        try:
            f = float(v)
            if f != f:  # NaN
                return None
            return round(f, 4)
        except (TypeError, ValueError):
            return None

    per_q = []
    for i, r in enumerate(rows):
        item = dict(r)
        for metric, scores in ragas_scores.items():
            if i < len(scores):
                item[metric] = _fmt(scores[i])
        per_q.append(item)

    summary = {"variant": variant, "n_questions": len(rows)}
    for metric, scores in ragas_scores.items():
        non_null = [_fmt(s) for s in scores]
        non_null = [v for v in non_null if v is not None]
        if non_null:
            summary[f"{metric}_mean"] = round(sum(non_null) / len(non_null), 4)
            summary[f"{metric}_n_valid"] = len(non_null)
            summary[f"{metric}_n_failed"] = len(scores) - len(non_null)

    payload = {"summary": summary, "per_question": per_q}
    write_json_atomic(json_path, payload)

    metric_names = sorted(ragas_scores.keys())
    lines = [
        f"# RAGAS Tier 2 Report — variant={variant}",
        f"",
        f"- 时间: {ts}",
        f"- 题数: {len(rows)}",
        f"",
        "## 聚合指标",
        "",
        "| 指标 | 均值 |",
        "|---|---|",
    ]
    for m in metric_names:
        v = summary.get(f"{m}_mean", "-")
        lines.append(f"| **{m}** | {v} |")
    lines.extend(["", "## Per-question", "",
                  "| ID | scenario | " + " | ".join(metric_names) + " |",
                  "|---|---|" + "|".join(["---"] * len(metric_names)) + "|"])
    for r in per_q:
        cells = [r["id"], r["scenario"]] + [
            f"{r.get(m, '-')}" if isinstance(r.get(m), float) else str(r.get(m, '-'))
            for m in metric_names
        ]
        lines.append("| " + " | ".join(cells) + " |")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["baseline", "step3", "full"], default="full")
    ap.add_argument("--questions", default=str(PROJECT_ROOT / "eval" / "questions.jsonl"))
    ap.add_argument("--ids", default=None,
                    help="Comma-separated question IDs for weak-sample subset runs, e.g. q12,q14,q16")
    ap.add_argument("--use-cache", action="store_true",
                    help="如果存在 rag_outputs_<variant>.json 缓存就复用，跳过 ~10 min 收集")
    ap.add_argument("--collect-only", action="store_true",
                    help="只收集 RAG 输出存缓存，不调 RAGAS（用来避开 DashScope 配额时调试）")
    ap.add_argument("--id-only", action="store_true",
                    help="只计算 ID-based context precision/recall，不调用 RAGAS LLM judge")
    ap.add_argument("--regenerate-template-answers", action="store_true",
                    help="从已缓存 retrieval rows 重新生成 deterministic template answers，不调用模型")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "eval" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    questions = load_questions(Path(args.questions))
    questions, subset_label = filter_questions_by_ids(questions, args.ids)
    report_variant = args.variant if subset_label == "full" else f"{args.variant}_{subset_label}"
    cache_path = out_dir / f"rag_outputs_{report_variant}.json"
    print(
        f"[ragas] loaded {len(questions)} questions, variant={args.variant}, "
        f"subset={subset_label}"
    )

    rows = None
    if args.use_cache:
        full_cache_path = None
        if subset_label != "full":
            full_cache_path = out_dir / f"rag_outputs_{args.variant}.json"
        rows = load_cached_rag_rows(
            cache_path,
            full_cache_path,
            [q["id"] for q in questions],
        )

    if rows is None:
        if args.regenerate_template_answers:
            raise RuntimeError(
                "--regenerate-template-answers requires --use-cache with an "
                "existing RAG output cache; it does not collect retrieval rows."
            )
        print("[ragas] collecting RAG outputs ...")
        rows = collect_rag_outputs(args.variant, questions)
        write_json_atomic(cache_path, rows)
        print(f"[ragas] cached {len(rows)} rows to {cache_path}")

    if args.regenerate_template_answers:
        print("[ragas] regenerating deterministic template answers from cached rows ...")
        rows = regenerate_template_answers_from_cache(rows)
        report_variant = f"{report_variant}_template_answers"
        cache_path = out_dir / f"rag_outputs_{report_variant}.json"
        write_json_atomic(cache_path, rows)
        print(f"[ragas] cached template-regenerated rows to {cache_path}")

    if args.collect_only:
        print("[ragas] --collect-only 模式，跳过 RAGAS 打分")
        return

    if args.id_only:
        print(f"[ragas] running API-free ID context scoring on {len(rows)} rows ...")
        scores = run_id_context_scoring(rows)
        id_report_variant = f"{report_variant}_id_only"
        scores_cache = out_dir / f"ragas_scores_{id_report_variant}.json"
        write_json_atomic(scores_cache, scores)
        print(f"[ragas] ID scores cached to {scores_cache}")
        jp, mp = write_ragas_report(id_report_variant, rows, scores, out_dir)
        print(f"[ragas] ID-only reports: {jp}, {mp}")
        return

    print(f"[ragas] running RAGAS scoring on {len(rows)} rows ...")
    print(f"        预计 {len(rows) * 6}-{len(rows) * 10} 次 LLM 调用，~3-5 分钟")
    print(
        "        judge config: "
        f"timeout={_env_int('RAGAS_JUDGE_TIMEOUT_SECONDS', 300)}s "
        f"retries={_env_int('RAGAS_JUDGE_MAX_RETRIES', 3)} "
        f"workers={_env_int('RAGAS_JUDGE_MAX_WORKERS', 4)}"
    )

    scores = run_ragas_scoring(rows)

    # 落盘 raw scores 立即（即使后续 write_ragas_report 挂掉也不丢钱）
    scores_cache = out_dir / f"ragas_scores_{report_variant}.json"
    write_json_atomic(scores_cache, scores)
    print(f"[ragas] raw scores cached to {scores_cache}")

    jp, mp = write_ragas_report(report_variant, rows, scores, out_dir)
    print(f"[ragas] reports: {jp}, {mp}")


if __name__ == "__main__":
    main()

"""
CrossBridge AI - Step 4b Tier 2 (RAGAS)
========================================
跑业界标准的 RAGAS 4 维评估，不需要 ground truth（LLM-as-judge）：
  - faithfulness:       答案是否忠于检索的 context（不幻觉）
  - answer_relevancy:   答案与问题的相关性
  - context_precision:  context 排序是否合理（相关的在前）

跟 4a 用同一份 eval/questions.jsonl，但只用 question + answer + context。

用法:
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  .venv/bin/python eval/run_ragas.py --variant full

输出:
  eval/reports/ragas_<variant>_<timestamp>.json
  eval/reports/ragas_<variant>_<timestamp>.md

成本估算: 24 题 × 3 指标 × ~3 LLM 调用 ≈ 200 次 Qwen chat ≈ ¥3-5 / variant
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

    # Monkey-patch _format_output 让它输出真实 contexts 的 content（不是 title）
    original_format = rag._format_output
    def _format_with_contexts(state):
        result = original_format(state)
        result["_contexts"] = [
            doc["content"] for doc, _ in state.get("retrieved_for_citation", state.get("retrieved", []))
        ]
        return result
    rag._format_output = _format_with_contexts
    rag.chain = rag._build_langchain_chain()

    rows = []
    for q in questions:
        t0 = time.time()
        try:
            out = rag.ask(q["question"], top_k=5, debug=True)
        except Exception as e:
            print(f"  [{q['id']}] ERROR: {type(e).__name__}: {e}")
            continue
        elapsed = time.time() - t0
        rows.append({
            "id": q["id"],
            "scenario": q["scenario"],
            "question": q["question"],
            "answer": out.get("answer", ""),
            "contexts": out.get("_contexts", []),
            "elapsed_sec": round(elapsed, 2),
        })
        print(f"  [{q['id']}] ans={len(out.get('answer','')):4d}chars ctx={len(out.get('_contexts',[]))} ({elapsed:.1f}s)")
    return rows


def run_ragas_scoring(rows: list[dict]) -> dict:
    """调 RAGAS 0.4 API 给每行打 metric 分。

    RAGAS 0.4 关键变化：
      - 数据结构改成 EvaluationDataset + SingleTurnSample
      - 列名改成 user_input / response / retrieved_contexts（不是 question/answer/contexts）
      - 老 datasets.Dataset 传进去会被静默丢弃 → samples 为空 → IndexError
    """
    from ragas import EvaluationDataset, SingleTurnSample
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import faithfulness, answer_relevancy
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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
        chunk_size=10,
    ))

    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"] or [""],
        )
        for r in rows
    ]
    ds = EvaluationDataset(samples=samples)

    metrics = [faithfulness, answer_relevancy]

    result = ragas_evaluate(ds, metrics=metrics, llm=llm, embeddings=embeddings)
    # 用 to_pandas() 抽 metric 列
    df = result.to_pandas()
    out: dict = {}
    skip_cols = {"question", "answer", "contexts", "user_input", "response",
                 "retrieved_contexts", "reference", "rubrics"}
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
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

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
    ap.add_argument("--use-cache", action="store_true",
                    help="如果存在 rag_outputs_<variant>.json 缓存就复用，跳过 ~10 min 收集")
    ap.add_argument("--collect-only", action="store_true",
                    help="只收集 RAG 输出存缓存，不调 RAGAS（用来避开 DashScope 配额时调试）")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "eval" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / f"rag_outputs_{args.variant}.json"

    questions = load_questions(Path(args.questions))
    print(f"[ragas] loaded {len(questions)} questions, variant={args.variant}")

    if args.use_cache and cache_path.exists():
        print(f"[ragas] reusing cached RAG outputs from {cache_path}")
        rows = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        print("[ragas] collecting RAG outputs ...")
        rows = collect_rag_outputs(args.variant, questions)
        cache_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[ragas] cached {len(rows)} rows to {cache_path}")

    if args.collect_only:
        print("[ragas] --collect-only 模式，跳过 RAGAS 打分")
        return

    print(f"[ragas] running RAGAS scoring on {len(rows)} rows ...")
    print(f"        预计 {len(rows) * 6}-{len(rows) * 10} 次 LLM 调用，~3-5 分钟")

    scores = run_ragas_scoring(rows)

    # 落盘 raw scores 立即（即使后续 write_ragas_report 挂掉也不丢钱）
    scores_cache = out_dir / f"ragas_scores_{args.variant}.json"
    scores_cache.write_text(json.dumps(scores, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    print(f"[ragas] raw scores cached to {scores_cache}")

    jp, mp = write_ragas_report(args.variant, rows, scores, out_dir)
    print(f"[ragas] reports: {jp}, {mp}")


if __name__ == "__main__":
    main()

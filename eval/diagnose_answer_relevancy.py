"""
CrossBridge AI - RAGAS answer_relevancy diagnostic
==================================================

This script explains why Ragas answer_relevancy scores a cached RAG answer the
way it does. It uses the same Ragas ResponseRelevancePrompt and scoring formula:

1. generate N questions from the answer
2. mark each generated output as noncommittal or committal
3. embed generated questions and the original user question
4. score = mean cosine similarity * int(not all_noncommittal)

Usage:
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  .venv/bin/python eval/diagnose_answer_relevancy.py \
    --rows eval/reports/rag_outputs_full_ids_q04-q19-q22_template_answers.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import numpy as np


def _stub_vertexai_module() -> None:
    try:
        import langchain_community.chat_models.vertexai  # noqa
        return
    except Exception:
        pass
    stub = types.ModuleType("langchain_community.chat_models.vertexai")

    class _ChatVertexAIStub:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Vertex AI is unavailable; RAGAS compatibility stub")

    stub.ChatVertexAI = _ChatVertexAIStub
    sys.modules["langchain_community.chat_models.vertexai"] = stub


_stub_vertexai_module()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "eval" / "reports"


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _require_env() -> None:
    missing = [
        name
        for name in ("DASHSCOPE_API_KEY", "LANGSMITH_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Export them through a secure local mechanism; do not write API keys into files."
        )


def _load_rows(path: Path, ids_csv: str | None) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise RuntimeError(f"Rows file must contain a JSON list: {path}")

    if ids_csv:
        requested = [item.strip() for item in ids_csv.split(",") if item.strip()]
        by_id = {row.get("id"): row for row in rows}
        missing = [qid for qid in requested if qid not in by_id]
        if missing:
            raise RuntimeError(f"Rows file is missing requested IDs: {', '.join(missing)}")
        rows = [by_id[qid] for qid in requested]

    required = {"id", "question", "answer"}
    for row in rows:
        missing = sorted(required - set(row))
        if missing:
            raise RuntimeError(
                f"Rows file is missing fields {missing} for row {row.get('id', '?')}"
            )
    return rows


def _make_llm_and_embeddings():
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.run_config import RunConfig

    run_config = RunConfig(
        timeout=_env_int("RAGAS_JUDGE_TIMEOUT_SECONDS", 300),
        max_retries=_env_int("RAGAS_JUDGE_MAX_RETRIES", 3),
        max_workers=_env_int("RAGAS_JUDGE_MAX_WORKERS", 2),
    )
    base_url = os.environ.get(
        "QWEN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    llm = LangchainLLMWrapper(
        ChatOpenAI(
            model=os.environ.get("QWEN_MODEL", "qwen-plus"),
            openai_api_key=os.environ["DASHSCOPE_API_KEY"],
            openai_api_base=base_url,
            temperature=0,
        ),
        run_config=run_config,
    )
    embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(
            model=os.environ.get("QWEN_EMBEDDING_MODEL", "text-embedding-v4"),
            openai_api_key=os.environ["DASHSCOPE_API_KEY"],
            openai_api_base=base_url,
            check_embedding_ctx_length=False,
            chunk_size=10,
        ),
        run_config=run_config,
    )
    return llm, embeddings


def _cosine_scores(embeddings, question: str, generated_questions: list[str]) -> list[float]:
    question_vec = np.asarray(embeddings.embed_query(question)).reshape(1, -1)
    gen_question_vec = np.asarray(
        embeddings.embed_documents(generated_questions)
    ).reshape(len(generated_questions), -1)
    norm = np.linalg.norm(gen_question_vec, axis=1) * np.linalg.norm(question_vec, axis=1)
    scores = (
        np.dot(gen_question_vec, question_vec.T).reshape(-1,) / norm
    )
    return [float(score) for score in scores]


async def _diagnose_row(row: dict, llm, embeddings, strictness: int) -> dict:
    from ragas.metrics._answer_relevance import (
        ResponseRelevanceInput,
        ResponseRelevancePrompt,
    )

    prompt = ResponseRelevancePrompt()
    responses = await prompt.generate_multiple(
        data=ResponseRelevanceInput(response=row["answer"]),
        llm=llm,
        n=strictness,
        temperature=0,
        callbacks=[],
    )
    generated = [
        {
            "question": response.question,
            "noncommittal": int(response.noncommittal),
        }
        for response in responses
    ]
    generated_questions = [item["question"] for item in generated]
    all_noncommittal = all(item["noncommittal"] for item in generated)
    if all(question == "" for question in generated_questions):
        cosine_scores: list[float] = []
        mean_similarity = None
        final_score = None
    else:
        cosine_scores = _cosine_scores(embeddings, row["question"], generated_questions)
        mean_similarity = float(sum(cosine_scores) / len(cosine_scores))
        final_score = mean_similarity * int(not all_noncommittal)

    return {
        "id": row["id"],
        "scenario": row.get("scenario"),
        "question": row["question"],
        "answer_generation_mode": row.get("answer_generation_mode"),
        "answer_length_chars": len(row.get("answer", "")),
        "generated_questions": generated,
        "all_noncommittal": bool(all_noncommittal),
        "cosine_scores": cosine_scores,
        "mean_similarity": mean_similarity,
        "answer_relevancy_formula_score": final_score,
    }


async def _diagnose(rows: list[dict], strictness: int) -> list[dict]:
    llm, embeddings = _make_llm_and_embeddings()
    results = []
    for row in rows:
        print(f"[diagnose] {row['id']} answer_len={len(row.get('answer', ''))}")
        results.append(await _diagnose_row(row, llm, embeddings, strictness))
    return results


def _write_reports(results: list[dict], label: str) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORT_DIR / f"answer_relevancy_diagnostic_{label}_{ts}.json"
    md_path = REPORT_DIR / f"answer_relevancy_diagnostic_{label}_{ts}.md"
    payload = {
        "summary": {
            "label": label,
            "n_rows": len(results),
            "n_all_noncommittal": sum(1 for row in results if row["all_noncommittal"]),
        },
        "rows": results,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Answer Relevancy Diagnostic - {label}",
        "",
        f"- Rows: {len(results)}",
        f"- All-noncommittal rows: {payload['summary']['n_all_noncommittal']}",
        "",
        "| ID | mode | all_noncommittal | mean_similarity | formula_score | generated questions |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in results:
        generated = "<br>".join(
            f"{item['question']} (noncommittal={item['noncommittal']})"
            for item in row["generated_questions"]
        )
        lines.append(
            "| "
            + " | ".join([
                str(row["id"]),
                str(row.get("answer_generation_mode") or ""),
                str(row["all_noncommittal"]),
                "-" if row["mean_similarity"] is None else f"{row['mean_similarity']:.4f}",
                "-" if row["answer_relevancy_formula_score"] is None else f"{row['answer_relevancy_formula_score']:.4f}",
                generated.replace("|", "\\|"),
            ])
            + " |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True, help="Path to cached rag_outputs*.json rows")
    ap.add_argument("--ids", default=None, help="Optional comma-separated row IDs")
    ap.add_argument("--label", default=None, help="Report label; defaults to rows filename stem")
    ap.add_argument("--strictness", type=int, default=3, help="Generated questions per answer")
    args = ap.parse_args()

    _require_env()
    rows_path = Path(args.rows)
    rows = _load_rows(rows_path, args.ids)
    label = args.label or rows_path.stem
    safe_label = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in label)
    results = asyncio.run(_diagnose(rows, args.strictness))
    json_path, md_path = _write_reports(results, safe_label)
    print(f"[diagnose] reports: {json_path}, {md_path}")


if __name__ == "__main__":
    main()

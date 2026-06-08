"""
CrossBridge AI - LangSmith latency benchmark
============================================
Runs representative RAG questions repeatedly, then queries LangSmith back for
the uploaded root traces and child spans. LangSmith trace duration is the
performance source of truth; local wall-clock duration is diagnostic only.

Usage:
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  export LANGSMITH_TRACING=true
  export LANGSMITH_PROJECT=CrossBridge-RAG-Latency-Optimization
  .venv/bin/python eval/run_latency_benchmark.py --label baseline

For a cheaper diagnostic smoke before an acceptance run:
  .venv/bin/python eval/run_latency_benchmark.py \
    --label smoke --question-id q01 --repetitions 1
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "files"))

MIN_ACCEPTANCE_RUNS = 5
TARGET_P95_SECONDS = 35.0
TRACE_TAG = "latency-benchmark"


def load_questions(path: Path, question_ids: set[str] | None = None) -> list[dict]:
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            question = json.loads(line)
            if question_ids and question["id"] not in question_ids:
                continue
            questions.append(question)
    return questions


def percentile(values: Iterable[float], percentile_value: float) -> float | None:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    rank = max(1, math.ceil((percentile_value / 100.0) * len(ordered)))
    return round(ordered[rank - 1], 4)


def run_duration_seconds(run: Any) -> float | None:
    if run.start_time is None or run.end_time is None:
        return None
    return round(max(0.0, (run.end_time - run.start_time).total_seconds()), 4)


def wait_for_tagged_root_runs(
    client: Any,
    *,
    project_name: str,
    benchmark_tag: str,
    started_at: datetime,
    expected_count: int,
    timeout_seconds: float,
) -> list[Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        roots = list(
            client.list_runs(
                project_name=project_name,
                is_root=True,
                start_time=started_at,
                filter=f'has(tags, "{benchmark_tag}")',
            )
        )
        completed_roots = [run for run in roots if run.end_time is not None]
        if len(completed_roots) >= expected_count:
            return sorted(completed_roots, key=lambda run: run.start_time)
        if time.monotonic() >= deadline:
            raise RuntimeError(
                "LangSmith trace upload did not become queryable before timeout: "
                f"expected={expected_count}, found={len(completed_roots)}, "
                f"project={project_name}, tag={benchmark_tag}"
            )
        time.sleep(2.0)


def load_trace_spans(
    client: Any,
    *,
    project_name: str,
    benchmark_tag: str,
    started_at: datetime,
    root_runs: list[Any],
) -> list[Any]:
    root_trace_ids = {run.trace_id for run in root_runs}
    spans = client.list_runs(
        project_name=project_name,
        start_time=started_at,
        trace_filter=f'has(tags, "{benchmark_tag}")',
    )
    return [span for span in spans if span.trace_id in root_trace_ids]


def summarize_spans(spans: list[Any], root_runs: list[Any]) -> list[dict]:
    root_ids = {run.id for run in root_runs}
    durations_by_name: dict[str, list[float]] = defaultdict(list)
    for span in spans:
        if span.id in root_ids:
            continue
        duration = run_duration_seconds(span)
        if duration is None:
            continue
        durations_by_name[span.name].append(duration)

    rows = []
    for name, durations in durations_by_name.items():
        rows.append(
            {
                "name": name,
                "count": len(durations),
                "total_sec": round(sum(durations), 4),
                "avg_sec": round(sum(durations) / len(durations), 4),
                "p95_sec": percentile(durations, 95),
                "max_sec": round(max(durations), 4),
            }
        )
    return sorted(rows, key=lambda row: row["total_sec"], reverse=True)


def build_report_payload(
    *,
    benchmark_id: str,
    label: str,
    project_name: str,
    repetitions: int,
    target_p95_seconds: float,
    local_rows: list[dict],
    root_runs: list[Any],
    spans: list[Any],
    client: Any,
) -> dict:
    local_by_key = {
        (row["question_id"], row["iteration"]): row for row in local_rows
    }
    trace_rows = []
    for run in root_runs:
        metadata = run.metadata or {}
        question_id = str(metadata.get("benchmark_question_id", "unknown"))
        iteration = int(metadata.get("benchmark_iteration", 0))
        duration = run_duration_seconds(run)
        if duration is None:
            continue
        local = local_by_key.get((question_id, iteration), {})
        trace_rows.append(
            {
                "question_id": question_id,
                "iteration": iteration,
                "trace_latency_sec": duration,
                "local_wall_clock_sec": local.get("local_wall_clock_sec"),
                "trace_id": str(run.trace_id),
                "run_id": str(run.id),
                "trace_url": client.get_run_url(run=run, project_name=project_name),
                "error": run.error,
            }
        )

    by_question: dict[str, list[float]] = defaultdict(list)
    for row in trace_rows:
        by_question[row["question_id"]].append(row["trace_latency_sec"])
    per_question = []
    for question_id, latencies in sorted(by_question.items()):
        per_question.append(
            {
                "question_id": question_id,
                "runs": len(latencies),
                "avg_sec": round(sum(latencies) / len(latencies), 4),
                "p50_sec": percentile(latencies, 50),
                "p95_sec": percentile(latencies, 95),
                "max_sec": round(max(latencies), 4),
                "meets_target": bool(
                    (percentile(latencies, 95) or float("inf"))
                    <= target_p95_seconds
                ),
            }
        )

    all_latencies = [row["trace_latency_sec"] for row in trace_rows]
    overall_p95 = percentile(all_latencies, 95)
    trace_errors = [row for row in trace_rows if row["error"]]
    acceptance_ready = bool(
        per_question
        and len(trace_rows) >= MIN_ACCEPTANCE_RUNS
        and len(per_question) * repetitions == len(trace_rows)
        and not trace_errors
    )
    meets_target = bool(
        acceptance_ready
        and overall_p95 is not None
        and overall_p95 <= target_p95_seconds
        and all(row["meets_target"] for row in per_question)
    )

    return {
        "summary": {
            "benchmark_id": benchmark_id,
            "label": label,
            "langsmith_project": project_name,
            "trace_source_of_truth": "LangSmith root trace duration",
            "questions": len(per_question),
            "requested_repetitions_per_question": repetitions,
            "minimum_acceptance_runs": MIN_ACCEPTANCE_RUNS,
            "trace_runs": len(trace_rows),
            "trace_errors": len(trace_errors),
            "target_p95_sec": target_p95_seconds,
            "overall_avg_sec": (
                round(sum(all_latencies) / len(all_latencies), 4)
                if all_latencies
                else None
            ),
            "overall_p50_sec": percentile(all_latencies, 50),
            "overall_p95_sec": overall_p95,
            "acceptance_ready": acceptance_ready,
            "meets_target": meets_target,
        },
        "per_question": per_question,
        "slowest_spans_by_total_time": summarize_spans(spans, root_runs)[:20],
        "runs": trace_rows,
    }


def write_report(payload: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = payload["summary"]["label"]
    json_path = out_dir / f"latency_{label}_{ts}.json"
    md_path = out_dir / f"latency_{label}_{ts}.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = payload["summary"]
    lines = [
        f"# LangSmith Latency Benchmark - {label}",
        "",
        f"- Benchmark ID: `{summary['benchmark_id']}`",
        f"- LangSmith project: `{summary['langsmith_project']}`",
        f"- Source of truth: {summary['trace_source_of_truth']}",
        f"- Trace runs: {summary['trace_runs']}",
        f"- Overall p95: {summary['overall_p95_sec']}s",
        f"- Target p95: <= {summary['target_p95_sec']}s",
        f"- Acceptance-ready: {summary['acceptance_ready']}",
        f"- Meets target: {summary['meets_target']}",
        "",
        "## Per Question",
        "",
        "| ID | runs | avg | p50 | p95 | max | target |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["per_question"]:
        lines.append(
            f"| {row['question_id']} | {row['runs']} | {row['avg_sec']}s | "
            f"{row['p50_sec']}s | {row['p95_sec']}s | {row['max_sec']}s | "
            f"{'PASS' if row['meets_target'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## Slowest Spans",
            "",
            "| span | calls | total | avg | p95 | max |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["slowest_spans_by_total_time"]:
        lines.append(
            f"| {row['name']} | {row['count']} | {row['total_sec']}s | "
            f"{row['avg_sec']}s | {row['p95_sec']}s | {row['max_sec']}s |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def require_runtime_config() -> None:
    missing = [
        name
        for name in ("DASHSCOPE_API_KEY", "LANGSMITH_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    os.environ.setdefault("LANGSMITH_TRACING", "true")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="baseline")
    parser.add_argument(
        "--questions", default=str(PROJECT_ROOT / "eval" / "questions.jsonl")
    )
    parser.add_argument("--question-id", action="append", default=[])
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--project",
        default=os.environ.get(
            "LANGSMITH_PROJECT", "CrossBridge-RAG-Latency-Optimization"
        ),
    )
    parser.add_argument("--trace-wait-timeout", type=float, default=60.0)
    parser.add_argument("--target-p95", type=float, default=TARGET_P95_SECONDS)
    parser.add_argument(
        "--out-dir", default=str(PROJECT_ROOT / "eval" / "reports")
    )
    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("--repetitions must be >= 1")
    require_runtime_config()

    selected_ids = set(args.question_id) or None
    questions = load_questions(Path(args.questions), selected_ids)
    if not questions:
        parser.error("no questions selected")

    benchmark_id = (
        f"{args.label}-{datetime.now().strftime('%Y%m%dT%H%M%S')}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    benchmark_tag = f"{TRACE_TAG}:{benchmark_id}"
    started_at = datetime.now(timezone.utc)
    local_rows = []

    from rag_engine import CrossBridgeRAG

    rag = CrossBridgeRAG(
        chunks_path=str(PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"),
        persist_directory=str(PROJECT_ROOT / "data" / "chroma"),
    )
    print(
        f"[latency] benchmark={benchmark_id} questions={len(questions)} "
        f"repetitions={args.repetitions}"
    )
    for question in questions:
        for iteration in range(1, args.repetitions + 1):
            t0 = time.perf_counter()
            rag.ask(
                question["question"],
                top_k=args.top_k,
                debug=False,
                trace_tags=[TRACE_TAG, benchmark_tag],
                trace_metadata={
                    "benchmark_id": benchmark_id,
                    "benchmark_label": args.label,
                    "benchmark_question_id": question["id"],
                    "benchmark_iteration": iteration,
                },
            )
            elapsed = round(time.perf_counter() - t0, 4)
            local_rows.append(
                {
                    "question_id": question["id"],
                    "iteration": iteration,
                    "local_wall_clock_sec": elapsed,
                }
            )
            print(
                f"  [{question['id']} #{iteration}] "
                f"local_wall_clock={elapsed:.2f}s"
            )

    from langchain_core.tracers.langchain import wait_for_all_tracers
    from langsmith import Client

    wait_for_all_tracers()
    client = Client()
    expected_count = len(questions) * args.repetitions
    root_runs = wait_for_tagged_root_runs(
        client,
        project_name=args.project,
        benchmark_tag=benchmark_tag,
        started_at=started_at,
        expected_count=expected_count,
        timeout_seconds=args.trace_wait_timeout,
    )
    spans = load_trace_spans(
        client,
        project_name=args.project,
        benchmark_tag=benchmark_tag,
        started_at=started_at,
        root_runs=root_runs,
    )
    payload = build_report_payload(
        benchmark_id=benchmark_id,
        label=args.label,
        project_name=args.project,
        repetitions=args.repetitions,
        target_p95_seconds=args.target_p95,
        local_rows=local_rows,
        root_runs=root_runs,
        spans=spans,
        client=client,
    )
    json_path, md_path = write_report(payload, Path(args.out_dir))
    print(f"[latency] reports: {json_path}, {md_path}")
    print(json.dumps(payload["summary"], indent=2))
    return 0 if payload["summary"]["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

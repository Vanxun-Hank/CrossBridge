"""
Step 4c.C：从现有 chunks.jsonl 重灌 Chroma。

为什么需要：
  - ingestion.py --with-context 已经把 contextualized_content 写进 chunks.jsonl
  - 但老 Chroma 里的 embedding 是基于原 content 的，不能直接 upsert（content_hash
    没变 → 跳过）
  - 需要全量 rebuild：删旧 Chroma + ChromaVectorIndex.add(chunks) 用新 contextualized
    文本重新 embed

用法：
  export DASHSCOPE_API_KEY=... LANGSMITH_API_KEY=...
  .venv/bin/python files/rebuild_chroma.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "files"))

from rag_engine import ChromaVectorIndex, load_chunks_jsonl  # noqa


def main() -> None:
    chroma_dir = PROJECT_ROOT / "data" / "chroma"
    chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"

    if chroma_dir.exists():
        print(f"[rebuild] removing {chroma_dir}")
        shutil.rmtree(chroma_dir)

    chunks = load_chunks_jsonl(str(chunks_path))
    # Sample 用 contextualized 还是 content
    sample = chunks[0]
    has_ctx = bool(sample.get("contextualized_content"))
    if has_ctx:
        ctx_len = len(sample["contextualized_content"])
        content_len = len(sample["content"])
        print(f"[rebuild] sample chunk: content={content_len} ctx={ctx_len} → embed will use contextualized_content")
    else:
        print(f"[rebuild] sample chunk has NO contextualized_content → embed will fallback to content")

    idx = ChromaVectorIndex(str(chroma_dir))
    added = idx.add(chunks, skip_existing=False)
    print(f"[rebuild] added {added} chunks, total {len(idx)}")


if __name__ == "__main__":
    main()

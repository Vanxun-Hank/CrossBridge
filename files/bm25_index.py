"""
CrossBridge AI - BM25 Sparse Index
===================================
职责：
  对 ingestion 产出的 chunks（dict 列表）建一个 BM25 倒排索引。
  与 ChromaVectorIndex.search() 完全平行的接口，让 AdaptiveRetriever
  能 dense + sparse 双路并联，再交给 RRF 融合。

为什么要 BM25：
  合规文档充满专有 token —— "SFGS_09/2024"、"汇发〔2023〕28号"、"§4.12"、
  "EDD"、"HKMA"、"SBV" —— dense embedding 对这些精确 token 信号弱，
  BM25 才能稳。

设计要点：
  - 中文用 jieba 切词，英文走 whitespace + lower
  - 标题 / 章节号 在索引时重复一次，相当于做了一个 free title boost
  - 不做持久化：809 chunks × jieba 切词 ~2 秒，每次冷启动现建够用
"""

from __future__ import annotations

import os
import re
from typing import Iterable

try:
    import jieba  # type: ignore
    jieba.initialize()  # 提前加载词典避免第一次 search 慢
    _HAS_JIEBA = True
except Exception:
    _HAS_JIEBA = False

from rank_bm25 import BM25Okapi


# ----------------------------------------------------------------------
# Tokenizer
# ----------------------------------------------------------------------

# 中文字符匹配（含日韩汉字段，保险起见用 一-鿿）
_CJK_RE = re.compile(r"[一-鿿]+")
# 英文/数字 token 匹配（保留连字符、斜杠、井号等让 "SFGS_09/2024" 不被切碎）
_LATIN_RE = re.compile(r"[A-Za-z0-9_/\-§#.]+")


def _tokenize(text: str) -> list[str]:
    """
    中英混合切词：
      1. 把 CJK 段交给 jieba（没 jieba 就按字切，rank_bm25 仍能跑）
      2. 把英文/数字段按正则抽出来，整体保留（"SFGS_09/2024" 不被拆）
      3. 全部 lower-case，丢掉单字符 token（标点噪声）
    """
    if not text:
        return []
    text = text.strip()

    tokens: list[str] = []

    # 先抽英文/数字 token（保留专有标识符整体）
    latin_tokens = _LATIN_RE.findall(text)
    tokens.extend(t.lower() for t in latin_tokens)

    # 再抽中文段，逐段过 jieba
    for cjk_seg in _CJK_RE.findall(text):
        if _HAS_JIEBA:
            tokens.extend(t for t in jieba.cut_for_search(cjk_seg) if t.strip())
        else:
            tokens.extend(list(cjk_seg))

    # 丢掉空 token 和长度 1 的英文 token（中文单字保留）
    out = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue
        if len(t) == 1 and not _CJK_RE.match(t):
            continue
        out.append(t)
    return out


# ----------------------------------------------------------------------
# Chunk → downstream doc shape
# ----------------------------------------------------------------------

def _chunk_to_doc(chunk: dict) -> dict:
    """
    把 ingestion chunk dict 转成 downstream 代码期望的 doc dict 形状。
    必须与 rag_engine._chroma_result_to_doc 的输出对齐（同 id / 同字段名），
    否则 rrf_fuse 按 id 去重会失败。
    """
    return {
        # downstream 必需字段
        "id": chunk.get("chunk_id") or chunk.get("doc_id"),
        "title": chunk.get("title", ""),
        "content": chunk.get("content", ""),
        "source_name": chunk.get("source_name") or chunk.get("issuer", ""),
        "source_url": chunk.get("source_url", ""),
        "region": chunk.get("region_code", ""),
        "topic": chunk.get("topic_code", ""),
        # downstream 可选字段
        "effective_date": chunk.get("effective_date") or None,
        "publish_date": chunk.get("publish_date") or None,
        "source_type": chunk.get("source_type") or "unknown",
        "authority_level": chunk.get("authority_level") or "medium",
        "disclaimer_level": chunk.get("disclaimer_level") or "unknown",
        "disclaimer": chunk.get("disclaimer", ""),
        # chunk 元数据，给精细引用用
        "doc_id": chunk.get("doc_id", ""),
        "parent_doc_id": chunk.get("parent_doc_id", "") or chunk.get("doc_id", ""),
        "chunk_id": chunk.get("chunk_id", ""),
        "chunk_index": chunk.get("chunk_index", 0),
        "chapter": chunk.get("chapter", ""),
        "section": chunk.get("section", ""),
        "page": chunk.get("page", ""),
        # Step 3.5：版本指纹 + Codex trust 分级
        "content_hash": chunk.get("content_hash", ""),
        "trust_tier": chunk.get("trust_tier", ""),
        "document_type": chunk.get("document_type", ""),
    }


def _doc_text_for_indexing(chunk: dict) -> str:
    """
    构造 BM25 要索引的"超级文本"：
      - Step 4c.C：主体优先用 contextualized_content（LLM 生成的中文 context 前缀
        + 原 content），fallback 原 content
      - title / chapter / section 重复一次相当于给标题做轻量 boost

    这就是 Anthropic "Contextual BM25" 的关键 trick —— context 前缀让英文 doc 也能
    被中文 query token 命中。
    """
    main = chunk.get("contextualized_content") or chunk.get("content") or ""
    parts = [main]
    for field in ("title", "chapter", "section"):
        val = chunk.get(field)
        if val:
            parts.append(str(val))
    return "\n".join(parts)


# ----------------------------------------------------------------------
# LangSmith tracing (optional)
# ----------------------------------------------------------------------

try:
    from langsmith import traceable  # type: ignore
except Exception:
    def traceable(*_args, **_kwargs):  # type: ignore
        def _decorator(fn):
            return fn
        return _decorator


# ----------------------------------------------------------------------
# BM25Index
# ----------------------------------------------------------------------

class BM25Index:
    """
    BM25 sparse 索引。
    接口与 ChromaVectorIndex.search() 平行：
        search(query, region=None, topic=None, top_k=3) -> [(doc_dict, score), ...]
    """

    backend = "bm25"

    def __init__(self, chunks: Iterable[dict]):
        self.chunks: list[dict] = [c for c in chunks if c]
        if not self.chunks:
            raise ValueError("BM25Index 至少需要 1 个 chunk")
        self._tokenized: list[list[str]] = [
            _tokenize(_doc_text_for_indexing(c)) for c in self.chunks
        ]
        self._bm25 = BM25Okapi(self._tokenized)
        print(
            f"[Index] BM25 已构建 docs={len(self.chunks)} "
            f"avgdl={sum(len(t) for t in self._tokenized) / max(1, len(self._tokenized)):.1f} "
            f"jieba={'on' if _HAS_JIEBA else 'off'}"
        )

    def __len__(self) -> int:
        return len(self.chunks)

    @traceable(run_type="retriever", name="BM25Search")
    def search(
        self,
        query: str,
        region: str | None = None,
        topic: str | None = None,
        top_k: int = 3,
    ) -> list[tuple[dict, float]]:
        if not query or not query.strip():
            return []
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        scores = self._bm25.get_scores(q_tokens)

        # 收集 (chunk_idx, score)，按 region/topic 过滤
        candidates: list[tuple[int, float]] = []
        for i, s in enumerate(scores):
            if s <= 0:
                continue
            chunk = self.chunks[i]
            if region and region != "全部":
                if (chunk.get("region_code") or "") != region:
                    continue
            if topic and topic != "全部":
                if (chunk.get("topic_code") or "") != topic:
                    continue
            candidates.append((i, float(s)))

        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[: max(1, top_k)]

        return [(_chunk_to_doc(self.chunks[i]), s) for i, s in candidates]


# ----------------------------------------------------------------------
# CLI smoke entry
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # 用 chunks.jsonl 跑一个独立 smoke test，不依赖 chroma / api key
    import sys, json

    path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/chunks.jsonl"
    if not os.path.exists(path):
        print(f"chunks 文件不存在: {path}")
        sys.exit(1)

    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    idx = BM25Index(chunks)

    test_queries = [
        "SFGS_09/2024",
        "汇发〔2023〕28号",
        "§4.12 客户尽调",
        "HKMA AML",
        "跨境付款合规",
    ]
    for q in test_queries:
        print(f"\n=== Q: {q}")
        for doc, s in idx.search(q, top_k=3):
            print(f"  {s:.3f}  {doc['doc_id']:<35}  {doc['title'][:50]}")

"""
CrossBridge AI - Cross-Encoder Reranker
========================================
职责：
  在 RRF 给出 top-N 候选池之后，用 cross-encoder 精排，提升 top-3 的 precision。
  RRF 看 rank 投票（recall 友好），rerank 看 (query, doc) 语义对（precision 友好），
  二者串联是工业标准 hybrid 检索 pipeline。

实现：
  - 直接 HTTP 调 DashScope `gte-rerank` 模型（阿里 GTE-Rerank，中英多语强）
  - 不引入 dashscope SDK 这个新依赖，用已有的 requests
  - 复用 DASHSCOPE_API_KEY 环境变量
  - 失败时 graceful fallback：返回原候选顺序，不阻塞 demo

API 文档：
  https://help.aliyun.com/zh/model-studio/developer-reference/general-text-sorting-model
"""

from __future__ import annotations

import os
from typing import List, Tuple

import requests

try:
    from langsmith import traceable  # type: ignore
except Exception:
    def traceable(*_args, **_kwargs):  # type: ignore
        def _decorator(fn):
            return fn
        return _decorator


DEFAULT_RERANK_MODEL = os.environ.get("DASHSCOPE_RERANK_MODEL", "gte-rerank-v2")
DEFAULT_RERANK_ENDPOINT = os.environ.get(
    "DASHSCOPE_RERANK_ENDPOINT",
    "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
)
DEFAULT_RERANK_TIMEOUT = float(os.environ.get("DASHSCOPE_RERANK_TIMEOUT", "20"))
# 单条 doc 字符上限，DashScope 文档默认建议 ≤ 4000 字。我们 chunk_size=800 token，
# 大概 1200-1600 字，留个 2500 字裕度。
DEFAULT_RERANK_DOC_CHARS = int(os.environ.get("DASHSCOPE_RERANK_DOC_CHARS", "2500"))


class DashScopeReranker:
    """
    DashScope gte-rerank 的薄封装。一次 HTTP 调用搞定一个 (query, [docs]) 批次。

    用法：
        rr = DashScopeReranker()
        reranked = rr.rerank(query, [(doc_dict, rrf_score), ...])
        # reranked: [(doc_dict, rerank_score), ...] 按 rerank_score 倒序
    """

    backend = "dashscope-rerank"

    def __init__(
        self,
        model: str = DEFAULT_RERANK_MODEL,
        api_key: str | None = None,
        endpoint: str = DEFAULT_RERANK_ENDPOINT,
        timeout: float = DEFAULT_RERANK_TIMEOUT,
        doc_chars: int = DEFAULT_RERANK_DOC_CHARS,
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self.endpoint = endpoint
        self.timeout = timeout
        self.doc_chars = doc_chars
        self._available = bool(self.api_key)
        # 反映最近一次 rerank() 调用是否真正成功（不只是 API key 在不在）
        # 让上游 trace 能区分 "rerank 调用成功" vs "fallback 到 RRF 顺序"
        self.last_call_succeeded = False
        if not self._available:
            print("[Rerank] DASHSCOPE_API_KEY 未设置，reranker 将禁用（fallback 到 RRF 顺序）")
        else:
            print(f"[Rerank] 已就绪 model={self.model}")

    def is_available(self) -> bool:
        return self._available

    def _truncate(self, text: str) -> str:
        if not text:
            return ""
        if len(text) <= self.doc_chars:
            return text
        return text[: self.doc_chars]

    @traceable(run_type="retriever", name="Rerank")
    def rerank(
        self,
        query: str,
        candidates: List[Tuple[dict, float]],
        top_n: int | None = None,
    ) -> List[Tuple[dict, float]]:
        """
        参数:
            query: 用户原始 query（不要传 HyDE 假答案，rerank 用原 query 才对）
            candidates: RRF 之后的 [(doc_dict, rrf_score), ...]
            top_n: 返回前 N 个；None = 全部返回
        返回:
            [(doc_dict, rerank_score), ...] 按 rerank_score 倒序
            失败时返回原 candidates（保持 RRF 顺序）
        """
        self.last_call_succeeded = False
        if not candidates:
            return []
        if not self._available:
            return candidates if top_n is None else candidates[:top_n]
        if not query or not query.strip():
            return candidates if top_n is None else candidates[:top_n]

        documents = [self._truncate(c[0].get("content") or "") for c in candidates]
        # 排除完全空文本（rerank 会报错）
        if not any(documents):
            return candidates if top_n is None else candidates[:top_n]

        payload = {
            "model": self.model,
            "input": {
                "query": query,
                "documents": documents,
            },
            "parameters": {
                "top_n": top_n if top_n is not None else len(documents),
                "return_documents": False,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                self.endpoint, json=payload, headers=headers, timeout=self.timeout
            )
            if resp.status_code != 200:
                print(
                    f"[Rerank] HTTP {resp.status_code} fallback to RRF order. "
                    f"body={resp.text[:200]}"
                )
                return candidates if top_n is None else candidates[:top_n]
            data = resp.json()
        except Exception as e:
            print(f"[Rerank] 调用异常 fallback to RRF order: {type(e).__name__}: {e}")
            return candidates if top_n is None else candidates[:top_n]

        results = (data.get("output") or {}).get("results") or []
        if not results:
            print(f"[Rerank] 响应里没有 results 字段 fallback. resp={data}")
            return candidates if top_n is None else candidates[:top_n]

        reranked: list[tuple[dict, float]] = []
        for r in results:
            idx = r.get("index")
            score = float(r.get("relevance_score", 0.0))
            if idx is None or not (0 <= idx < len(candidates)):
                continue
            doc = candidates[idx][0]
            # 把 rerank_score 也塞回 doc dict 里，方便 trace / debug 显示
            doc = {**doc, "rerank_score": score}
            reranked.append((doc, score))

        if not reranked:
            return candidates if top_n is None else candidates[:top_n]

        # DashScope 一般已经按 score 排了，再 sort 一遍保险
        reranked.sort(key=lambda x: x[1], reverse=True)
        self.last_call_succeeded = True
        return reranked if top_n is None else reranked[:top_n]


# ----------------------------------------------------------------------
# CLI smoke
# ----------------------------------------------------------------------

if __name__ == "__main__":
    rr = DashScopeReranker()
    if not rr.is_available():
        print("跳过 smoke：未设置 DASHSCOPE_API_KEY")
        raise SystemExit(0)

    fake_candidates = [
        ({"id": "a", "content": "苹果是一种水果，富含维生素。"}, 0.5),
        ({"id": "b", "content": "Apple Inc. 是一家美国科技公司。"}, 0.5),
        ({"id": "c", "content": "今天天气真好，适合散步。"}, 0.5),
    ]
    out = rr.rerank("iPhone 是哪个公司做的？", fake_candidates, top_n=3)
    print("\n=== rerank 结果（期望 b 排第一）：")
    for doc, s in out:
        print(f"  {s:.3f}  {doc['id']}  {doc['content']}")

"""
CrossBridge AI — OpenAI-compatible RAG server
=============================================
把 files/rag_engine.py 包成 OpenAI Chat Completions 兼容 HTTP endpoint，
供 ChatRaw（或任何 OpenAI 兼容前端）作为 "LLM endpoint" 调用。

端点:
    POST /v1/chat/completions    OpenAI 兼容 chat completion
    POST /v1/embeddings          OpenAI 兼容 embeddings（占位，避免 ChatRaw 端点测试 404）
    GET  /v1/models              OpenAI 兼容 model list
    GET  /healthz                健康检查

启动:
    export DASHSCOPE_API_KEY="..."
    export LANGSMITH_TRACING=false
    .venv/bin/uvicorn server.api:app --port 8080 --host 0.0.0.0
"""

from __future__ import annotations

import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse

# 让 server/ 能 import files/rag_engine
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "files"))

from language_utils import (  # noqa: E402
    detect_explicit_language_request,
    detect_response_language,
    normalize_answer_language,
)
from server.function5_local import LocalComplianceRAG  # noqa: E402

# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("crossbridge.api")

# ---------------------------------------------------------------------------
# RAG 引擎（单例，启动时加载）
# ---------------------------------------------------------------------------
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

RAG_FALLBACK_REASON: str | None = None
_LOCAL_FALLBACK_RAG: LocalComplianceRAG | None = None


def _load_local_fallback(reason: str) -> LocalComplianceRAG:
    """Load the local runnable Function 5 engine."""
    global _LOCAL_FALLBACK_RAG
    if _LOCAL_FALLBACK_RAG is None:
        log.warning("Loading local Function 5 fallback. reason=%s", reason)
        _LOCAL_FALLBACK_RAG = LocalComplianceRAG(CHUNKS_PATH)
    return _LOCAL_FALLBACK_RAG


def _load_rag_engine():
    """
    Prefer the full Qwen + Chroma + BM25 + rerank pipeline. If the environment
    is not ready, fall back to the local BM25/RRF/citation-gating engine so
    Function 5 still runs on port 8080 for demo and development.
    """
    global RAG_FALLBACK_REASON
    log.info("Loading CrossBridge RAG engine from %s ...", CHUNKS_PATH)
    try:
        from rag_engine import CrossBridgeRAG  # noqa: WPS433

        engine = CrossBridgeRAG(
            chunks_path=str(CHUNKS_PATH),
            persist_directory=str(CHROMA_DIR),
        )
        RAG_FALLBACK_REASON = None
        return engine
    except Exception as exc:  # noqa: BLE001
        RAG_FALLBACK_REASON = f"{type(exc).__name__}: {exc}"
        log.exception("Full RAG engine failed to load; using local fallback")
        return _load_local_fallback(RAG_FALLBACK_REASON)


rag = _load_rag_engine()
log.info(
    "RAG engine ready. backend=%s, %d chunks loaded",
    rag.index.backend,
    len(rag.docs),
)

# ---------------------------------------------------------------------------
# trust_tier → 单色中文小标签（用户要求："单色（深灰/黑）小 tag，去 emoji"）
# ---------------------------------------------------------------------------
TIER_LABELS = {
    "zh": {
        "regulator": "监管",
        "central_bank": "央行",
        "government": "政府",
        "official_dev": "官方机构",
        "bank": "银行",
        "industry": "业界",
        "non_official": "第三方",
    },
    "en": {
        "regulator": "Regulator",
        "central_bank": "Central bank",
        "government": "Government",
        "official_dev": "Official institution",
        "bank": "Bank",
        "industry": "Industry",
        "non_official": "Third party",
    },
    "bilingual": {
        "regulator": "监管 / Regulator",
        "central_bank": "央行 / Central bank",
        "government": "政府 / Government",
        "official_dev": "官方机构 / Official institution",
        "bank": "银行 / Bank",
        "industry": "业界 / Industry",
        "non_official": "第三方 / Third party",
    },
}

MODEL_ID = os.environ.get("CROSSBRIDGE_MODEL_ID", "crossbridge-rag")


# ---------------------------------------------------------------------------
# Citation 格式：Markdown 段落（ChatRaw 默认渲染 Markdown）
# ---------------------------------------------------------------------------
def _strip_llm_trailing_citation_line(answer: str) -> str:
    """
    rag_engine 的 SYSTEM_PROMPT 让 LLM 在答案末尾自己加一行
    "信息来源：[资料1]、[资料2]、[资料3]"。
    我们要在下面追加结构化的 Markdown 信息来源段（含链接 + trust tag），
    所以先把 LLM 自己写的这一行裁掉，避免出现两个 "信息来源" 标题。

    注意：只裁"末尾这一行"，inline 出现的 [资料X] 引用标记保留（它们让答案更可信）。
    """
    if not answer:
        return answer
    lines = answer.rstrip().split("\n")
    # 从末尾往前找，跳过空行，找到第一条非空行
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        last = lines[-1].strip()
        # 匹配中英文模型自行生成的末尾 source line，避免重复标题。
        if (
            last.startswith(("信息来源", "来源：", "来源:", "Sources", "Source:", "Sources:"))
            and ("[资料" in last or "[Source" in last)
        ):
            lines.pop()
    return "\n".join(lines).rstrip()


def _format_citations_markdown(citations: list[dict], response_language: str = "zh") -> str:
    """
    生成答案末尾追加的"信息来源"段。

    格式（用户审美方向：克制、无 emoji、单色斜体小 tag）：

        ---

        **信息来源**

        1. [HKMA AML-2 指引](https://...) · *监管*
        2. [SAFE 跨境便利化政策](https://...) · *政府*
    """
    if not citations:
        return ""
    is_english = response_language == "en"
    is_bilingual = response_language == "bilingual"
    heading = "Sources" if is_english else "信息来源 / Sources" if is_bilingual else "信息来源"
    lines = ["", "---", "", f"**{heading}**", ""]
    for i, c in enumerate(citations, 1):
        title = (c.get("title") or "").strip() or ("Untitled source" if is_english else "未命名资料")
        url = (c.get("url") or "").strip()
        tier_lbl = TIER_LABELS[response_language].get(c.get("trust_tier") or "")
        # link 部分：有 URL 用链接，没 URL 用 bold title
        if url:
            link = f"[{title}]({url})"
        else:
            link = f"**{title}**"
        # 尾巴小 tag（深灰斜体，单色，符合 ChatRaw 风格）
        tail = f" · *{tier_lbl}*" if tier_lbl else ""
        lines.append(f"{i}. {link}{tail}")
    return "\n".join(lines)


def _extract_query_from_messages(messages: list[dict]) -> str:
    """
    OpenAI chat completion: messages 是 [{role, content}, ...]。
    取最后一条 user 消息当作 RAG query。
    pitch demo 现场不做真正 multi-turn —— 每个问题独立检索。
    """
    user_msgs = [m for m in messages if m.get("role") == "user"]
    if not user_msgs:
        return ""
    last = user_msgs[-1].get("content", "")
    # OpenAI multi-part content (vision): 取所有 text part 拼起来
    if isinstance(last, list):
        text_parts = []
        for part in last:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif isinstance(part, str):
                text_parts.append(part)
        return "\n".join(text_parts).strip()
    return str(last).strip()


def _resolve_response_language(messages: list[dict], fallback: str | None = None) -> str:
    """Use the latest clear user language; ambiguous turns inherit conversation language."""
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        text = _extract_query_from_messages([message])
        if requested := detect_explicit_language_request(text):
            return requested
        if detected := detect_response_language(text):
            return detected
    return normalize_answer_language(fallback)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CrossBridge AI — OpenAI-compatible RAG server",
    version="1.0.0",
)

# CORS 全开（pitch demo 本地，前后端可能不同 origin）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict:
    return {
        "status": "ok",
        "rag_backend": rag.index.backend,
        "n_chunks": len(rag.docs),
        "model_id": MODEL_ID,
        "fallback_active": RAG_FALLBACK_REASON is not None,
        "fallback_reason": RAG_FALLBACK_REASON,
    }


@app.get("/v1/models")
def list_models() -> dict:
    """OpenAI 兼容 model list — ChatRaw 通常会调这个测试 endpoint。"""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "crossbridge-ai",
            }
        ],
    }


@app.post("/v1/embeddings")
async def embeddings_stub(req: Request) -> JSONResponse:
    """
    占位 embeddings endpoint —— ChatRaw 可能调它测试 model type=embedding。
    我们不真的提供 embedding 服务（rag_engine 内部直接用 DashScope），
    这里返回 400 + 友好错误信息。
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": "Embedding endpoint is not supported by CrossBridge RAG server. "
                           "Use /v1/chat/completions instead.",
                "type": "invalid_request_error",
                "code": "endpoint_not_supported",
            }
        },
    )


@app.post("/v1/chat/completions")
async def chat_completions(req: Request) -> JSONResponse:
    """
    OpenAI 兼容 chat completion. ChatRaw 调这个。

    流程:
      1. 从 messages 取最后一条 user message 当 query
      2. 调 rag.ask(query, top_k=3) — 完整 hybrid + rerank + citation gating pipeline
      3. 把 citation 拼成 Markdown 段落追加到答案末尾
      4. 返回 OpenAI 标准响应（含 choices[0].message.content）

    Streaming: 当前不支持（rag.ask 是 ~20s 的 blocking pipeline，streaming 收益 ≈ 0）。
    若 ChatRaw 请求 stream=True，我们仍然走非 streaming 返回完整一次。
    """
    try:
        body = await req.json()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": f"Invalid JSON body: {e}", "type": "invalid_request_error"}},
        )

    messages = body.get("messages", [])
    query = _extract_query_from_messages(messages)
    if not query:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": "messages must contain at least one user message with non-empty content",
                               "type": "invalid_request_error"}},
        )

    response_language = _resolve_response_language(
        messages,
        fallback=req.headers.get("X-CrossBridge-UI-Language"),
    )
    log.info(
        "Chat request: query=%r (len=%d), response_language=%s",
        query[:80],
        len(query),
        response_language,
    )
    t0 = time.time()
    try:
        result = rag.ask(query, top_k=3, debug=False, response_language=response_language)
    except Exception as e:  # noqa: BLE001
        if RAG_FALLBACK_REASON is None:
            # Full RAG loaded, but a live dependency failed during this request
            # (for example DashScope quota/network). Preserve the demo by
            # falling back to the local Function 5 engine for this turn.
            log.exception("Full RAG ask() failed; retrying with local fallback")
            try:
                fallback = _load_local_fallback(f"runtime {type(e).__name__}: {e}")
                result = fallback.ask(
                    query,
                    top_k=3,
                    debug=False,
                    response_language=response_language,
                )
            except Exception as fallback_error:  # noqa: BLE001
                log.exception("Local fallback RAG ask() failed")
                return JSONResponse(
                    status_code=502,
                    content={
                        "error": {
                            "message": (
                                f"RAG backend failed: {type(e).__name__}: {e}; "
                                f"fallback failed: {type(fallback_error).__name__}: {fallback_error}"
                            ),
                            "type": "backend_error",
                        }
                    },
                )
        else:
            # Fallback was already active and still failed.
            log.exception("RAG ask() failed")
            return JSONResponse(
                status_code=502,
                content={
                    "error": {
                        "message": f"RAG backend failed: {type(e).__name__}: {e}",
                        "type": "backend_error",
                    }
                }
            )

    elapsed = time.time() - t0
    raw_answer = (result.get("answer") or "").strip()
    answer = _strip_llm_trailing_citation_line(raw_answer)
    citations = result.get("citations") or []
    citation_md = _format_citations_markdown(citations, response_language=response_language)
    full_text = answer + citation_md if citation_md else answer

    log.info(
        "Chat response: %.1fs, %d citations, answer_len=%d",
        elapsed, len(citations), len(answer),
    )

    # OpenAI 标准 chat completion 响应
    return JSONResponse(content={
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", MODEL_ID),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            # 我们不算 token，这里给 0 让 ChatRaw 别炸
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    })


# ---------------------------------------------------------------------------
# Function 5 自带 demo —— 结构化政策合规问答 endpoint + 单页前端
#
# 设计原则：纯加法。
#   - 不改 /v1/chat/completions（ChatRaw 仍用它，OpenAI 兼容）。
#   - 不改 rag.ask() 的调用方式，所以 eval/run_eval.py、run_ragas.py（直接 import
#     CrossBridgeRAG 调 .ask()）完全不受影响。
#   - 引擎是哪条由 server 自动决定：有 DASHSCOPE_API_KEY + 依赖齐全 → 完整 Qwen 流水线；
#     否则 → 本地兜底引擎（server/function5_local.py）。两条都喂同一个 demo 页。
# ---------------------------------------------------------------------------
F5_DEMO_PAGE = Path(__file__).resolve().parent / "static" / "function5.html"


def _engine_info() -> dict:
    """当前实际在跑的引擎信息（给 demo 页的徽标用）。"""
    return {
        "backend": rag.index.backend,
        "n_chunks": len(rag.docs),
        "fallback_active": RAG_FALLBACK_REASON is not None,
        "fallback_reason": RAG_FALLBACK_REASON,
        "mode": "local_fallback" if RAG_FALLBACK_REASON is not None else "full_pipeline",
    }


def _resolve_demo_language(query: str, requested: str | None) -> str:
    """显式选择优先；否则按问题文本检测；都没有则回退默认。"""
    if requested in {"zh", "en", "bilingual"}:
        return requested
    return (
        detect_explicit_language_request(query)
        or detect_response_language(query)
        or normalize_answer_language(None)
    )


@app.post("/function5/ask")
async def function5_ask(req: Request) -> JSONResponse:
    """
    结构化政策合规问答（Function 5 自带 demo 页调用）。

    与 /v1/chat/completions 区别：这里返回结构化 JSON
    （answer + citations[] + retrieval trace + engine 信息），方便前端分区展示
    “权威答案 / 合规风险提示 / 操作建议 / 官方来源”。

    请求体: {"query": "...", "language": "auto|zh|en|bilingual", "top_k": 3}
    """
    try:
        body = await req.json()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": {
            "message": f"Invalid JSON body: {e}", "type": "invalid_request_error"}})

    query = (body.get("query") or body.get("question") or "").strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": {
            "message": "field 'query' is required and must be non-empty",
            "type": "invalid_request_error"}})

    language = _resolve_demo_language(query, body.get("language"))
    try:
        top_k = max(1, min(8, int(body.get("top_k") or 3)))
    except (TypeError, ValueError):
        top_k = 3

    log.info("Function5 ask: query=%r (len=%d), language=%s", query[:80], len(query), language)
    t0 = time.time()
    try:
        result = rag.ask(query, top_k=top_k, debug=True, response_language=language)
    except Exception as e:  # noqa: BLE001
        # 与 /v1/chat/completions 一致：完整引擎运行时挂掉 → 本轮用本地兜底救场
        if RAG_FALLBACK_REASON is None:
            log.exception("Full RAG ask() failed in /function5/ask; retrying with local fallback")
            try:
                fallback = _load_local_fallback(f"runtime {type(e).__name__}: {e}")
                result = fallback.ask(query, top_k=top_k, debug=True, response_language=language)
            except Exception as fallback_error:  # noqa: BLE001
                log.exception("Local fallback ask() also failed")
                return JSONResponse(status_code=502, content={"error": {
                    "message": (f"RAG backend failed: {type(e).__name__}: {e}; "
                                f"fallback failed: {type(fallback_error).__name__}: {fallback_error}"),
                    "type": "backend_error"}})
        else:
            log.exception("RAG ask() failed")
            return JSONResponse(status_code=502, content={"error": {
                "message": f"RAG backend failed: {type(e).__name__}: {e}", "type": "backend_error"}})

    return JSONResponse(content={
        "answer": (result.get("answer") or "").strip(),
        "citations": result.get("citations") or [],
        "response_language": result.get("response_language", language),
        "elapsed_seconds": round(time.time() - t0, 2),
        "engine": _engine_info(),
        "trace": result.get("retrieval_trace") or {},
    })


@app.get("/")
def root() -> Any:
    """根路径直接 serve Function 5 demo 页；缺失时退回纯文本端点说明。"""
    if F5_DEMO_PAGE.exists():
        return FileResponse(str(F5_DEMO_PAGE), media_type="text/html")
    return PlainTextResponse(
        "CrossBridge AI — Function 5 RAG server\n"
        "GET  /                     — Function 5 demo page (missing)\n"
        "POST /function5/ask        — structured policy & compliance Q&A\n"
        "POST /v1/chat/completions  — OpenAI-compatible chat (ChatRaw)\n"
        "GET  /v1/models            — list models\n"
        "GET  /healthz              — health check\n"
    )

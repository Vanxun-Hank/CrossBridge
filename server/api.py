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
from fastapi.responses import JSONResponse, PlainTextResponse

# 让 server/ 能 import files/rag_engine
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "files"))

from rag_engine import CrossBridgeRAG  # noqa: E402

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

log.info("Loading CrossBridge RAG engine from %s ...", CHUNKS_PATH)
rag = CrossBridgeRAG(
    chunks_path=str(CHUNKS_PATH),
    persist_directory=str(CHROMA_DIR),
)
log.info(
    "✅ RAG engine ready. backend=%s, %d chunks loaded",
    rag.index.backend,
    len(rag.docs),
)

# ---------------------------------------------------------------------------
# trust_tier → 单色中文小标签（用户要求："单色（深灰/黑）小 tag，去 emoji"）
# ---------------------------------------------------------------------------
TIER_LABEL = {
    "regulator":    "监管",
    "central_bank": "央行",
    "government":   "政府",
    "official_dev": "官方机构",
    "bank":         "银行",
    "industry":     "业界",
    "non_official": "第三方",
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
        # 匹配 "信息来源：[资料X]..." / "信息来源:[资料X]..." / "来源：[资料X]..."
        if last.startswith(("信息来源", "来源：", "来源:")) and "[资料" in last:
            lines.pop()
    return "\n".join(lines).rstrip()


def _format_citations_markdown(citations: list[dict]) -> str:
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
    lines = ["", "---", "", "**信息来源**", ""]
    for i, c in enumerate(citations, 1):
        title = (c.get("title") or "").strip() or "未命名资料"
        url = (c.get("url") or "").strip()
        tier_lbl = TIER_LABEL.get(c.get("trust_tier") or "")
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

    log.info("Chat request: query=%r (len=%d)", query[:80], len(query))
    t0 = time.time()
    try:
        result = rag.ask(query, top_k=3, debug=False)
    except Exception as e:  # noqa: BLE001
        # 真正调 RAG 失败（如 DashScope 配额耗尽、网络断）→ 返回友好错误
        log.exception("RAG ask() failed")
        return JSONResponse(
            status_code=502,
            content={
                "error": {
                    "message": f"RAG backend failed: {type(e).__name__}: {e}",
                    "type": "backend_error",
                }
            },
        )

    elapsed = time.time() - t0
    raw_answer = (result.get("answer") or "").strip()
    answer = _strip_llm_trailing_citation_line(raw_answer)
    citations = result.get("citations") or []
    citation_md = _format_citations_markdown(citations)
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


@app.get("/")
def root() -> PlainTextResponse:
    return PlainTextResponse(
        "CrossBridge AI — OpenAI-compatible RAG server\n"
        "POST /v1/chat/completions  — chat with RAG\n"
        "GET  /v1/models            — list models\n"
        "GET  /healthz              — health check\n"
    )

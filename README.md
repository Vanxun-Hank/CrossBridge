# CrossBridge AI

跨境普惠金融决策助手（B2B）— 中銀香港創新先驅大賽 2026 參賽項目。

帮助中小企业把跨境政策、汇款、融资讲清楚，每条答案都附 **trust_tier × document_type 双维分级**的权威来源。

---

## 核心能力

- **Hybrid Retrieval**: BM25 (jieba 中文切词) + Dense (Qwen text-embedding-v4) + RRF 融合
- **Cross-Encoder Rerank**: DashScope gte-rerank-v2 精排
- **Anthropic Contextual Retrieval**: 每个 chunk embed 前注入 50-100 字中文 context 前缀，解决中文 query → 英文 doc 跨语言 retrieval
- **Per-doc Chunk Cap**: 防大文档（HKMA AML 82 chunks）独占 top-K
- **Citation Gating**: `trust_tier ∈ {regulator, central_bank, government, official_dev, bank}` AND `document_type ∉ {hub_page}` 双维门控，hub/导航页只作 context 不作 citation
- **Graceful Fallback**: rerank API 失败 → RRF 顺序；citation filter 全空 → 三路退化（trusted_clean / fallback_trusted_hub / fallback_all）

---

## Eval 数据（24 题 eval set）

| 指标 | 值 |
|---|---|
| Recall@5 | **100%** (24/24) |
| Recall@10 | **100%** |
| Citation Hit Rate | **100%** |
| Faithfulness (RAGAS) | **0.7642**（7 题 ≥0.9） |

详细报告：`eval/reports/eval_full_*.md` + `ragas_full_*.md`

---

## 项目结构

```
files/
  rag_engine.py              主引擎（LangGraph chain: classify → multi-query → search → RRF → rerank → metadata score → citation gate → prompt → LLM）
  bm25_index.py              BM25Okapi + jieba
  reranker.py                DashScope gte-rerank-v2 HTTP wrapper（含 graceful fallback）
  ingestion.py               切块 + 元数据抽取 + Anthropic Contextual Retrieval（--with-context）
  rebuild_chroma.py          从 chunks.jsonl 全量重建 Chroma
  app_streamlit_legacy.py    早期 Streamlit demo UI（pitch backup）
  knowledge_base.json        in-memory demo fallback

server/
  api.py                     OpenAI-compatible HTTP wrapper（FastAPI），把 rag_engine 包成 /v1/chat/completions 端点

data/
  processed/chunks.jsonl     1171 chunks (76 篇官方文档，含 Contextual Retrieval 前缀)
  chroma/                    Chroma 持久化向量库
  *.md                       76 篇官方源文档（HKMA / SAFE / BOCHK / HKMC / GoGBA / HKTDC / SBV / FIA 等）
  metadata_index.json        全局文档清单

eval/
  questions.jsonl            24 题 eval set（5 个 demo 场景）
  run_eval.py                Tier 1 runner (recall@k + citation_hit)
  run_ragas.py               Tier 2 runner (RAGAS faithfulness)
  reports/                   eval 报告（baseline/step3/full + ragas）
```

---

## 部署

### 后端（RAG FastAPI server）

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # 或参见 files/requirements.txt
export DASHSCOPE_API_KEY="..."
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export QWEN_MODEL="qwen-plus"
uvicorn server.api:app --host 127.0.0.1 --port 8080
```

### 前端

UI 用 [ChatRaw](https://github.com/massif-01/ChatRaw) （MIT, © massif-01）作为聊天前端。本仓库**不嵌入** ChatRaw 源码，请单独 clone：

```bash
git clone https://github.com/massif-01/ChatRaw chatraw-fork
cd chatraw-fork/backend
pip install -r requirements.txt
python main.py
```

启动后 POST 注册模型 + 改 brand：

```bash
# 注册 CrossBridge RAG 为 default-chat 模型
curl -X POST http://127.0.0.1:51111/api/models \
  -H 'Content-Type: application/json' \
  -d '{"id":"default-chat","name":"CrossBridge AI","api_url":"http://127.0.0.1:8080/v1","api_key":"dummy","model_id":"crossbridge-rag","context_length":16384,"max_output":4096,"type":"chat"}'

# 改 brand
curl -X POST http://127.0.0.1:51111/api/settings \
  -H 'Content-Type: application/json' \
  -d '{"chat_settings":{"temperature":0.3,"stream":false},"ui_settings":{"logo_text":"CrossBridge AI","subtitle":"跨境普惠金融决策助手 · 每条答案附权威来源","theme_mode":"light"}}'
```

### 反向代理（生产）

`/etc/nginx/sites-available/crossbridge`：

```nginx
geo $allowed {
    default 0;
    YOUR.IP.HERE 1;
    127.0.0.1 1;
}

server {
    listen 80 default_server;
    if ($allowed = 0) { return 403; }
    location / {
        proxy_pass http://127.0.0.1:51111;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 90s;
    }
}
```

---

## 开发笔记

- `PROGRESS.md` — 改造时间线 + eval 数据演进 + 已知坑
- `PROJECT_MEMORY.md` — 产品背景 + pitch demo 场景剧本

---

## 致谢

- [ChatRaw](https://github.com/massif-01/ChatRaw) by massif-01 — MIT 极简聊天 UI
- [Anthropic Contextual Retrieval (2024)](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide) — 跨语言 retrieval 思路
- DashScope (Qwen) — embedding / chat / cross-encoder rerank

---

## License

MIT

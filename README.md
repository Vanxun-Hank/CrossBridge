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
- **Function 1 Loan Matching**: 独立 FastAPI + SQLite/Alembic + BOCHK 官方公开来源目录；企业画像草稿、最多 3 轮 AI 澄清、Python 确定性匹配、来源链接、用户确认后才保存长期画像
- **Function 1 Public Detail Crawl**: 抓取 7 个 BOCHK 官方来源（产品页、进出口详情页、收费表 PDF），分开展示公开手续费、适用说明、材料提示与待客户经理确认字段
- **Function 2 Document Preparation**: 独立 FastAPI + SQLite/Alembic 材料准备工作台；按进口付款 / 出口履约场景组织三档清单、产品公开材料、可编辑模板、实时校验和打印稿
- **Bilingual Workspace**: Function 1 / Function 2 工作区全部可见文字跟随 ChatRaw Settings language 切换，中英文模式不混排

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
  business/                  Function 1 独立业务服务（FastAPI + SQLAlchemy + Alembic）
  document_preparation/      Function 2 独立材料准备服务（FastAPI + SQLAlchemy + Alembic）

migrations/
  versions/                  Function 1 SQLite schema migration

data/
  official_products/         Function 1 BOCHK 官方公开来源结构化目录
  document_preparation/      Function 2 场景基础包 + 产品叠加材料快照
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

Function 1 需要先启动独立业务服务：

```bash
pip install -r server/business/requirements.txt
.venv/bin/python scripts/crawl_bochk_products.py
.venv/bin/alembic -c alembic.ini upgrade head
CROSSBRIDGE_CATALOG_MODE=official .venv/bin/uvicorn server.business.app:app --host 127.0.0.1 --port 8081
```

F1 的自由文本草稿抽取会优先读取 `CROSSBRIDGE_CLARIFIER_API_KEY`，未设置时复用
`DASHSCOPE_API_KEY`。生产环境将密钥保存在 `/opt/crossbridge/.env`，不要提交到 Git：

```bash
DASHSCOPE_API_KEY="..."
QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL="qwen-plus"
```

Function 2 使用独立数据库和快照：

```bash
.venv/bin/python scripts/sync_document_preparation_catalog.py
.venv/bin/uvicorn server.document_preparation.app:app --host 127.0.0.1 --port 8082
```

```bash
git clone https://github.com/massif-01/ChatRaw chatraw-fork
./scripts/apply_chatraw_patch.sh
cd chatraw-fork/backend
pip install -r requirements.txt
python main.py
```

`patches/chatraw-function1-function2.patch` 保存 CrossBridge 对 ChatRaw 的定制：
F1 聊天内嵌贷款匹配、F2 右侧材料工作台、双语文案、固定代理路由、三栏拖拽布局，
以及为产品卡腾出空间的紧凑底部输入区。政策问答和 F1 澄清问题会跟随用户提问语言；
无法判断语言时使用最近一次明确语言，首次进入则回退到 Settings。
ChatRaw 本体仍保持独立 clone，不嵌入本仓库。

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
- `.venv/bin/python eval/run_function1_eval.py` — Function 1 独立自动化 eval，输出 JSON + Markdown 报告
- `.venv/bin/python eval/run_function1_official_catalog_eval.py` — Function 1 BOCHK 官方公开来源目录 eval
- `.venv/bin/python eval/run_function2_eval.py` — Function 2 独立自动化 eval

Function 1 官方目录抓取范围：

- `https://www.bochk.com/en/loan/loan/unsecured.html`
- `https://www.bochk.com/dam/smeinone/loan/en.html`
- `https://www.bochk.com/en/corporate/tradefinance/overview.html`
- `https://www.bochk.com/en/corporate/tradefinance/import.html`
- `https://www.bochk.com/en/corporate/tradefinance/export.html`
- `https://www.bochk.com/dam/corporatebanking/tfs_tariffs_en.pdf`
- `https://www.bochk.com/en/loan/loan/tradefinance/supply_chain_finance_solution.html`

---

## 致谢

- [ChatRaw](https://github.com/massif-01/ChatRaw) by massif-01 — MIT 极简聊天 UI
- [Anthropic Contextual Retrieval (2024)](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide) — 跨语言 retrieval 思路
- DashScope (Qwen) — embedding / chat / cross-encoder rerank

---

## License

MIT

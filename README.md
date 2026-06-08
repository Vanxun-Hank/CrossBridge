# CrossBridge AI

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

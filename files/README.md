# 🌉 CrossBridge AI — MVP

跨境普惠金融决策助手。中小企业用一句话提问,AI 基于权威资料回答,每个答案都附**引用来源**。

科技主题:生成式 AI ｜ 场景主题:跨境(大湾区+东南亚)+ 普惠金融

---

## 这个 MVP 做了什么

```
用户提问 → 按地区/主题检索知识库 → 取最相关资料 → 大模型生成带引用的答案
```

只聚焦一个核心闭环:**问 → 查权威资料 → 答 + 引用**。这是与 ChatGPT 最大的区别 —— 答案有出处、可追溯、专注跨境金融。

---

## 三个文件,各管一件事

| 文件 | 作用 |
|---|---|
| `knowledge_base.json` | 结构化知识库(目前是示例数据,**正式用要换成爬来的真实资料**)|
| `rag_engine.py` | RAG 核心:向量化 → 检索 → 调用大模型生成 |
| `app.py` | Streamlit 对话界面(路演演示用)|

---

## 怎么跑起来(3 步)

### 1. 装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置千问和 LangSmith API
当前版本使用千问生成模型 + 千问向量模型,并通过 LangSmith 做可视化 tracing。API key 只放环境变量,不要写进代码:
```bash
export DASHSCOPE_API_KEY=your_dashscope_key
export QWEN_BASE_URL=https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1
export QWEN_MODEL=qwen-plus
export QWEN_EMBEDDING_MODEL=text-embedding-v4
export QWEN_EMBEDDING_DIMENSIONS=1024

export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=your_langsmith_key
export LANGSMITH_PROJECT=CrossBridge-RAG
```

### 3. 启动
```bash
# 命令行测试引擎
python rag_engine.py

# 启动网页 Demo
streamlit run app.py
```
浏览器打开 `http://localhost:8501` 即可。

---

## 当前运行模式

| 条件 | 效果 |
|---|---|
| 配置 DashScope + LangSmith key | Qwen embedding 检索 + Qwen 生成 + LangSmith trace |
| 缺少 key | 启动时报错,提示配置缺失的环境变量 |

> 路演忠告:当前版本为了可视化追踪和真实模型效果,不再静默降级为无 key 模式。正式演示前请提前确认香港 endpoint、DashScope key 和 LangSmith project 都可用。

---

## 下一步可以扩展什么

1. **换真实数据**:写爬虫抓 HKMA / 外管局 / 各国央行,替换 `knowledge_base.json`(保持字段格式一致即可)
2. **升级向量库**:把 `rag_engine.py` 里的内存检索换成 Chroma(注释已留好)
3. **加功能模块**:汇率对比(接汇率 API)、信贷预审(规则引擎 + 企业画像)
4. **多 Agent**:用 LangGraph 把"政策/财务/市场/信贷"拆成专职 Agent

---

## ⚠️ 重要提醒

- `knowledge_base.json` 里目前是**示例数据**,带 `disclaimer` 标记。**正式比赛/演示前必须替换为真实爬取的权威来源**,否则引用的"法规"是假的。
- 本工具定位为初步情报助手,**不取代法律或金融专业人士**。

# RAG LangChain + Qwen 改造记录

Last updated: 2026-05-25

## 本次改造目标

把原来的本地 RAG demo 改成:

```text
LangChain pipeline
+ Qwen text-embedding-v4 向量检索
+ Qwen qwen-plus 答案生成
+ LangSmith 可视化 tracing
```

本轮没有做 crawler,也没有接 Chroma/Milvus/pgvector。当前仍然使用内存向量索引,方便后续替换 index backend。

## 主要改动

### 1. Qwen 配置

`rag_engine.py` 新增默认配置:

```bash
QWEN_BASE_URL=https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
QWEN_EMBEDDING_MODEL=text-embedding-v4
QWEN_EMBEDDING_DIMENSIONS=1024
LANGSMITH_PROJECT=CrossBridge-RAG
```

API key 不写进代码,只从环境变量读取:

```bash
export DASHSCOPE_API_KEY=your_dashscope_key
export LANGSMITH_API_KEY=your_langsmith_key
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=CrossBridge-RAG
```

如果缺少 `DASHSCOPE_API_KEY` 或 `LANGSMITH_API_KEY`,程序会直接报错,避免静默降级。

### 2. Qwen Embeddings

原来的 `sentence-transformers` 路径已不再作为主路径使用。

现在 `VectorIndex` 使用 LangChain 的 `OpenAIEmbeddings`,通过阿里云百炼 OpenAI-compatible endpoint 调用:

```python
OpenAIEmbeddings(
    model="text-embedding-v4",
    dimensions=1024,
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url=QWEN_BASE_URL,
    check_embedding_ctx_length=False,
)
```

当前 index backend 名称:

```python
rag.index.backend == "qwen_embedding"
```

当前仍然是内存矩阵:

```text
docs -> Qwen embeddings -> normalized numpy matrix
query -> Qwen embedding -> cosine similarity
```

后续接 Chroma/Milvus/pgvector 时,只需要替换 `VectorIndex` adapter。

### 3. LangChain Pipeline

`CrossBridgeRAG.ask()` 现在调用 LangChain Runnable pipeline。

Trace 节点包括:

```text
PrepareInput
ParseStructuredQuery
RouteQuery
TransformQuery
SearchVariants
RRFFusion
MetadataScoring
BuildPrompt
GenerateAnswer
FormatOutput
```

这些节点会出现在 LangSmith trace 中,方便观察:

- query 被判成什么类型
- 生成了哪些 query variants
- 每个 variant 检索到哪些资料
- RRF 如何融合排序
- metadata scoring 如何调整分数
- 最终 prompt 和答案生成过程

### 4. Qwen Chat

答案生成也改成 LangChain 的 `ChatOpenAI`,同样走香港 endpoint:

```python
ChatOpenAI(
    model="qwen-plus",
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url=QWEN_BASE_URL,
    temperature=0.1,
)
```

原来的 Anthropic/OpenAI fallback 已移除。当前版本要求配置 Qwen 和 LangSmith key。

### 5. 保留的 Retrieval 逻辑

原来的 retrieval transformation 逻辑保留:

- `simple`
- `vague`
- `compound`
- `conceptual`
- `low_recall`
- multi-query
- decomposition
- step-back
- HyDE fallback
- RRF fusion

区别是现在这些步骤被 LangChain Runnable 包起来,可以被 LangSmith 追踪。

### 6. UI 和 README

`app.py` 只做了小改动:

- 侧边栏检索后端显示 `Qwen text-embedding-v4`

`README.md` 已更新:

- 删除旧的 Anthropic/OpenAI 配置说明
- 改成 DashScope/Qwen + LangSmith 环境变量说明
- 说明当前版本缺 key 会报错

## 新增依赖

`requirements.txt` 新增:

```text
langchain
langchain-core
langchain-openai
langsmith
```

`sentence-transformers` 和 `scikit-learn` 已不再是主流程必需依赖。

## 验证结果

已完成本地验证:

```bash
.venv/bin/python -m py_compile files/rag_engine.py files/app.py
.venv/bin/python -m pip check
```

结果:

```text
py_compile 通过
No broken requirements found
```

也用 dummy 环境变量验证过 LangChain client 可构造:

```text
OpenAIEmbeddings text-embedding-v4 1024
ChatOpenAI qwen-plus
```

没有使用真实 API key 发请求。

## 安全注意

不要把 API key 写进:

- `rag_engine.py`
- `README.md`
- `.json`
- Git commit
- 聊天记录

如果 key 已经暴露,建议立刻去对应平台 revoke/rotate。

## 后续预留空间

### 1. Index backend

当前 `VectorIndex` 是临时 adapter。后续可以替换为:

- Chroma
- Milvus
- pgvector
- FAISS

上层 LangChain pipeline 不需要大改。

### 2. Crawler

本轮没有做 crawler。后续 teammate 的 crawler 只需要产出结构化 JSON 文档。

建议未来文档 metadata 至少包含:

```text
id
title
content
source_name
source_url
region
topic
publish_date
effective_date
source_type
authority_level
disclaimer_level
last_checked_date
```

### 3. StructuredQuery

当前已有轻量 structured parsing:

- regions
- topics
- intent
- conflicts
- semantic_query

后续可以继续增强:

- source_type filter
- date filter
- authority filter
- region/topic conflict policy
- vector DB where filter 映射

### 4. Evaluation

建议下一步增加小型评测集,每条包含:

```text
question
expected_regions
expected_topics
expected_doc_ids
ideal_answer_notes
```

这样可以用 LangSmith 对比 retrieval 改动前后的表现。

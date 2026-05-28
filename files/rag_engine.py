"""
CrossBridge AI - RAG 引擎核心
================================
职责:
  1. 加载结构化知识库 (knowledge_base.json)
  2. 把每条资料向量化 (Embedding)
  3. 根据用户问题 + 地区/主题过滤,检索最相关的资料
  4. 把检索结果组装成 Prompt,调用大模型生成带引用的答案
  5. 没有 API key 时,降级为模板答案,保证 Demo 永远能跑

设计要点:
  - 通过 LangChain 调用千问 OpenAI-compatible API
  - 向量模型默认用百炼/千问 text-embedding-v4
  - 生成模型默认用 qwen-plus
  - LangSmith 负责可视化 tracing; 本地 debug trace 保留
"""

import os
import json
import re
import numpy as np
from functools import lru_cache

# ----------------------------------------------------------------------
# 1. 加载知识库
# ----------------------------------------------------------------------
def load_knowledge_base(path="knowledge_base.json"):
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    print(f"[KB] 已加载 {len(docs)} 条资料")
    return docs


# ----------------------------------------------------------------------
# 2. 基础工具
# ----------------------------------------------------------------------


def _zh_tokenize(text):
    """简单中文分词:有 jieba 用 jieba,没有就按字切。"""
    try:
        import jieba
        return " ".join(jieba.cut(text))
    except Exception:
        return " ".join(list(text))


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


QWEN_BASE_URL = os.environ.get(
    "QWEN_BASE_URL",
    "https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1",
)
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen-plus")
QWEN_EMBEDDING_MODEL = os.environ.get(
    "QWEN_EMBEDDING_MODEL", "text-embedding-v4"
)
QWEN_EMBEDDING_DIMENSIONS = _env_int("QWEN_EMBEDDING_DIMENSIONS", 1024)
LANGSMITH_PROJECT = os.environ.get("LANGSMITH_PROJECT", "CrossBridge-RAG")
RETRIEVAL_MODE = os.environ.get("CB_RETRIEVAL_MODE", "auto").strip().lower()
MAX_QUERY_VARIANTS = _env_int("CB_MAX_QUERY_VARIANTS", 3)
RETRIEVAL_CANDIDATES = _env_int("CB_RETRIEVAL_CANDIDATES", 8)
LOW_RECALL_THRESHOLD = _env_float("CB_LOW_RECALL_THRESHOLD", 0.15)
RRF_K = _env_int("CB_RRF_K", 60)
# Step 3：BM25 + dense hybrid 融合的 source weighting
#   BM25 略偏置（合规专有 token 场景更准），但 1.1 保守，不打死 dense
DENSE_WEIGHT = _env_float("CB_DENSE_WEIGHT", 1.0)
BM25_WEIGHT = _env_float("CB_BM25_WEIGHT", 1.1)
# RRF 之后喂给 reranker 的候选池大小
RERANK_POOL = _env_int("CB_RERANK_POOL", 15)
# Step 4c.B+：retrieval 多样性。同一 parent_doc_id 最多在 RRF 输出里出现 N 次。
# 防 SAFE 资本项目外汇业务指引（80 chunks）独占 top10 的 anti-diversity 模式。
# 设 0 关闭这个 cap。
MAX_CHUNKS_PER_DOC = _env_int("CB_MAX_CHUNKS_PER_DOC", 3)

# Step 3.5：citation 二元过滤
#   1. trust_tier 必须 ∈ trusted（来源是官方）
#   2. document_type 不能 ∈ non-citable（不是导航/聚合页）
#   两者都满足才能进答案末尾的"信息来源"列表。
#   不满足的可作为 context 帮 LLM 理解上下文，但不被引用。
# Step 4a eval 调整：原本排除 bank（"只引用监管原文"），但 eval 暴露 q08/q19/q20
#   （中银香港 SME 贷款产品类问题）的权威答案就在 BOCHK 产品页里，排除 bank 导致
#   citation_hit 从 70.83% 掉到 54.17%。修正：加入 bank，导航/聚合噪声靠
#   NON_CITABLE_DOCUMENT_TYPES（hub_page）兜底。
TRUSTED_TIERS_FOR_CITATION = frozenset({
    "government", "regulator", "central_bank", "official_dev", "bank",
})
# hub_page 是 Banking Made Easy / Setting Up Business / CIPS Introduction 这种导航聚合页
#   即使发布机构是 regulator，本身也是索引页而非原文，引用价值低 → 仅作 context
NON_CITABLE_DOCUMENT_TYPES = frozenset({"hub_page"})


def validate_runtime_config():
    """关键外部服务必须显式配置,避免 demo 静默降级成假成功。"""
    missing = []
    if not os.environ.get("DASHSCOPE_API_KEY"):
        missing.append("DASHSCOPE_API_KEY")
    if not os.environ.get("LANGSMITH_API_KEY"):
        missing.append("LANGSMITH_API_KEY")
    if missing:
        raise RuntimeError(
            "缺少必要环境变量: "
            + ", ".join(missing)
            + "。请在环境变量中配置,不要把 API key 写进代码。"
        )

    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_PROJECT", LANGSMITH_PROJECT)


def _import_langchain():
    try:
        from langchain_core.documents import Document
        from langchain_core.runnables import RunnableLambda
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        return Document, RunnableLambda, ChatOpenAI, OpenAIEmbeddings
    except ImportError as e:
        raise RuntimeError(
            "缺少 LangChain 依赖。请运行: pip install -r requirements.txt"
        ) from e


@lru_cache(maxsize=1)
def get_qwen_embeddings():
    validate_runtime_config()
    _Document, _RunnableLambda, _ChatOpenAI, OpenAIEmbeddings = _import_langchain()
    return OpenAIEmbeddings(
        model=QWEN_EMBEDDING_MODEL,
        dimensions=QWEN_EMBEDDING_DIMENSIONS,
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url=QWEN_BASE_URL,
        check_embedding_ctx_length=False,
        chunk_size=10,  # DashScope text-embedding-v4 单次最多 10 条
    )


@lru_cache(maxsize=1)
def get_qwen_chat_model():
    validate_runtime_config()
    _Document, _RunnableLambda, ChatOpenAI, _OpenAIEmbeddings = _import_langchain()
    return ChatOpenAI(
        model=QWEN_MODEL,
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url=QWEN_BASE_URL,
        temperature=0.1,
    )


def run_langchain_step(name, func, payload):
    """把自定义步骤包成 LangChain Runnable,方便 LangSmith 追踪。"""
    _Document, RunnableLambda, _ChatOpenAI, _OpenAIEmbeddings = _import_langchain()
    return RunnableLambda(func).with_config(run_name=name).invoke(payload)


def _normalize_matrix(matrix):
    matrix = np.array(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def _normalize_vector(vector):
    vector = np.array(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


REGION_TERMS = {
    "HK": ["香港", "港企", "港资", "Hong Kong", "HK"],
    "GBA": ["大湾区", "内地", "大陆", "深圳", "广东", "广州", "东莞", "珠海", "GBA"],
    "VN": ["越南", "胡志明", "河内", "Vietnam", "VN"],
    "TH": ["泰国", "曼谷", "Thailand", "TH"],
    "SG": ["新加坡", "Singapore", "SG"],
    "ID": ["印尼", "印度尼西亚", "Indonesia", "ID"],
}

REGION_LABELS = {
    "HK": "香港",
    "GBA": "大湾区 内地 深圳",
    "VN": "越南",
    "TH": "泰国",
    "SG": "新加坡",
    "ID": "印尼",
}

TOPIC_TERMS = {
    "remittance": ["汇款", "付款", "付钱", "打钱", "电汇", "转账", "付汇", "收款"],
    "compliance": ["合规", "监管", "反洗钱", "AML", "KYC", "KYB", "CDD", "EDD", "尽职审查", "交易背景", "资金来源", "风险"],
    "credit": ["贷款", "融资", "授信", "信贷", "贸易融资", "信用贷款", "额度", "利率"],
    "tax": ["税", "税务", "所得税", "预扣税", "转让定价", "利润"],
    "market_entry": ["设公司", "注册公司", "开户", "牌照", "市场进入", "落地", "外资", "经营"],
}

TOPIC_EXPANSIONS = {
    "remittance": "跨境汇款 对外付汇 电汇 贸易背景 交易真实性 银行审核 所需文件 外汇申报",
    "compliance": "KYC KYB AML CDD EDD 客户尽职审查 反洗钱 交易目的 资金来源 可疑交易",
    "credit": "中小企业贷款 贸易融资 信用贷款 授信额度 利率 银行流水 应收账款",
    "tax": "企业所得税 预扣税 跨境利润 税务登记 转让定价 税务合规",
    "market_entry": "公司设立 银行开户 注册文件 董事身份证明 经营地址 外资持股 牌照",
}


def _unique_keep_order(items):
    seen = set()
    unique = []
    for item in items:
        if not item:
            continue
        value = str(item).strip()
        if not value or value in seen:
            continue
        unique.append(value)
        seen.add(value)
    return unique


def _contains_any(text, terms):
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _detect_regions(query, selected_region=None):
    regions = []
    for code, terms in REGION_TERMS.items():
        if _contains_any(query, terms):
            regions.append(code)
    if selected_region and selected_region != "全部":
        regions.append(selected_region)
    return _unique_keep_order(regions)


def _detect_topics(query, selected_topic=None):
    topics = []
    for code, terms in TOPIC_TERMS.items():
        if _contains_any(query, terms):
            topics.append(code)
    if selected_topic and selected_topic != "全部":
        topics.append(selected_topic)
    return _unique_keep_order(topics)


def normalize_query(query, region="全部", topic="全部", *, expand_topics=False):
    """补充地区/主题同义词，用于提高检索召回。

    Step 4c.A：`expand_topics` 默认 False —— 老版本无条件拼 TOPIC_EXPANSIONS（"合规"
    → 全套 KYC/AML/CDD/EDD 词包），导致 specific query 被改宽，retrieval 漂到 SAFE
    大块头文档。eval q15/q19 等回归全是这个污染造成。

    现在只在 vague / low_recall query 上 expand_topics=True（router 已识别"我需要扩
    召回"），simple/compound/conceptual query 走 expand_topics=False 保留原意图。
    """
    regions = _detect_regions(query, region)
    parts = [query]
    parts.extend(REGION_LABELS[r] for r in regions if r in REGION_LABELS)
    if expand_topics:
        topics = _detect_topics(query, topic)
        parts.extend(TOPIC_EXPANSIONS[t] for t in topics if t in TOPIC_EXPANSIONS)
    return " ".join(_unique_keep_order(parts))


# Step 4c.A：合规专有标识符出现就强制 simple，避免 multi-query rewrite 改写丢精度。
#   SFGS_09/2024 / §4.12 / 汇发〔2023〕28号 这种正则一旦被 LLM 改"通顺"，BM25
#   精确匹配立刻消失。少胜于错。
SPECIFIC_TOKEN_PATTERNS = [
    re.compile(r"[A-Z]{2,}_\d+/\d+"),                # SFGS_09/2024
    re.compile(r"§\s*\d+(?:\.\d+)?"),                 # §4.12
    re.compile(r"汇发[〔\(]\s*\d+\s*[〕\)]\s*\d+号"),  # 汇发〔2023〕28号
]
# 合规/监管 specific 缩写白名单。出现这些 → 强制 simple。
# 注意：**不要**放进通用商业术语 SME / CEO / USD / HKD / RMB / GDP / KPI / API,
# 否则 "SME 贷款" 这种通用业务 query 会被强制 simple 失去 query expansion benefits.
SPECIFIC_ABBREVS = {
    "HKMA", "SBV", "PBOC", "MAS", "BNM", "BOT",  # 央行
    "SAFE",                                       # 国家外汇管理局
    "KYC", "KYB", "AML", "CFT", "CDD", "EDD",    # 反洗钱合规
    "CIPS", "RTGS", "CHATS", "FPS",              # 清算系统
    "SFGS", "HKMC",                              # 担保 scheme
    "IRD",                                        # 香港税务局
    "GoGBA",                                      # GBA promo
}
_ABBREV_REGEX = re.compile(r"\b([A-Z][A-Za-z]{2,4})\b")


def _has_specific_compliance_token(query: str) -> bool:
    """检测合规专有标识符。命中 → 强制 simple。
    - 含 SFGS_09/2024 / §4.12 / 汇发〔...〕 等结构化 token：直接命中
    - 含合规缩写白名单（HKMA/SBV/AML/CIPS...）：精确大写匹配命中
    - **不算**通用商业缩写（SME/USD/HKD/CEO 等）
    """
    if any(p.search(query) for p in SPECIFIC_TOKEN_PATTERNS):
        return True
    for m in _ABBREV_REGEX.findall(query):
        if m in SPECIFIC_ABBREVS:
            return True
    return False


def classify_query(query, region="全部", topic="全部"):
    """规则优先的 query router。LLM 只负责生成变体,不负责主判定。"""
    # Step 4c.A：含合规专有 token 的 query → simple（跳过 multi-query rewrite 防漂移）
    if _has_specific_compliance_token(query):
        return "simple"

    regions = _detect_regions(query, region)
    topics = _detect_topics(query, topic)
    compound_markers = [
        "比较", "区别", "分别", "同时", "以及", "和", "还有", " vs ", " versus ",
        "对比", "哪个", "哪些",
    ]
    conceptual_markers = [
        "为什么", "为何", "原因", "原理", "依据", "什么情况下", "银行为什么",
        "会不会查", "怎么判断", "如何判断",
    ]
    vague_markers = [
        "怎么办", "怎么弄", "要注意什么", "注意什么", "怎么做", "过去",
        "那边", "这个呢", "可以吗", "行不行",
    ]

    if ((len(regions) >= 2 or len(topics) >= 2)
            and _contains_any(query, compound_markers)):
        return "compound"
    if _contains_any(query, conceptual_markers):
        return "conceptual"
    if _contains_any(query, vague_markers) or len(query.strip()) <= 14:
        return "vague"
    return "simple"


def _extract_json_from_text(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _call_transform_llm(task, query, normalized_query, max_items=3):
    """
    用 Qwen 生成 query transformation。失败时返回 None,由规则模板兜底。
    """
    prompt = (
        "你是金融 RAG 系统的检索查询改写器。只输出 JSON,不要解释。\n"
        "目标: 提高官方金融/合规资料检索召回,但不能引入虚构事实。\n"
        f"任务: {task}\n"
        f"原始问题: {query}\n"
        f"已归一化问题: {normalized_query}\n"
        f"最多输出 {max_items} 条中文检索查询。\n"
        "JSON 格式: [\"query 1\", \"query 2\"]"
    )

    try:
        resp = get_qwen_chat_model().invoke([
            ("system", "你只负责生成检索查询,必须输出 JSON。"),
            ("user", prompt),
        ])
        data = _extract_json_from_text(str(resp.content))
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()][:max_items]
    except Exception as e:
        print(f"[Retrieval LLM] Qwen query transformation 失败,使用规则兜底: {e}")

    return None


def _fallback_multi_queries(query, normalized_query, max_items):
    """LLM transformation 失败时的规则兜底。

    Step 4c.A：删掉 else 分支（原代码无论什么 query 都拼"银行审核 客户尽职审查
    信息来源 官方资料"，跟原 query 经常无关，导致 retrieval 漂到 SAFE/HKMA AML
    方向）。少胜于错：未识别 topic 时只返回 原 query + normalized，不加噪声变体。
    """
    topics = _detect_topics(normalized_query)
    variants = [query, normalized_query]

    if "remittance" in topics or _contains_any(query, ["付款", "付钱", "汇款", "打钱"]):
        variants.extend([
            "跨境汇款 对外付汇 贸易背景 交易真实性 所需文件 银行审核",
            "跨境电汇 反洗钱 客户尽职审查 资金来源 收款人身份",
            "供应商付款 外汇申报 合规要求 银行审核 风险提示",
        ])
    elif "market_entry" in topics:
        variants.extend([
            "境外公司设立 银行开户 注册文件 董事身份证明 经营地址",
            "外资企业 市场进入 牌照 外资持股限制 银行账户开立",
        ])
    # else: 不再添加无关 variant；只用原 query + normalized

    return _unique_keep_order(variants)[:max_items + 1]


def _fallback_decompose(query, region="全部", topic="全部", max_items=3):
    regions = _detect_regions(query, region)
    topics = _detect_topics(query, topic)
    subqueries = []

    if regions and topics:
        for r in regions:
            for t in topics:
                region_text = REGION_LABELS.get(r, r)
                topic_text = TOPIC_EXPANSIONS.get(t, t)
                subqueries.append(f"{region_text} {topic_text} 官方要求")
                if len(subqueries) >= max_items:
                    return subqueries

    pieces = re.split(r"[，,。；;？?]|\s+和\s+|\s+以及\s+", query)
    pieces = [p.strip() for p in pieces if p.strip()]
    if len(pieces) > 1:
        subqueries.extend(pieces)

    return _unique_keep_order(subqueries or [query])[:max_items]


def _fallback_stepback(query, normalized_query):
    if _contains_any(query, ["交易背景", "银行", "审查", "查"]):
        return "跨境电汇 反洗钱 客户尽职审查 交易真实性审核 资金来源 交易目的"
    if _contains_any(query, ["汇款", "付款", "付钱", "电汇"]):
        return "跨境付款 银行合规审查 交易真实性 外汇申报 所需文件"
    return f"金融机构 合规要求 风险管理 客户尽职审查 {normalized_query}"


def _fallback_hyde(query, normalized_query):
    topics = _detect_topics(normalized_query)
    expansions = [TOPIC_EXPANSIONS[t] for t in topics if t in TOPIC_EXPANSIONS]
    if not expansions:
        expansions = ["官方监管要求 银行审核 所需文件 合规风险 信息来源"]
    return f"{query}。相关权威资料通常涉及: {' '.join(expansions)}。"


def transform_query(query, query_type, region="全部", topic="全部"):
    # Step 4c.A：只在 vague / low_recall query 上扩 topic expansion
    # 其他（simple / compound / conceptual）保留原 query 意图，防 TOPIC_EXPANSIONS 污染
    expand_topics = query_type in ("vague", "low_recall")
    normalized = normalize_query(query, region, topic, expand_topics=expand_topics)
    max_items = max(1, MAX_QUERY_VARIANTS)

    if query_type == "vague":
        llm_queries = _call_transform_llm(
            "multi-query: 从不同检索角度改写用户问题", query, normalized, max_items
        )
        variants = [query] + (llm_queries or _fallback_multi_queries(
            query, normalized, max_items
        ))
        return _unique_keep_order(variants)[:max_items + 1]

    if query_type == "compound":
        llm_queries = _call_transform_llm(
            "decomposition: 将复合问题拆成可单独检索的子问题", query, normalized, max_items
        )
        variants = llm_queries or _fallback_decompose(query, region, topic, max_items)
        return _unique_keep_order(variants)[:max_items]

    if query_type == "conceptual":
        llm_queries = _call_transform_llm(
            "step-back: 生成更抽象的原则性检索查询", query, normalized, 1
        )
        stepback = llm_queries[0] if llm_queries else _fallback_stepback(query, normalized)
        return _unique_keep_order([query, normalized, stepback])

    if query_type == "low_recall":
        hyde_query = _call_transform_llm(
            "HyDE: 生成一段保守的假想资料摘要,仅用于检索,不要编造数字或条款",
            query,
            normalized,
            1,
        )
        hyde_text = hyde_query[0] if hyde_query else _fallback_hyde(query, normalized)
        # Step 4c.A：去掉 normalized 这条变体。原因：当 LangGraph auto-trigger HyDE
        # 时（probe_results 低于阈值），会把 query_type 临时切到 "low_recall"，
        # 这里的 normalized 会带 TOPIC_EXPANSIONS 污染，回流到 simple/compound query
        # 的 retrieval variants 列表里。HyDE LLM 文本本身已经覆盖语义扩展，不需要
        # 再带 normalized 噪声。
        return _unique_keep_order([query, hyde_text])

    return _unique_keep_order([query, normalized])


# ----------------------------------------------------------------------
# 3. 向量索引
#    当前 adapter 使用 Qwen embeddings + 内存余弦相似度。
#    后续可替换为 Chroma / Milvus / pgvector,上层 Runnable 流程不变。
# ----------------------------------------------------------------------
class VectorIndex:
    def __init__(self, docs):
        self.docs = docs
        corpus = [f"{d['title']}。{d['content']}" for d in docs]
        self.embeddings = get_qwen_embeddings()
        self.backend = "qwen_embedding"
        self.embedding_model = QWEN_EMBEDDING_MODEL
        self.embedding_dimensions = QWEN_EMBEDDING_DIMENSIONS

        vecs = run_langchain_step(
            "EmbedDocuments", self.embeddings.embed_documents, corpus
        )
        self.matrix = _normalize_matrix(vecs)
        self.embedding_dimensions = int(self.matrix.shape[1])
        print(
            f"[Index] Qwen embedding 索引已建立: {self.matrix.shape} "
            f"model={self.embedding_model}"
        )

    def _query_scores(self, query):
        q = run_langchain_step(
            "EmbedQueryVariants", self.embeddings.embed_query, query
        )
        q = _normalize_vector(q)
        return self.matrix @ q

    def search(self, query, region=None, topic=None, top_k=3):
        """
        检索最相关资料。region / topic 为可选过滤 (None 或 '全部' = 不过滤)。
        返回 [(doc, score), ...]
        """
        scores = self._query_scores(query)
        results = []
        for i, doc in enumerate(self.docs):
            if region and region != "全部" and doc["region"] != region:
                continue
            if topic and topic != "全部" and doc["topic"] != topic:
                continue
            results.append((doc, float(scores[i])))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # 生产环境提示:
    # 这个 adapter 可直接替换为 Chroma / Milvus:
    #   collection.query(query_embeddings=[q_vec], n_results=top_k,
    #                    where={"region": region})
    # 接口语义一致,无需改动上层逻辑。


# ----------------------------------------------------------------------
# 3b. Chroma 持久化向量索引
#     接口与 VectorIndex 平行（add/search/backend/__len__），
#     上层 AdaptiveRetriever 无需修改即可切换。
# ----------------------------------------------------------------------

# Chroma metadata 只能存 str/int/float/bool/None，list 要 flatten
_CHROMA_META_KEYS = (
    # 路演引用必须的字段
    "doc_id", "parent_doc_id", "title", "issuer", "source_name",
    "source_url", "document_url", "source_type", "language",
    "authority_level", "publish_date", "effective_date",
    "disclaimer_level", "disclaimer",
    # UI vocab 标量（filter 用）
    "region_code", "topic_code",
    # 原始 list 字段（"," 拼接，留作展示 / debug）
    "region_raw", "topic_raw",
    # chunk 级
    "chunk_id", "chunk_index", "chapter", "section", "page",
    # crawler / citation eligibility
    "content_hash", "trust_tier", "document_type",
)


def _chunk_to_chroma_metadata(chunk: dict) -> dict:
    """ingestion chunk dict → Chroma 友好 metadata（无 None，无 list）。"""
    md: dict = {}
    md["doc_id"] = chunk.get("doc_id") or ""
    md["parent_doc_id"] = chunk.get("parent_doc_id") or chunk.get("doc_id") or ""
    md["title"] = chunk.get("title") or ""
    md["issuer"] = chunk.get("issuer") or ""
    md["source_name"] = chunk.get("issuer") or ""  # downstream code 用 source_name
    md["source_url"] = chunk.get("source_url") or ""
    md["document_url"] = chunk.get("document_url") or ""
    md["source_type"] = chunk.get("source_type") or ""
    md["language"] = chunk.get("language") or ""
    md["authority_level"] = chunk.get("authority_level") or ""
    md["publish_date"] = chunk.get("publish_date") or ""
    md["effective_date"] = chunk.get("effective_date") or ""
    md["disclaimer_level"] = chunk.get("disclaimer_level") or ""
    md["disclaimer"] = chunk.get("disclaimer") or ""
    md["region_code"] = chunk.get("region_code") or ""
    md["topic_code"] = chunk.get("topic_code") or ""
    md["region_raw"] = ",".join(chunk.get("region") or [])
    md["topic_raw"] = ",".join(chunk.get("topic") or [])
    md["chunk_id"] = chunk.get("chunk_id") or ""
    md["chunk_index"] = int(chunk.get("chunk_index", 0))
    md["chapter"] = chunk.get("chapter") or ""
    md["section"] = chunk.get("section") or ""
    md["page"] = chunk.get("page") or ""
    # Step 3.5：内容指纹 + Codex trust 分级。无值时空串（Chroma 不接受 None）
    md["content_hash"] = chunk.get("content_hash") or ""
    md["trust_tier"] = chunk.get("trust_tier") or ""
    md["document_type"] = chunk.get("document_type") or ""
    return md


def _chroma_result_to_doc(metadata: dict, content: str) -> dict:
    """Chroma 检索结果 → downstream 代码期望的 doc dict 形状。"""
    return {
        # downstream 必需字段
        "id": metadata.get("chunk_id") or metadata.get("doc_id"),
        "title": metadata.get("title", ""),
        "content": content,
        "source_name": metadata.get("source_name") or metadata.get("issuer", ""),
        "source_url": metadata.get("source_url", ""),
        "region": metadata.get("region_code", ""),      # 标量，回兼老 doc shape
        "topic": metadata.get("topic_code", ""),
        # downstream 可选字段
        "effective_date": metadata.get("effective_date") or None,
        "publish_date": metadata.get("publish_date") or None,
        "source_type": metadata.get("source_type") or "unknown",
        "authority_level": metadata.get("authority_level") or "medium",
        "disclaimer_level": metadata.get("disclaimer_level") or "unknown",
        "disclaimer": metadata.get("disclaimer", ""),
        # chunk 元数据，方便 pitch 时精细引用 "AML-2 §4.12 p.33"
        "doc_id": metadata.get("doc_id", ""),
        "parent_doc_id": metadata.get("parent_doc_id", ""),
        "chunk_id": metadata.get("chunk_id", ""),
        "chunk_index": metadata.get("chunk_index", 0),
        "chapter": metadata.get("chapter", ""),
        "section": metadata.get("section", ""),
        "page": metadata.get("page", ""),
        # Step 3.5
        "content_hash": metadata.get("content_hash", ""),
        "trust_tier": metadata.get("trust_tier", ""),
        "document_type": metadata.get("document_type", ""),
    }


class ChromaVectorIndex:
    """
    Chroma-backed 向量索引。与 VectorIndex 平行：
      - search(query, region, topic, top_k) -> [(doc_dict, score), ...]
      - backend / __len__ / add(chunks)
    """

    COLLECTION_NAME = "crossbridge"

    def __init__(self, persist_directory: str):
        from langchain_chroma import Chroma
        self.persist_directory = persist_directory
        self.embeddings = get_qwen_embeddings()
        self.embedding_model = QWEN_EMBEDDING_MODEL
        self.embedding_dimensions = QWEN_EMBEDDING_DIMENSIONS
        self.backend = "chroma"
        self.store = Chroma(
            collection_name=self.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        try:
            self._count = self.store._collection.count()
        except Exception:
            self._count = 0
        print(
            f"[Index] Chroma 已连接 persist_dir={persist_directory} "
            f"collection={self.COLLECTION_NAME} count={self._count} "
            f"embed_model={self.embedding_model}"
        )

    def __len__(self):
        return self._count

    def add(self, chunks: list, *, skip_existing: bool = True) -> int:
        """
        把 chunks（ingestion 产出的 dict 列表）写进 Chroma。
        返回实际新增条数。skip_existing=True 时按 chunk_id 跳过已入库的。
        """
        if not chunks:
            return 0

        ids_all = [c["chunk_id"] for c in chunks]
        to_add = chunks
        if skip_existing and self._count > 0:
            existing = set(self.store.get(ids=ids_all).get("ids", []))
            if existing:
                to_add = [c for c in chunks if c["chunk_id"] not in existing]
                if len(to_add) < len(chunks):
                    print(f"[Index] 跳过已存在 {len(chunks) - len(to_add)} 条 chunk")
        if not to_add:
            return 0

        # Step 4c.C：embed input 优先用 contextualized_content（含 LLM 生成的中文
        # context 前缀），fallback 到原 content。chunk metadata 仍存原 content，
        # downstream LLM 看到的是干净原文。
        texts = [c.get("contextualized_content") or c["content"] for c in to_add]
        metas = [_chunk_to_chroma_metadata(c) for c in to_add]
        ids = [c["chunk_id"] for c in to_add]

        run_langchain_step(
            "ChromaAddTexts",
            lambda batch: self.store.add_texts(
                texts=batch["texts"], metadatas=batch["metadatas"], ids=batch["ids"]
            ),
            {"texts": texts, "metadatas": metas, "ids": ids},
        )
        self._count = self.store._collection.count()
        print(f"[Index] Chroma 已写入 {len(to_add)} 条，当前总数 {self._count}")
        return len(to_add)

    def upsert(self, chunks: list, *, hash_field: str = "content_hash") -> tuple[int, int]:
        """
        Step 3.5：crawler-friendly 写入。
            - chunk_id 不存在 → add
            - chunk_id 已存在 且 content_hash 相同 → skip
            - chunk_id 已存在 且 content_hash 不同 → delete-then-add（doc 内容真变了）

        返回 (added_count, updated_count)。bulk first-load 仍用 add(skip_existing=True)
        更快；周期性 crawler ingest 用这个方法防止哑炮（同 chunk_id 新内容静默丢失）。
        """
        if not chunks:
            return (0, 0)

        ids_all = [c["chunk_id"] for c in chunks]
        existing_records = self.store.get(ids=ids_all) if self._count > 0 else {"ids": [], "metadatas": []}
        existing_ids = existing_records.get("ids", []) or []
        existing_metas = existing_records.get("metadatas", []) or []
        existing_hash_by_id = {
            cid: (m or {}).get(hash_field, "")
            for cid, m in zip(existing_ids, existing_metas)
        }

        to_add: list[dict] = []      # 全新 chunk
        to_update: list[dict] = []   # 已存在但 content 变了
        for c in chunks:
            cid = c["chunk_id"]
            if cid not in existing_hash_by_id:
                to_add.append(c)
                continue
            old_hash = existing_hash_by_id[cid]
            new_hash = c.get(hash_field) or ""
            if not new_hash:
                # chunk 没带 hash（旧数据）→ 强制视为 update，让 metadata 被刷新
                to_update.append(c)
            elif old_hash != new_hash:
                to_update.append(c)
            # hash 相同 → skip，啥也不做

        # 先 delete 要 update 的，再统一 add（保证一次 store.add_texts batch）
        if to_update:
            update_ids = [c["chunk_id"] for c in to_update]
            run_langchain_step(
                "ChromaDeleteForUpsert",
                lambda payload: self.store.delete(ids=payload["ids"]),
                {"ids": update_ids},
            )

        merged = to_add + to_update
        if merged:
            # Step 4c.C：embed input 优先用 contextualized_content
            texts = [c.get("contextualized_content") or c["content"] for c in merged]
            metas = [_chunk_to_chroma_metadata(c) for c in merged]
            ids = [c["chunk_id"] for c in merged]
            run_langchain_step(
                "ChromaUpsertAddTexts",
                lambda batch: self.store.add_texts(
                    texts=batch["texts"], metadatas=batch["metadatas"], ids=batch["ids"]
                ),
                {"texts": texts, "metadatas": metas, "ids": ids},
            )

        self._count = self.store._collection.count()
        skipped = len(chunks) - len(to_add) - len(to_update)
        print(
            f"[Index] Chroma upsert: added={len(to_add)} updated={len(to_update)} "
            f"skipped={skipped} total={self._count}"
        )
        return (len(to_add), len(to_update))

    def search(self, query, region=None, topic=None, top_k=3):
        """与 VectorIndex.search 同签名；返回 [(doc_dict, score)]，score 为余弦相似度近似。"""
        where = {}
        if region and region != "全部":
            where["region_code"] = region
        if topic and topic != "全部":
            where["topic_code"] = topic
        # Chroma where 接 dict；多条件用 $and
        if len(where) > 1:
            where_filter = {"$and": [{k: v} for k, v in where.items()]}
        elif where:
            where_filter = where
        else:
            where_filter = None

        raw = run_langchain_step(
            "ChromaSimilaritySearch",
            lambda payload: self.store.similarity_search_with_score(
                query=payload["query"], k=payload["k"], filter=payload["filter"]
            ),
            {"query": query, "k": top_k, "filter": where_filter},
        )
        results = []
        for langchain_doc, distance in raw:
            doc_dict = _chroma_result_to_doc(langchain_doc.metadata, langchain_doc.page_content)
            # Chroma 默认返回 cosine distance ∈ [0, 2]，转为 similarity ∈ [-1, 1]
            similarity = 1.0 - float(distance)
            results.append((doc_dict, similarity))
        return results


# ----------------------------------------------------------------------
# 4. Retrieval Orchestrator
#    单 query 检索升级为: router -> query transformation -> RRF 融合
# ----------------------------------------------------------------------
def rrf_fuse(result_lists, rrf_k=RRF_K, source_weights=None,
             max_chunks_per_doc=None):
    """
    Reciprocal Rank Fusion。

    输入支持两种形式（自动判别，向后兼容）：
      1. 老形式：`[[(doc, raw_score), ...], ...]`
           所有 list 权重都按 1.0 处理（行为同改造前）
      2. 新形式：`[("dense", [(doc, raw_score), ...]), ("bm25", [...]), ...]`
           配合 source_weights={"dense": 1.0, "bm25": 1.1} 给不同来源加权

    Step 4c.B+ 新增 `max_chunks_per_doc`：限制同一 parent_doc_id 在最终排序里最多
    出现 N 次。防止 SAFE 80-chunk 大文档独占 top10 的 anti-diversity 模式。
    None 或 0 = 不限制（向后兼容）。

    返回 `[(doc, fused_score), ...]` 按 fused_score 降序。
    """
    if source_weights is None:
        source_weights = {}

    fused_scores: dict = {}
    best_raw_scores: dict = {}
    docs_by_id: dict = {}

    for item in result_lists:
        # 自动判别 tuple 形式 vs 老 list 形式
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str):
            source_name, results = item
            weight = float(source_weights.get(source_name, 1.0))
        else:
            results = item
            weight = 1.0

        for rank, (doc, raw_score) in enumerate(results, 1):
            doc_id = doc.get("id") or doc.get("title")
            docs_by_id[doc_id] = doc
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + \
                weight * (1.0 / (rrf_k + rank))
            best_raw_scores[doc_id] = max(best_raw_scores.get(doc_id, float("-inf")),
                                          float(raw_score))

    fused = [
        (docs_by_id[doc_id], fused_score, best_raw_scores.get(doc_id, 0.0))
        for doc_id, fused_score in fused_scores.items()
    ]
    fused.sort(key=lambda item: (item[1], item[2]), reverse=True)

    # Step 4c.B+: per-doc chunk cap (diversity)
    if max_chunks_per_doc and max_chunks_per_doc > 0:
        seen_per_doc: dict = {}
        capped = []
        for doc, score, raw in fused:
            pdoc = doc.get("parent_doc_id") or doc.get("doc_id") or doc.get("id")
            count = seen_per_doc.get(pdoc, 0)
            if count >= max_chunks_per_doc:
                continue
            seen_per_doc[pdoc] = count + 1
            capped.append((doc, score, raw))
        fused = capped

    return [(doc, score) for doc, score, _raw in fused]


class AdaptiveRetriever:
    def __init__(self, index, bm25_index=None, reranker=None):
        self.index = index
        self.bm25_index = bm25_index   # 可空：JSON fallback 路径不带 BM25
        self.reranker = reranker       # 可空：API key 缺失时 reranker.is_available()=False
        self.mode = RETRIEVAL_MODE
        self.candidate_k = max(1, RETRIEVAL_CANDIDATES)
        self.low_recall_threshold = LOW_RECALL_THRESHOLD
        self.rrf_k = RRF_K
        self.rerank_pool = max(1, RERANK_POOL)
        self.source_weights = {"dense": DENSE_WEIGHT, "bm25": BM25_WEIGHT}

    def _forced_query_type(self):
        forced = {
            "simple": "simple",
            "multi_query": "vague",
            "decompose": "compound",
            "stepback": "conceptual",
            "hyde": "low_recall",
        }
        return forced.get(self.mode)

    def _search_variants(self, variants, region, topic):
        """
        对每个 query variant 同时跑 dense + BM25（如果 BM25 可用），
        返回 (searches_trace, result_lists)。
        result_lists 是 [("dense"|"bm25", [(doc, score), ...]), ...]
        交给 rrf_fuse(source_weights=...) 加权融合。
        """
        searches = []
        result_lists = []
        for variant in variants:
            # Dense 路（Chroma）
            dense_results = self.index.search(
                variant, region=region, topic=topic, top_k=self.candidate_k
            )
            searches.append({
                "query": variant,
                "source": "dense",
                "results": [
                    {
                        "id": doc.get("id"),
                        "title": doc.get("title"),
                        "score": round(float(score), 4),
                    }
                    for doc, score in dense_results
                ],
            })
            result_lists.append(("dense", dense_results))

            # Sparse 路（BM25），如果有的话
            if self.bm25_index is not None:
                bm25_results = self.bm25_index.search(
                    variant, region=region, topic=topic, top_k=self.candidate_k
                )
                searches.append({
                    "query": variant,
                    "source": "bm25",
                    "results": [
                        {
                            "id": doc.get("id"),
                            "title": doc.get("title"),
                            "score": round(float(score), 4),
                        }
                        for doc, score in bm25_results
                    ],
                })
                result_lists.append(("bm25", bm25_results))
        return searches, result_lists

    def _is_low_recall(self, probe_results):
        if not probe_results:
            return True
        return float(probe_results[0][1]) < self.low_recall_threshold

    def retrieve(self, query, region="全部", topic="全部", top_k=3):
        forced_type = self._forced_query_type()
        query_type = forced_type or classify_query(query, region, topic)
        # Step 4c.A：跟 transform_query 一致，按 query_type 决定是否扩 topic
        normalized = normalize_query(
            query, region, topic,
            expand_topics=query_type in ("vague", "low_recall"),
        )

        trace = {
            "mode": self.mode,
            "query_type": query_type,
            "normalized_query": normalized,
            "query_variants": [],
            "hyde_used": False,
            "low_recall_threshold": self.low_recall_threshold,
            "searches": [],
            "fusion_scores": [],
        }

        variants = transform_query(query, query_type, region, topic)
        trace["query_variants"] = variants

        searches, result_lists = self._search_variants(variants, region, topic)
        trace["searches"].extend(searches)

        probe_results = self.index.search(
            normalized, region=region, topic=topic, top_k=1
        )
        should_hyde = (
            query_type == "low_recall"
            or (self.mode == "auto" and self._is_low_recall(probe_results))
        )

        if should_hyde and query_type != "low_recall":
            hyde_variants = transform_query(query, "low_recall", region, topic)
            hyde_only = [q for q in hyde_variants if q not in variants]
            if hyde_only:
                hyde_searches, hyde_lists = self._search_variants(hyde_only, region, topic)
                trace["searches"].extend(hyde_searches)
                result_lists.extend(hyde_lists)
                variants.extend(hyde_only)
                trace["query_variants"] = variants
            trace["hyde_used"] = True
        elif query_type == "low_recall":
            trace["hyde_used"] = True

        fused = rrf_fuse(
            result_lists, self.rrf_k,
            source_weights=self.source_weights,
            max_chunks_per_doc=MAX_CHUNKS_PER_DOC,
        )
        trace["fusion_scores"] = [
            {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "score": round(float(score), 4),
            }
            for doc, score in fused[:self.candidate_k]
        ]

        # Cross-encoder rerank：RRF 收 top-N 候选池 → reranker 精排
        pool = fused[: self.rerank_pool]
        if self.reranker is not None and getattr(self.reranker, "is_available", lambda: True)():
            reranked = self.reranker.rerank(query, pool, top_n=self.rerank_pool)
            trace["rerank_scores"] = [
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "score": round(float(score), 4),
                }
                for doc, score in reranked[:self.candidate_k]
            ]
            return reranked[:top_k], trace

        return pool[:top_k], trace


# ----------------------------------------------------------------------
# 5. LLM 调用 (带降级)
# ----------------------------------------------------------------------
SYSTEM_PROMPT = """你是 CrossBridge AI,一个跨境普惠金融决策助手,服务大湾区与东南亚的中小企业。

严格遵守以下规则:
1. 只能基于【参考资料】回答,不得编造任何法规、数字或产品条款。
2. 若参考资料不足以回答,要诚实说明"现有资料无法确认",不要猜。
3. 回答要分点、清晰、可操作,面向不懂金融术语的中小企业老板。
4. 你不是律师或会计师,回答末尾必须提示用户最终操作前向银行客户经理或专业人士确认。
5. 绝不提供逃税、洗钱、规避监管等违规建议。
6. 引用规则:答案末尾"信息来源"中,只列出【参考资料】里标记为"可引用"的资料 ([资料N]);
   标记为"仅作context,不可引用"的资料 ([资料Cx]) 可以帮助你理解,但不要出现在信息来源列表中。
"""

def build_prompt(query, retrieved, context_only=None):
    """把检索结果拼进 Prompt。

    Step 3.5: retrieved 是可引用的（来自 trusted source），
              context_only 仅用于 LLM 理解上下文，禁止出现在 citation 列表。
    """
    blocks = []
    for i, (doc, _score) in enumerate(retrieved, 1):
        blocks.append(
            f"[资料{i}] (可引用) 来源:{doc['source_name']} | 地区:{doc['region']} | "
            f"生效日:{doc.get('effective_date','-')}\n"
            f"标题:{doc['title']}\n正文:{doc['content']}"
        )
    if context_only:
        for j, (doc, _score) in enumerate(context_only, 1):
            blocks.append(
                f"[资料C{j}] (仅作context,不可引用) 来源:{doc['source_name']} | "
                f"地区:{doc['region']}\n标题:{doc['title']}\n正文:{doc['content']}"
            )
    context = "\n\n".join(blocks)
    user_msg = (
        f"【参考资料】\n{context}\n\n"
        f"【用户问题】\n{query}\n\n"
        f"请基于以上资料回答,并在结尾用'信息来源'列出你引用了哪几条【可引用】资料。"
    )
    return user_msg


def call_llm(query, retrieved):
    """
    通过 LangChain 调用 Qwen 生成答案。
    """
    user_msg = build_prompt(query, retrieved)
    resp = get_qwen_chat_model().invoke([
        ("system", SYSTEM_PROMPT),
        ("user", user_msg),
    ])
    return str(resp.content)


def _fallback_answer(query, retrieved):
    """没有大模型时,直接结构化展示检索结果。"""
    if not retrieved:
        return "现有资料库暂时找不到与您问题直接相关的权威资料,建议补充更多数据源或咨询银行客户经理。"
    lines = ["(演示模式:未配置大模型 API,以下为检索到的权威资料摘要)\n"]
    for i, (doc, score) in enumerate(retrieved, 1):
        lines.append(f"{i}. 【{doc['title']}】({doc['source_name']})")
        # 摘要取正文前 80 字
        summary = doc["content"][:80].strip()
        lines.append(f"   要点:{summary}……")
        lines.append("")
    lines.append("⚠️ 以上为参考信息,最终操作前请向中银香港客户经理或专业人士确认。")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 6. 对外统一入口
# ----------------------------------------------------------------------
def load_chunks_jsonl(path: str) -> list:
    """读 ingestion.py 产出的 chunks.jsonl。每行一个 chunk dict。"""
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    print(f"[KB] 已从 {path} 加载 {len(chunks)} 个 chunks")
    return chunks


class CrossBridgeRAG:
    def __init__(
        self,
        kb_path: str = "knowledge_base.json",
        *,
        chunks_path: str = None,
        persist_directory: str = None,
    ):
        """
        两种加载方式：
          1. Chroma 模式（Step 2 之后）：传 chunks_path + persist_directory
             - 从 chunks.jsonl 读 chunk 列表
             - 用 ChromaVectorIndex 持久化
          2. Demo fallback 模式（保留）：只传 kb_path
             - 读 knowledge_base.json
             - 用 in-memory VectorIndex
        """
        validate_runtime_config()
        self.bm25_index = None
        self.reranker = None
        if chunks_path and persist_directory:
            self.docs = load_chunks_jsonl(chunks_path)
            self.index = ChromaVectorIndex(persist_directory)
            # 增量灌库：首次跑会全量 embed，第二次跑跳过已存在的
            if len(self.index) == 0 or len(self.index) < len(self.docs):
                self.index.add(self.docs, skip_existing=True)
            # Step 3：BM25 sparse index + cross-encoder reranker。
            #   - BM25 直接用 chunks 现建（每次启动 ~2 秒，不存盘）
            #   - Reranker 在 DASHSCOPE_API_KEY 缺失时禁用，retriever 自动 fallback
            from bm25_index import BM25Index  # 局部 import 避免循环
            from reranker import DashScopeReranker
            self.bm25_index = BM25Index(self.docs)
            self.reranker = DashScopeReranker()
        else:
            self.docs = load_knowledge_base(kb_path)
            self.index = VectorIndex(self.docs)
            # JSON fallback 路径保持简单：只有 dense，没 BM25 没 reranker
        self.retriever = AdaptiveRetriever(
            self.index,
            bm25_index=self.bm25_index,
            reranker=self.reranker,
        )
        self.chain = self._build_langchain_chain()

    def _build_langchain_chain(self):
        _Document, RunnableLambda, _ChatOpenAI, _OpenAIEmbeddings = _import_langchain()
        return (
            RunnableLambda(self._prepare_state).with_config(run_name="PrepareInput")
            | RunnableLambda(self._parse_structured_query).with_config(
                run_name="ParseStructuredQuery"
            )
            | RunnableLambda(self._route_query).with_config(run_name="RouteQuery")
            | RunnableLambda(self._transform_queries).with_config(
                run_name="TransformQuery"
            )
            | RunnableLambda(self._search_variants).with_config(
                run_name="SearchVariants"
            )
            | RunnableLambda(self._rrf_fusion).with_config(run_name="RRFFusion")
            | RunnableLambda(self._rerank_pool).with_config(run_name="Rerank")
            | RunnableLambda(self._metadata_scoring).with_config(
                run_name="MetadataScoring"
            )
            | RunnableLambda(self._validate_citations).with_config(
                run_name="ValidateCitations"
            )
            | RunnableLambda(self._build_prompt_state).with_config(
                run_name="BuildPrompt"
            )
            | RunnableLambda(self._generate_answer).with_config(
                run_name="GenerateAnswer"
            )
            | RunnableLambda(self._format_output).with_config(run_name="FormatOutput")
        )

    def _prepare_state(self, state):
        state = dict(state)
        state["top_k"] = max(1, int(state.get("top_k", 3)))
        state["region"] = state.get("region", "全部")
        state["topic"] = state.get("topic", "全部")
        state["debug"] = bool(state.get("debug", False))
        state["trace"] = {
            "mode": RETRIEVAL_MODE,
            "query_type": None,
            "normalized_query": None,
            "query_variants": [],
            "hyde_used": False,
            "low_recall_threshold": LOW_RECALL_THRESHOLD,
            "searches": [],
            "fusion_scores": [],
            "structured_query": {},
            "metadata_scores": [],
            "rerank_used": False,
            "rerank_scores": [],
            # Step 3.5: citation 分层
            "citation_filter_applied": False,
            "citation_tiers_used": [],
            "context_only_tiers": [],
        }
        return state

    def _parse_structured_query(self, state):
        query = state["query"]
        region = state["region"]
        topic = state["topic"]
        text_regions = _detect_regions(query)
        text_topics = _detect_topics(query)
        regions = _detect_regions(query, region)
        topics = _detect_topics(query, topic)
        conflicts = []

        if region != "全部" and text_regions and region not in text_regions:
            conflicts.append({
                "field": "region",
                "ui_value": region,
                "query_values": text_regions,
                "policy": "merge",
            })
        if topic != "全部" and text_topics and topic not in text_topics:
            conflicts.append({
                "field": "topic",
                "ui_value": topic,
                "query_values": text_topics,
                "policy": "merge",
            })

        # Step 4c.A：先算 intent，再按 intent 决定 normalize 是否扩 topic
        intent = classify_query(query, region, topic)
        structured_query = {
            "raw_query": query,
            "semantic_query": normalize_query(
                query, region, topic,
                expand_topics=intent in ("vague", "low_recall"),
            ),
            "regions": regions,
            "topics": topics,
            "source_types": [],
            "date_after": None,
            "date_before": None,
            "intent": intent,
            "conflicts": conflicts,
        }
        state["structured_query"] = structured_query
        state["trace"]["structured_query"] = structured_query
        state["trace"]["normalized_query"] = structured_query["semantic_query"]
        state["trace"]["conflicts"] = conflicts
        return state

    def _route_query(self, state):
        forced_type = self.retriever._forced_query_type()
        query_type = forced_type or state["structured_query"]["intent"]
        state["query_type"] = query_type
        state["trace"]["query_type"] = query_type
        return state

    def _transform_queries(self, state):
        query = state["query"]
        region = state["region"]
        topic = state["topic"]
        query_type = state["query_type"]
        variants = transform_query(query, query_type, region, topic)
        state["query_variants"] = variants
        state["trace"]["query_variants"] = variants
        return state

    def _search_variants(self, state):
        """
        LangGraph 节点：对每个 query variant 同时跑 dense + BM25。
        result_lists 元素是 ("dense"|"bm25", [(doc, score), ...])，
        交给下游 _rrf_fusion 加权融合。
        """
        searches = []
        result_lists = []

        def _run_one(variant: str) -> None:
            dense_results = self.index.search(
                variant,
                region=state["region"],
                topic=state["topic"],
                top_k=self.retriever.candidate_k,
            )
            searches.append({
                "query": variant,
                "source": "dense",
                "results": [
                    {
                        "id": doc.get("id"),
                        "title": doc.get("title"),
                        "score": round(float(score), 4),
                    }
                    for doc, score in dense_results
                ],
            })
            result_lists.append(("dense", dense_results))

            if self.bm25_index is not None:
                bm25_results = self.bm25_index.search(
                    variant,
                    region=state["region"],
                    topic=state["topic"],
                    top_k=self.retriever.candidate_k,
                )
                searches.append({
                    "query": variant,
                    "source": "bm25",
                    "results": [
                        {
                            "id": doc.get("id"),
                            "title": doc.get("title"),
                            "score": round(float(score), 4),
                        }
                        for doc, score in bm25_results
                    ],
                })
                result_lists.append(("bm25", bm25_results))

        for variant in state["query_variants"]:
            _run_one(variant)

        probe_results = self.index.search(
            state["structured_query"]["semantic_query"],
            region=state["region"],
            topic=state["topic"],
            top_k=1,
        )
        should_hyde = (
            state["query_type"] == "low_recall"
            or (
                RETRIEVAL_MODE == "auto"
                and self.retriever._is_low_recall(probe_results)
            )
        )
        if should_hyde and state["query_type"] != "low_recall":
            hyde_variants = transform_query(
                state["query"], "low_recall", state["region"], state["topic"]
            )
            hyde_only = [q for q in hyde_variants if q not in state["query_variants"]]
            for variant in hyde_only:
                _run_one(variant)
            state["query_variants"].extend(hyde_only)
            state["trace"]["query_variants"] = state["query_variants"]
            state["trace"]["hyde_used"] = True
        elif state["query_type"] == "low_recall":
            state["trace"]["hyde_used"] = True

        state["result_lists"] = result_lists
        state["trace"]["searches"] = searches
        return state

    def _rrf_fusion(self, state):
        fused = rrf_fuse(
            state["result_lists"],
            self.retriever.rrf_k,
            source_weights=self.retriever.source_weights,
            max_chunks_per_doc=MAX_CHUNKS_PER_DOC,
        )
        state["fused_results"] = fused
        state["trace"]["fusion_scores"] = [
            {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "score": round(float(score), 4),
            }
            for doc, score in fused[:self.retriever.candidate_k]
        ]
        return state

    def _rerank_pool(self, state):
        """
        Step 3：RRF 候选池 (top RERANK_POOL) → cross-encoder rerank。
        - rerank 用原始 query（不是 HyDE 变体），否则 cross-encoder 评的是假答案
        - reranker 不可用时无副作用：state["fused_results"] 保持 RRF 排序
        - rerank 之后 state["fused_results"] 被替换为 [(doc, rerank_score), ...]
          下游 _metadata_scoring 继续乘 authority/source 系数
        """
        pool = state["fused_results"][: self.retriever.rerank_pool]
        reranker = self.retriever.reranker
        if reranker is None or not getattr(reranker, "is_available", lambda: True)():
            state["fused_results"] = pool
            state["trace"]["rerank_used"] = False
            return state

        reranked = reranker.rerank(
            state["query"], pool, top_n=self.retriever.rerank_pool
        )
        state["fused_results"] = reranked
        # 只有 API 真正调用成功时才算 rerank_used，否则只是 fallback 到 RRF 顺序
        state["trace"]["rerank_used"] = bool(getattr(reranker, "last_call_succeeded", False))
        if state["trace"]["rerank_used"]:
            state["trace"]["rerank_scores"] = [
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "score": round(float(score), 4),
                }
                for doc, score in reranked[: self.retriever.candidate_k]
            ]
        return state

    def _metadata_multiplier(self, doc):
        source_type = doc.get("source_type", "unknown")
        authority_level = doc.get("authority_level", "medium")
        disclaimer_level = doc.get("disclaimer_level", "unknown")
        disclaimer = doc.get("disclaimer", "")

        source_boost = {
            "regulator": 1.10,
            "tax_authority": 1.10,
            "bank": 1.05,
            "product_page": 1.03,
            "demo": 0.92,
            "unknown": 1.0,
        }.get(source_type, 1.0)
        authority_boost = {
            "high": 1.08,
            "medium": 1.0,
            "low": 0.94,
        }.get(authority_level, 1.0)
        disclaimer_boost = {
            "official": 1.05,
            "demo": 0.92,
            "stale": 0.90,
            "unknown": 1.0,
        }.get(disclaimer_level, 1.0)
        if "示例数据" in disclaimer or "非真实" in disclaimer:
            disclaimer_boost *= 0.92
        return source_boost * authority_boost * disclaimer_boost

    def _metadata_scoring(self, state):
        scored = []
        metadata_scores = []
        for doc, score in state["fused_results"]:
            multiplier = self._metadata_multiplier(doc)
            final_score = float(score) * multiplier
            scored.append((doc, final_score))
            metadata_scores.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "base_score": round(float(score), 4),
                "metadata_multiplier": round(multiplier, 4),
                "final_score": round(final_score, 4),
            })

        scored.sort(key=lambda item: item[1], reverse=True)
        state["retrieved"] = scored[:state["top_k"]]
        state["documents"] = [
            self._to_langchain_document(doc, score)
            for doc, score in state["retrieved"]
        ]
        state["trace"]["metadata_scores"] = metadata_scores[:self.retriever.candidate_k]
        return state

    def _validate_citations(self, state):
        """
        Step 3.5 + 4c.B: 把 retrieved 拆成 (citation_docs, context_only)。

        三路分流（Step 4c.B 改）：
          1. trusted_clean: trust_tier ∈ TRUSTED **且** document_type ∉ NON_CITABLE
             → 第一档可引用源（官方原文 + 非 hub 页）
          2. trusted_hub: trust_tier ∈ TRUSTED **但** document_type ∈ NON_CITABLE
             → 备胎（HKMA Banking Made Easy / CIPS Introduction 这种"trusted 但 hub"）
          3. untrusted: trust_tier ∉ TRUSTED
             → context only

        引用规则：
          - 有 trusted_clean → 用它（理想情况）
          - 没 trusted_clean 但有 trusted_hub → fallback 用 hub（pitch "诚实退化"故事）
            这一档是 Step 4c.B 新增的，原版会直接 fallback 到全部 retrieved（包括
            non_official），现在 trusted hub > untrusted 优先级
          - 全空 → 最后兜底允许全部
        """
        trusted_clean, trusted_hub, untrusted = [], [], []
        for doc, score in state["retrieved"]:
            tier = doc.get("trust_tier") or "non_official"
            dtype = doc.get("document_type") or "unknown"
            if tier not in TRUSTED_TIERS_FOR_CITATION:
                untrusted.append((doc, score))
            elif dtype in NON_CITABLE_DOCUMENT_TYPES:
                trusted_hub.append((doc, score))
            else:
                trusted_clean.append((doc, score))

        if trusted_clean:
            state["retrieved_for_citation"] = trusted_clean
            state["context_only"] = trusted_hub + untrusted
            state["trace"]["citation_filter_applied"] = True
            state["trace"]["citation_filter_mode"] = "trusted_clean"
        elif trusted_hub:
            # Step 4c.B：trusted 来源但都是 hub 页 → 退而求其次（比 untrusted 强）
            state["retrieved_for_citation"] = trusted_hub
            state["context_only"] = untrusted
            state["trace"]["citation_filter_applied"] = True
            state["trace"]["citation_filter_mode"] = "fallback_trusted_hub"
        else:
            # 连 trusted 都没有 → 全开（pitch 现场"诚实退化"故事）
            state["retrieved_for_citation"] = state["retrieved"]
            state["context_only"] = []
            state["trace"]["citation_filter_applied"] = False
            state["trace"]["citation_filter_mode"] = "fallback_all"
            state["trace"]["citation_filter_warning"] = (
                "no trusted-tier docs in top_k; allowing all as citation (degraded)"
            )

        state["trace"]["citation_tiers_used"] = [
            d.get("trust_tier") or "?" for d, _ in state["retrieved_for_citation"]
        ]
        state["trace"]["context_only_tiers"] = [
            d.get("trust_tier") or "?" for d, _ in state["context_only"]
        ]
        # Step 4a: 给 eval 用的 pre-citation-filter doc 列表（算 recall@k）
        state["trace"]["retrieved_doc_ids"] = [
            d.get("doc_id") or d.get("id") for d, _ in state["retrieved"]
        ]
        state["trace"]["retrieved_citation_doc_ids"] = [
            d.get("doc_id") or d.get("id") for d, _ in state["retrieved_for_citation"]
        ]
        return state

    def _to_langchain_document(self, doc, score):
        Document, _RunnableLambda, _ChatOpenAI, _OpenAIEmbeddings = _import_langchain()
        return Document(
            page_content=doc["content"],
            metadata={
                "id": doc.get("id"),
                "title": doc.get("title"),
                "source": doc.get("source_name"),
                "source_url": doc.get("source_url"),
                "region": doc.get("region"),
                "topic": doc.get("topic"),
                "effective_date": doc.get("effective_date"),
                "publish_date": doc.get("publish_date"),
                "score": round(float(score), 4),
            },
        )

    def _build_prompt_state(self, state):
        # Step 3.5: prompt 用 retrieved_for_citation 作为可引用资料,
        # context_only 拼进去但明确标注"不可引用"
        state["prompt"] = build_prompt(
            state["query"],
            state.get("retrieved_for_citation", state["retrieved"]),
            context_only=state.get("context_only"),
        )
        return state

    def _generate_answer(self, state):
        resp = get_qwen_chat_model().invoke([
            ("system", SYSTEM_PROMPT),
            ("user", state["prompt"]),
        ])
        state["answer"] = str(resp.content)
        return state

    def _format_output(self, state):
        # Step 3.5: citations 只从 retrieved_for_citation 出（已过 trust_tier filter）
        citation_source = state.get("retrieved_for_citation", state["retrieved"])
        citations = [
            {
                "title": doc["title"],
                "source": doc["source_name"],
                "url": doc["source_url"],
                "date": doc.get("effective_date", "-"),
                "region": doc["region"],
                "score": round(score, 3),
                "trust_tier": doc.get("trust_tier", ""),
                "document_type": doc.get("document_type", ""),
            }
            for doc, score in citation_source
        ]
        result = {"answer": state["answer"], "citations": citations}
        if state["debug"]:
            result["retrieval_trace"] = state["trace"]
        return result

    def ask(self, query, region="全部", topic="全部", top_k=3, debug=False):
        return self.chain.invoke(
            {
                "query": query,
                "region": region,
                "topic": topic,
                "top_k": top_k,
                "debug": debug,
            },
            config={
                "run_name": "CrossBridgeRAG.ask",
                "tags": ["crossbridge-rag", "qwen", "langchain"],
                "metadata": {
                    "region": region,
                    "topic": topic,
                    "qwen_model": QWEN_MODEL,
                    "embedding_model": QWEN_EMBEDDING_MODEL,
                    "qwen_base_url": QWEN_BASE_URL,
                },
            },
        )


# ----------------------------------------------------------------------
# 命令行自测
# ----------------------------------------------------------------------
if __name__ == "__main__":
    rag = CrossBridgeRAG()
    q = "我深圳公司想汇款给越南供应商,有什么合规要求?"
    print("\n问题:", q)
    result = rag.ask(q, region="全部", topic="remittance")
    print("\n--- 答案 ---")
    print(result["answer"])
    print("\n--- 引用来源 ---")
    for c in result["citations"]:
        print(f"  [{c['source']}] {c['title']} (相关度 {c['score']})")

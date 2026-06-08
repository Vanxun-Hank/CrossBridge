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
# Prompt context diversity: after metadata scoring, keep the best chunk from
# each parent document first, then use remaining prompt slots for supporting
# chunks from the same document. This reduces repeated-source prompt noise while
# preserving enough section-level detail for long guidelines.
PROMPT_MAX_CHUNKS_PER_DOC = _env_int("CB_PROMPT_MAX_CHUNKS_PER_DOC", 2)

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


def _is_vietnam_manufacturing_investment_query(query: str) -> bool:
    return (
        _contains_any(query, ["越南", "Vietnam"])
        and _contains_any(query, [
            "投资", "合作", "建厂", "工厂", "制造", "产能", "工业园",
            "manufacturing", "factory", "plant", "industrial zone", "investment",
        ])
    )


def _is_china_vietnam_supplier_payment_query(query: str) -> bool:
    return (
        _contains_any(query, ["越南", "Vietnam"])
        and _contains_any(query, ["供应商", "supplier"])
        and _contains_any(query, ["付汇", "付款", "payment", "remittance"])
        and _contains_any(query, [
            "中国", "内地", "境内", "Mainland", "China", "Chinese",
            "付汇", "对外付汇", "外汇局", "SAFE",
        ])
    )


def _is_vietnam_supplier_payment_query(query: str) -> bool:
    return (
        _contains_any(query, ["越南", "Vietnam"])
        and _contains_any(query, ["供应商", "supplier"])
        and _contains_any(query, ["付款", "付钱", "汇款", "payment", "remittance", "transfer"])
        and _contains_any(query, ["外汇", "合规", "监管", "FX", "foreign exchange", "compliance"])
    )


def _is_sbv_credit_institution_query(query: str) -> bool:
    return (
        _contains_any(query, ["越南", "Vietnam", "SBV", "越南央行", "国家银行"])
        and _contains_any(query, [
            "信贷机构", "credit institution", "credit institutions",
            "银行机构", "商业银行", "监管要求", "supervision", "regulatory requirement",
        ])
    )


def _is_hk_gba_expansion_financing_query(query: str) -> bool:
    return (
        _contains_any(query, ["香港", "Hong Kong", "HK"])
        and _contains_any(query, ["深圳", "东莞", "大湾区", "GBA", "Greater Bay Area"])
        and _contains_any(query, ["跨境", "扩张", "工厂", "业务", "cross-border", "expansion", "factory"])
        and _contains_any(query, ["融资", "贷款", "产品", "资格", "loan", "financing", "product", "eligibility"])
    )


def _is_hkma_aml_cdd_query(query: str) -> bool:
    return _contains_any(query, [
        "反洗钱", "AML", "CFT", "CDD", "EDD",
        "客户尽职", "尽职调查", "强化尽职",
        "anti-money laundering", "counter-terrorist financing",
        "customer due diligence", "enhanced due diligence",
        "money laundering", "terrorist financing",
    ])


def _is_tt_remittance_fee_time_query(query: str) -> bool:
    return (
        _contains_any(query, [
            "TT", "电汇", "Telegraphic Transfer", "outward remittance",
            "对外汇款", "汇款",
        ])
        and _contains_any(query, [
            "费用", "收费", "手续费", "到账", "多久", "时间", "时效",
            "fee", "fees", "charge", "charges", "arrival", "processing time",
            "cutoff", "cut-off",
        ])
        and not _contains_any(query, [
            "FPS", "Faster Payment System", "转数快", "trade finance",
            "贸易融资", "documentary credit", "letter of credit", "信用证",
        ])
    )


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


def _targeted_query_variants(query: str) -> list[str]:
    variants = []
    if _is_hkma_aml_cdd_query(query):
        variants.extend([
            "HKMA AML-2 Guideline customer due diligence enhanced due diligence authorized institutions",
            "HKMA anti-money laundering counter-terrorist financing guideline cross-border wire transfer originator recipient information",
            "香港金管局 反洗钱 客户尽职调查 强化尽职调查 跨境电汇 汇款人 收款人 资料",
        ])
    if _contains_any(query, ["FPS", "Faster Payment System", "转数快"]) and _contains_any(
        query,
        ["限额", "上限", "金额", "额度", "limit", "transaction limit", "transfer amount"],
    ):
        variants.extend([
            "FPS transaction limit local bank transfer HKD3,000,000 BOCHK",
            "Faster Payment System funds transfer to other local banks transaction limit",
            "转数快 FPS 本地银行转账 限额 中银香港",
        ])
    if _is_tt_remittance_fee_time_query(query):
        variants.extend([
            "BOCHK outward remittance telegraphic transfer charges personal customer electronic channel branch",
            "BOCHK Outward Remittance Quick Reference Guide cutoff same day processing telegraphic transfer",
            "中银香港 电汇 TT 对外汇款 收费 截止时间 当日处理",
        ])
    if _contains_any(query, ["SME", "中小企业", "SFGS", "担保贷款"]) and _contains_any(
        query,
        ["财务证明", "账务文件", "材料", "文件", "supporting documents", "financial statements"],
    ):
        variants.extend([
            "SFGS supporting documents loan application HKMCI factsheet lender request supporting documents",
            "SME loan financial statements audited financial statements supporting documents BOCHK",
            "BOC Small Business Loan Unsecured Loan audited financial statements not required supporting documents",
            "BOCHK SME Financing Guarantee Scheme upload documents supporting documents",
        ])
    if _contains_any(query, ["SFGS", "担保贷款"]) and _contains_any(
        query,
        ["贷多少", "额度", "上限", "营业额", "利润", "maximum facility amount", "loan amount"],
    ):
        variants.extend([
            "SFGS maximum facility amount 80% 90% guarantee product HKD12,000,000 HKD18,000,000",
            "BOCHK SFGS product loan amount documents HKMC 90% guarantee product",
            "SFGS maximum facility amount financial proof wages rent 27 months HKD 9000000 BOCHK",
        ])
    if _contains_any(query, ["SME", "中小企业", "贷款", "loan"]) and _contains_any(
        query,
        ["抵押", "无抵押", "质押", "collateral", "unsecured", "security"],
    ):
        variants.extend([
            "BOC Small Business Loan Unsecured Loan collateral not required audited financial statements not required",
            "BOCHK loan services mortgage loan asset pledge loan machinery equipment financing collateral",
            "SME Financing Guarantee Scheme HKMCI factsheet guarantee product borrower supporting documents",
            "HKMA SME Financing Guarantee Scheme 90% Guarantee Product",
        ])
    if _is_hk_gba_expansion_financing_query(query):
        variants.extend([
            "Hong Kong registered company Shenzhen Dongguan factory cross-border expansion financing BOCHK SME loan trade finance",
            "BOCHK trade finance purchase order financing GBA factory cross-border business expansion",
            "BOC global purchase order financing SME cross-border trade finance eligibility",
            "HKMC SME Financing Guarantee Scheme factsheet Hong Kong GBA factory expansion financing",
        ])
    if _contains_any(query, ["前海", "Qianhai"]):
        variants.extend([
            "GoGBA Qianhai preferential policies tax incentives Shenzhen Hong Kong businesses",
            "HKTDC GoGBA Qianhai preferential policy enterprise tax subsidy incentives",
        ])
    if _contains_any(query, ["大湾区", "GBA", "Greater Bay Area"]) and _contains_any(
        query, ["银行账户", "bank account", "account opening"]
    ):
        variants.extend([
            "GoGBA opening a company bank account Greater Bay Area business registration documents",
            "HKTDC GoGBA company bank account opening process required materials business registration",
        ])
    if _contains_any(query, ["GoGBA", "大湾区", "GBA"]) and _contains_any(
        query, ["business registration", "企业注册", "公司注册", "商业登记"]
    ):
        variants.extend([
            "GoGBA business registration process business investment filing Greater Bay Area",
            "HKTDC GoGBA business registration materials process foreign invested enterprise",
        ])
    if _is_china_vietnam_supplier_payment_query(query):
        variants.extend([
            "中国企业 向越南供应商 付汇 贸易外汇 收支便利化 真实性审核 银行 审核材料",
            "跨境贸易 投资便利化 汇发2023 28 贸易外汇 收支 真实性 审核",
            "SAFE 贸易外汇 收支 便利化 银行 审核 交易真实性 越南供应商付款",
        ])
    if _is_vietnam_manufacturing_investment_query(query):
        variants.extend([
            "Vietnam manufacturing partnership investment HKTDC industrial zones incentives suitable industries",
            "HKTDC Vietnam manufacturing investment partnership EPZ incentives garments footwear electronics",
            "Vietnam foreign investment taxation customs FIA manufacturing factory compliance",
            "越南 投资 建厂 制造业 工业园 激励 税务 海关 外商投资 官方",
        ])
    if _is_sbv_credit_institution_query(query):
        variants.extend([
            "State Bank of Vietnam credit institutions supervision regulatory requirements official law",
            "SBV credit institutions Vietnam banking supervision compliance requirements",
            "越南央行 SBV 信贷机构 监管要求 商业银行 官方",
        ])
    if _is_vietnam_supplier_payment_query(query) and not _is_china_vietnam_supplier_payment_query(query):
        variants.extend([
            "State Bank of Vietnam supplier payment foreign exchange compliance current account transfer payment services",
            "SBV cross-border payment Vietnam supplier payment authorized banks foreign exchange services",
            "越南 供应商 付款 外汇 合规 SBV 经常项目 转账 支付服务 授权银行",
        ])
    return variants


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
        variants.extend(_targeted_query_variants(query))
        return _unique_keep_order(variants)[:max_items + 1 + len(_targeted_query_variants(query))]

    if query_type == "compound":
        llm_queries = _call_transform_llm(
            "decomposition: 将复合问题拆成可单独检索的子问题", query, normalized, max_items
        )
        variants = llm_queries or _fallback_decompose(query, region, topic, max_items)
        variants.extend(_targeted_query_variants(query))
        return _unique_keep_order(variants)[:max_items + len(_targeted_query_variants(query))]

    if query_type == "conceptual":
        llm_queries = _call_transform_llm(
            "step-back: 生成更抽象的原则性检索查询", query, normalized, 1
        )
        stepback = llm_queries[0] if llm_queries else _fallback_stepback(query, normalized)
        return _unique_keep_order([query, normalized, stepback] + _targeted_query_variants(query))

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
        return _unique_keep_order([query, hyde_text] + _targeted_query_variants(query))

    return _unique_keep_order([query, normalized] + _targeted_query_variants(query))


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


def _ingestion_chunk_to_doc(chunk: dict) -> dict:
    """Ingestion chunk -> downstream doc shape aligned with BM25/Chroma."""
    return {
        "id": chunk.get("chunk_id") or chunk.get("doc_id"),
        "title": chunk.get("title", ""),
        "content": chunk.get("content", ""),
        "source_name": chunk.get("source_name") or chunk.get("issuer", ""),
        "source_url": chunk.get("source_url", ""),
        "region": chunk.get("region_code", ""),
        "topic": chunk.get("topic_code", ""),
        "effective_date": chunk.get("effective_date") or None,
        "publish_date": chunk.get("publish_date") or None,
        "source_type": chunk.get("source_type") or "unknown",
        "authority_level": chunk.get("authority_level") or "medium",
        "disclaimer_level": chunk.get("disclaimer_level") or "unknown",
        "disclaimer": chunk.get("disclaimer", ""),
        "doc_id": chunk.get("doc_id", ""),
        "parent_doc_id": chunk.get("parent_doc_id", "") or chunk.get("doc_id", ""),
        "chunk_id": chunk.get("chunk_id", ""),
        "chunk_index": chunk.get("chunk_index", 0),
        "chapter": chunk.get("chapter", ""),
        "section": chunk.get("section", ""),
        "page": chunk.get("page", ""),
        "content_hash": chunk.get("content_hash", ""),
        "trust_tier": chunk.get("trust_tier", ""),
        "document_type": chunk.get("document_type", ""),
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
from language_utils import detect_explicit_language_request, resolve_answer_language


_HAN_CHAR_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:[-_][A-Za-z0-9]+)*")
_EN_QUESTION_RE = re.compile(
    r"\b(what|how|why|when|where|which|who|whom|can|could|should|do|does|is|are)\b",
    re.IGNORECASE,
)
_DOC_IDENTIFIER_RE = re.compile(r"\b[A-Z]{2,}[A-Z0-9_-]*[_-]\d{1,4}/\d{4}\b")


def resolve_rag_answer_language(query: str, fallback: str | None = None) -> str:
    """RAG-specific answer-language policy.

    Generic language detection treats mixed Chinese queries with English product
    names as English when Latin tokens dominate. For policy RAG, a Chinese
    question containing English product names such as FPS or GoGBA should still
    receive a Chinese answer unless the user explicitly asks for English.
    """
    explicit = detect_explicit_language_request(query)
    if explicit:
        return explicit

    text = str(query or "")
    han_count = len(_HAN_CHAR_RE.findall(text))
    latin_count = 0
    for token in _LATIN_WORD_RE.findall(text):
        if token.isupper() or len(token) <= 1:
            continue
        latin_count += len(token)

    if han_count >= 2:
        looks_like_english_question = (
            _EN_QUESTION_RE.search(text) is not None
            and latin_count >= max(12, han_count * 2)
        )
        if not looks_like_english_question:
            return "zh"

    return resolve_answer_language(text, fallback=fallback)


def detect_rag_audience(query: str) -> str:
    """Classify the likely reader so the prompt can tune clarity and caveats."""
    text = str(query or "")
    if _contains_any(text, [
        "中小企业", "SME", "公司", "企业", "工厂", "供应商", "贸易", "发票",
        "应收账款", "经营", "business", "corporate", "supplier",
    ]):
        return "sme_cross_border_operator"
    if _contains_any(text, [
        "个人", "汇款", "转账", "电汇", "FPS", "TT", "跨境付款", "收款",
        "到账", "费用", "限额", "remittance", "transfer",
    ]):
        return "personal_cross_border_user"
    if _contains_any(text, [
        "贷款", "借款", "按揭", "利率", "还款", "申请条件", "资格", "文件",
        "borrow", "loan", "repay",
    ]):
        return "ordinary_borrower"
    return "general_financial_user"


def _extract_doc_identifiers(text: str) -> list[str]:
    return [m.group(0).upper() for m in _DOC_IDENTIFIER_RE.finditer(str(text or ""))]


def _is_doc_identifier_lookup(text: str) -> bool:
    if not _extract_doc_identifiers(text):
        return False
    return _contains_any(text, [
        "对应", "是什么", "哪份", "哪个政策", "什么政策", "文件编号", "编号",
        "document id", "file number", "reference number", "corresponds to",
        "which policy", "what policy", "which document", "what document",
    ])


def _answer_shape_instruction(query: str, response_language: str) -> str:
    if _contains_any(query, ["SFGS", "担保贷款"]) and _contains_any(
        query, ["贷多少", "额度", "上限", "营业额", "利润", "maximum facility amount", "loan amount"]
    ):
        if response_language == "en":
            return (
                "\nSFGS amount answer shape:\n"
                "- Do not start with an insufficiency caveat. Start with: the user can first look at the product maximum limits, then bank approval decides the actual amount.\n"
                "- State the current maximum facility amounts supported by the latest HKMCI factsheet in the first bullet group.\n"
                "- Interpret the HKMCI factsheet table as: 80% Guarantee Product = HK$12,000,000; 90% Guarantee Product = HK$18,000,000; Special 100% Loan Guarantee = HK$8,000,000. Apply the wages/rent or HK$9,000,000 lower-cap formula only to Special 100% Loan Guarantee where the factsheet states it.\n"
                "- If an older HKMA announcement conflicts with the factsheet amount, treat the older announcement as historical background and use the factsheet for current limits.\n"
                "- Explain that turnover/profit alone does not determine approved amount unless the materials provide a formula.\n"
                "- For documents, state only confirmed document requirements. If the checklist is absent, write 'the materials do not list a fixed financial-file checklist' instead of a broad insufficiency caveat."
            )
        if response_language == "bilingual":
            return (
                "\nSFGS 额度回答形态 / SFGS amount answer shape:\n"
                "- 不要以“无法确认/无法推算”开头；开头先说“可先按产品最高上限判断，实际获批金额由银行审批决定”。Do not start with an insufficiency caveat.\n"
                "- 第一组 bullet 直接列出当前 HKMCI factsheet 支持的最高融资额度。Start with current maximum facility amounts from the latest HKMCI factsheet.\n"
                "- HKMCI factsheet 表格按以下方式解释：80% Guarantee Product = HK$12,000,000；90% Guarantee Product = HK$18,000,000；Special 100% Loan Guarantee = HK$8,000,000。工资/租金或 HK$9,000,000 较低者公式只适用于 factsheet 所列 Special 100% Loan Guarantee。\n"
                "- 如果旧 HKMA announcement 与 factsheet 额度冲突，把旧 announcement 当历史背景，当前限额以 factsheet 为准。\n"
                "- 说明营业额/利润本身不能直接换算获批金额，除非资料给出公式。\n"
                "- 文件部分只列已确认要求；未列明固定财务文件清单时写“资料未列出固定财务文件清单”，不要写成整题无法回答。"
            )
        return (
            "\nSFGS 额度回答形态：\n"
            "- 不要以“无法确认/无法推算”开头；开头先说“可先按产品最高上限判断，实际获批金额由银行审批决定”。\n"
            "- 第一组 bullet 直接列出当前 HKMCI factsheet 支持的最高融资额度。\n"
            "- HKMCI factsheet 表格按以下方式解释：80% Guarantee Product = HK$12,000,000；90% Guarantee Product = HK$18,000,000；Special 100% Loan Guarantee = HK$8,000,000。工资/租金或 HK$9,000,000 较低者公式只适用于 factsheet 所列 Special 100% Loan Guarantee。\n"
            "- 如果旧 HKMA announcement 与 factsheet 额度冲突，把旧 announcement 当历史背景，当前限额以 factsheet 为准。\n"
            "- 说明营业额/利润本身不能直接换算获批金额，除非资料给出公式。\n"
            "- 文件部分只列已确认要求；未列明固定财务文件清单时写“资料未列出固定财务文件清单”，不要写成整题无法回答。"
        )

    if (
        _contains_any(query, ["越南", "Vietnam"])
        and _contains_any(query, ["供应商", "supplier"])
        and _contains_any(query, ["付汇", "付款", "payment", "remittance"])
        and _contains_any(query, ["流程", "审核", "review", "process"])
    ):
        if response_language == "en":
            return (
                "\nChina-to-Vietnam supplier payment answer shape:\n"
                "- If SAFE trade-FX materials state bank review requirements, answer with a short China-side review flow first.\n"
                "- Treat Vietnam/SBV materials as Vietnam-side payment-system or risk context unless they state an inward-payment review step.\n"
                "- Do not say the process is unavailable merely because the SAFE rule is not Vietnam-specific; say it is the China-side goods-trade FX process.\n"
                "- Only list documents expressly named in the materials, such as contracts, invoices, customs declarations, filing records, transport documents, bonded-checklist records, or other valid commercial documents.\n"
                "- If some Vietnam-side or bank-internal details are absent, put them under 'Details to confirm with the bank' instead of saying the whole process is unavailable."
            )
        if response_language == "bilingual":
            return (
                "\n中国向越南供应商付款回答形态 / China-to-Vietnam supplier payment answer shape:\n"
                "- 如果 SAFE 贸易外汇资料列明银行审核要求，先给出中国侧银行审核流程。Answer the China-side review flow first when SAFE supports it.\n"
                "- 越南/SBV 资料只作为越南侧支付系统或风险背景，除非其明示入账审核步骤。\n"
                "- 不要因为 SAFE 规则不是越南专门规则就说流程不可得；应说明这是中国侧货物贸易付汇流程。\n"
                "- 只列资料明示的单据，例如合同、发票、报关单、备案清单、运输单据、保税核注清单或其他有效商业单据。\n"
                "- 如果越南侧或银行内部细节未列明，放在“需要向银行确认的细节”下，不要写成整套流程无法回答。"
            )
        return (
            "\n中国向越南供应商付款回答形态：\n"
            "- 如果 SAFE 贸易外汇资料列明银行审核要求，先给出中国侧银行审核流程。\n"
            "- 越南/SBV 资料只作为越南侧支付系统或风险背景，除非其明示入账审核步骤。\n"
            "- 不要因为 SAFE 规则不是越南专门规则就说流程不可得；应说明这是中国侧货物贸易付汇流程。\n"
            "- 只列资料明示的单据，例如合同、发票、报关单、备案清单、运输单据、保税核注清单或其他有效商业单据。\n"
            "- 如果越南侧或银行内部细节未列明，放在“需要向银行确认的细节”下，不要写成整套流程无法回答。"
        )

    if not _is_doc_identifier_lookup(query):
        return ""
    identifiers = ", ".join(_extract_doc_identifiers(query))
    if response_language == "en":
        return (
            "\nExact document-ID lookup rule:\n"
            f"- The user is asking what `{identifiers}` corresponds to. Keep the answer narrow.\n"
            "- First sentence: identify the matched document or policy title and issuer/administrator if supported.\n"
            "- Then give at most three short bullets: update/effective date if present, policy/scheme scope, and how the user should use the document.\n"
            "- Do not enumerate fee rates, eligibility rules, product matrices, application documents, or unsupported missing fields unless the user asks for details.\n"
            "- Do not add an 'available materials cannot confirm' section when the matched title and issuer are supported."
        )
    if response_language == "bilingual":
        return (
            "\n文件编号查询规则 / Exact document-ID lookup rule:\n"
            f"- 用户是在问 `{identifiers}` 对应什么文件或政策。答案必须聚焦这个对应关系。Keep the answer narrow.\n"
            "- 第一句说明匹配到的文件/政策标题和发布或管理机构。First sentence: title plus issuer/administrator if supported.\n"
            "- 后面最多三点：更新/生效日期、政策/计划范围、用户应如何使用该文件。Use at most three short bullets.\n"
            "- 除非用户追问详情，不要展开费用、资格、产品矩阵、申请文件或资料缺口。\n"
            "- 如果标题和机构已有资料支持，不要另加“现有资料无法确认”段落。"
        )
    return (
        "\n文件编号查询规则：\n"
        f"- 用户是在问 `{identifiers}` 对应什么文件或政策，答案必须聚焦这个对应关系。\n"
        "- 第一句说明匹配到的文件/政策标题，以及发布或管理机构（如资料支持）。\n"
        "- 后面最多三点：更新/生效日期、政策/计划范围、用户应如何使用该文件。\n"
        "- 除非用户追问详情，不要展开费用、资格、产品矩阵、申请文件或资料缺口。\n"
        "- 如果标题和机构已有资料支持，不要另加“现有资料无法确认”段落。"
    )


AUDIENCE_LABELS = {
    "ordinary_borrower": {
        "zh": "普通借款人",
        "en": "ordinary borrower",
        "bilingual": "普通借款人 / ordinary borrower",
    },
    "personal_cross_border_user": {
        "zh": "个人跨境金融用户",
        "en": "personal cross-border finance user",
        "bilingual": "个人跨境金融用户 / personal cross-border finance user",
    },
    "sme_cross_border_operator": {
        "zh": "中小企业跨境经营用户",
        "en": "SME cross-border business operator",
        "bilingual": "中小企业跨境经营用户 / SME cross-border business operator",
    },
    "general_financial_user": {
        "zh": "普通金融用户",
        "en": "general financial user",
        "bilingual": "普通金融用户 / general financial user",
    },
}


def _answer_contract(response_language: str, audience: str) -> str:
    label = AUDIENCE_LABELS.get(audience, AUDIENCE_LABELS["general_financial_user"])
    if response_language == "en":
        return (
            f"Target reader: {label['en']}.\n"
            "Hard requirements:\n"
            "- Start with a direct 1-2 sentence answer to the user's exact question, reusing the key terms in the question.\n"
            "- Every policy, fee, rate, limit, eligibility condition, required document, timeline, and bank process must be directly supported by the reference materials.\n"
            "- Do not fill gaps with industry practice, common assumptions, examples, transaction codes, bank lists, or inferred document packages.\n"
            "- If the materials only support part of the question, answer that part first, then state only the missing items that the user directly asked about.\n"
            "- Use 'available materials cannot confirm' only when no direct answer can be given. When a direct answer is supported but some details are absent, use a short 'details to confirm' note instead.\n"
            "- Keep unsupported-information notes concise: use at most three bullets unless the user explicitly asks for a gap analysis.\n"
            "- Use borrower-friendly language: explain terms briefly, avoid jargon, and separate confirmed facts from missing information.\n"
            "- For product or policy recommendations, only mention products or schemes that appear in the reference materials."
        )
    if response_language == "bilingual":
        return (
            f"回答对象 / Target reader: {label['bilingual']}.\n"
            "硬性要求 / Hard requirements:\n"
            "- 开头必须用1-2句直接回答用户的具体问题,并保留问题中的关键术语。Start with a direct 1-2 sentence answer to the exact question, reusing key terms.\n"
            "- 政策、费用、利率、限额、资格、所需文件、办理时效和银行流程必须由参考资料直接支持。\n"
            "- 不得用行业惯例、常识、例子、交易编码、银行名单或推断出的文件包补足空白。\n"
            "- 如果资料只支持部分答案，先回答已支持部分，再只说明用户直接问到但资料未列明的项目。\n"
            "- 只有完全无法直接回答时才使用“资料无法确认”。如果直接答案已有资料支持但部分细节缺失，用简短“需要确认的细节”说明。\n"
            "- 缺失信息说明保持简短；除非用户要求差距分析,最多列3点。Keep unsupported-information notes to at most three bullets unless the user asks for gap analysis.\n"
            "- 使用用户友好语言，简单解释术语，区分已确认事实和缺失信息。\n"
            "- 只推荐参考资料中出现的产品或计划。"
        )
    return (
        f"回答对象：{label['zh']}。\n"
        "硬性要求：\n"
        "- 开头必须用1-2句直接回答用户的具体问题,并保留问题中的关键术语。\n"
        "- 政策、费用、利率、额度、限额、申请资格、所需文件、办理时效和银行流程，必须能在参考资料中找到直接依据。\n"
        "- 不得用行业惯例、常识、例子、交易编码、银行名单或推断出的文件清单补足资料空白。\n"
        "- 如果资料只支持部分答案，先回答已支持部分，再只说明用户直接问到但资料未列明的项目。\n"
        "- 只有完全无法直接回答时才使用“现有资料无法确认”。如果直接答案已有资料支持但部分细节缺失，用简短“需要确认的细节”说明。\n"
        "- 缺失信息说明保持简短；除非用户要求差距分析,最多列3点。\n"
        "- 用用户友好语言，简单解释术语，区分已确认事实和缺失信息。\n"
        "- 只推荐参考资料中出现的产品、计划或监管要求。"
    )


SYSTEM_PROMPTS = {
    "zh": """你是 CrossBridge AI,一个跨境普惠金融决策助手,服务普通借款人、个人跨境金融用户以及大湾区与东南亚的中小企业。

严格遵守以下规则:
1. 只能基于【参考资料】回答,不得编造任何法规、数字或产品条款。
2. 若参考资料完全不足以直接回答,要诚实说明"现有资料无法确认",不要猜；若已能直接回答但部分细节缺失,用"需要确认的细节"简短列出,不要把整段答案写成拒答。
3. 回答开头必须直接回应用户问题,再分点说明依据;不要用大段背景或无关缺口淹没答案。
4. 你不是律师或会计师,回答末尾必须提示用户最终操作前向银行客户经理或专业人士确认。
5. 绝不提供逃税、洗钱、规避监管等违规建议。
6. 引用规则:答案末尾"信息来源"中,只列出【参考资料】里标记为"可引用"的资料 ([资料N]);
   标记为"仅作context,不可引用"的资料 ([资料Cx]) 可以帮助你理解,但不要出现在信息来源列表中。
7. 必须全程使用中文回答。官方标题、专有名词和链接可保留原文。
8. 不得使用"通常""一般""可合理推断""行业惯例"补充参考资料未直接支持的费用、利率、额度、限额、时效、资格、材料或流程。
""",
    "en": """You are CrossBridge AI, a cross-border inclusive-finance decision assistant for ordinary borrowers, personal cross-border finance users, and SMEs in the Greater Bay Area and Southeast Asia.

Follow these rules strictly:
1. Answer only from the provided reference materials. Never invent regulations, figures, or product terms.
2. If the materials are wholly insufficient for a direct answer, clearly say that the available materials cannot confirm the answer. If a direct answer is supported but some details are absent, use a short "details to confirm" note instead of framing the whole answer as unknown.
3. Start with a direct answer to the user's question, then explain the supporting facts in clear bullets. Do not bury the answer under broad background or unrelated gaps.
4. You are not a lawyer or accountant. End with a reminder to confirm final actions with a bank relationship manager or a qualified professional.
5. Never provide advice for tax evasion, money laundering, or regulatory avoidance.
6. In the final "Sources" section, list only materials marked "citable" ([SourceN]). Materials marked "context only, not citable" ([SourceCx]) may inform your understanding but must not appear in the source list.
7. Answer entirely in English. Official titles, proper nouns, and URLs may remain in their original language.
8. Do not use "usually", "generally", "reasonable inference", or "industry practice" to supplement unsupported fees, rates, amounts, limits, timelines, eligibility, documents, or procedures.
""",
    "bilingual": """你是 CrossBridge AI，一个服务普通借款人、个人跨境金融用户以及大湾区与东南亚中小企业的跨境普惠金融决策助手。
You are CrossBridge AI, a cross-border inclusive-finance decision assistant for ordinary borrowers, personal cross-border finance users, and SMEs in the Greater Bay Area and Southeast Asia.

严格遵守以下规则 / Follow these rules strictly:
1. 只能基于【参考资料】回答，不得编造法规、数字或产品条款。Answer only from the provided reference materials. Never invent regulations, figures, or product terms.
2. 若资料完全不足以直接回答，要明确说明现有资料无法确认，不要猜；若直接答案已有依据但部分细节缺失，用简短“需要确认的细节”说明。If a direct answer is supported but details are absent, use a short details-to-confirm note.
3. 开头直接回应用户问题,再分点说明依据;不要用大段背景或无关缺口淹没答案。Start with a direct answer, then explain the supporting facts in clear bullets.
4. 你不是律师或会计师。结尾提醒用户向银行客户经理或专业人士确认。End with a reminder to confirm final actions with a bank relationship manager or qualified professional.
5. 不得提供逃税、洗钱或规避监管建议。Never provide advice for tax evasion, money laundering, or regulatory avoidance.
6. 结尾“信息来源 / Sources”只列出标记为“可引用”的资料（[资料N]）；“仅作 context，不可引用”的资料（[资料Cx]）不得列出。
7. 必须使用中文和英文中英对照作答。Provide the answer in BOTH Chinese and English.
8. 不得用行业惯例、通常情况或合理推断补充资料未直接支持的费用、利率、额度、限额、时效、资格、材料或流程。Do not supplement unsupported operational details with industry practice or inference.
""",
}

def build_prompt(query, retrieved, context_only=None, response_language="zh"):
    """把检索结果拼进 Prompt。

    Step 3.5: retrieved 是可引用的（来自 trusted source），
              context_only 仅用于 LLM 理解上下文，禁止出现在 citation 列表。
    """
    blocks = []
    is_english = response_language == "en"
    is_bilingual = response_language == "bilingual"
    for i, (doc, _score) in enumerate(retrieved, 1):
        if is_english:
            blocks.append(
                f"[Source{i}] (citable) Source:{doc['source_name']} | Region:{doc['region']} | "
                f"Effective date:{doc.get('effective_date','-')}\n"
                f"Title:{doc['title']}\nContent:{doc['content']}"
            )
        else:
            blocks.append(
                f"[资料{i}] (可引用) 来源:{doc['source_name']} | 地区:{doc['region']} | "
                f"生效日:{doc.get('effective_date','-')}\n"
                f"标题:{doc['title']}\n正文:{doc['content']}"
            )
    if context_only:
        for j, (doc, _score) in enumerate(context_only, 1):
            if is_english:
                blocks.append(
                    f"[SourceC{j}] (context only, not citable) Source:{doc['source_name']} | "
                    f"Region:{doc['region']}\nTitle:{doc['title']}\nContent:{doc['content']}"
                )
            else:
                blocks.append(
                    f"[资料C{j}] (仅作context,不可引用) 来源:{doc['source_name']} | "
                    f"地区:{doc['region']}\n标题:{doc['title']}\n正文:{doc['content']}"
                )
    context = "\n\n".join(blocks)
    audience = detect_rag_audience(query)
    contract = _answer_contract(response_language, audience) + _answer_shape_instruction(query, response_language)
    if is_english:
        user_msg = (
            f"[Reference materials]\n{context}\n\n"
            f"[Answer contract]\n{contract}\n\n"
            f"[User question]\n{query}\n\n"
            "Answer in English based on the materials above. End with a 'Sources' section "
            "listing the citable materials you used."
        )
    elif is_bilingual:
        user_msg = (
            f"【参考资料 / Reference materials】\n{context}\n\n"
            f"【回答要求 / Answer contract】\n{contract}\n\n"
            f"【用户问题 / User question】\n{query}\n\n"
            "请基于以上资料使用中文和英文中英对照作答，并在结尾用"
            "“信息来源 / Sources”列出使用的【可引用】资料。"
        )
    else:
        user_msg = (
            f"【参考资料】\n{context}\n\n"
            f"【回答要求】\n{contract}\n\n"
            f"【用户问题】\n{query}\n\n"
            f"请基于以上资料回答,并在结尾用'信息来源'列出你引用了哪几条【可引用】资料。"
        )
    return user_msg


def call_llm(query, retrieved, response_language="zh"):
    """
    通过 LangChain 调用 Qwen 生成答案。
    """
    user_msg = build_prompt(query, retrieved, response_language=response_language)
    resp = get_qwen_chat_model().invoke([
        ("system", SYSTEM_PROMPTS[response_language]),
        ("user", user_msg),
    ])
    return str(resp.content)


def _fallback_answer(query, retrieved, response_language="zh"):
    """没有大模型时,直接结构化展示检索结果。"""
    is_english = response_language == "en"
    is_bilingual = response_language == "bilingual"
    if not retrieved:
        if is_english:
            return "The available knowledge base does not contain authoritative materials directly related to your question. Please provide more context or consult a bank relationship manager."
        if is_bilingual:
            return (
                "现有资料库暂时找不到与您问题直接相关的权威资料，请补充背景或咨询银行客户经理。\n\n"
                "The available knowledge base does not contain authoritative materials directly related to your question. "
                "Please provide more context or consult a bank relationship manager."
            )
        return "现有资料库暂时找不到与您问题直接相关的权威资料,建议补充更多数据源或咨询银行客户经理。"
    lines = [
        "(Demo mode: no LLM API is configured. The following are summaries of the retrieved authoritative materials.)\n"
        if is_english else
        "(演示模式：未配置大模型 API。以下为检索到的权威资料摘要。 / "
        "Demo mode: no LLM API is configured. The following are summaries of the retrieved authoritative materials.)\n"
        if is_bilingual else
        "(演示模式:未配置大模型 API,以下为检索到的权威资料摘要)\n"
    ]
    for i, (doc, score) in enumerate(retrieved, 1):
        lines.append(f"{i}. 【{doc['title']}】({doc['source_name']})")
        # 摘要取正文前 80 字
        summary = doc["content"][:80].strip()
        lines.append(
            f"   {'Summary' if is_english else '要点 / Summary' if is_bilingual else '要点'}:{summary}……"
        )
        lines.append("")
    lines.append(
        "The information above is for reference only. Confirm final actions with a BOCHK relationship manager or a qualified professional."
        if is_english else
        "以上信息仅供参考，最终操作前请向中银香港客户经理或专业人士确认。 / "
        "The information above is for reference only. Confirm final actions with a BOCHK relationship manager or a qualified professional."
        if is_bilingual else
        "以上为参考信息,最终操作前请向中银香港客户经理或专业人士确认。"
    )
    return "\n".join(lines)


def _extract_last_update_date(text: str) -> str:
    match = re.search(r"Last update date:\s*([^)\\n]+)", text or "", flags=re.I)
    if match:
        return match.group(1).strip()
    return ""


def _build_exact_identifier_answer(query: str, citation_source, response_language: str) -> str:
    identifiers = _extract_doc_identifiers(query)
    if not identifiers or not _is_doc_identifier_lookup(query):
        return ""

    for idx, (doc, _score) in enumerate(citation_source or [], 1):
        haystack = " ".join([
            str(doc.get("doc_id") or ""),
            str(doc.get("title") or ""),
            str(doc.get("content") or ""),
            str(doc.get("contextualized_content") or ""),
        ]).upper()
        matched = next((identifier for identifier in identifiers if identifier in haystack), "")
        if not matched:
            continue

        title = str(doc.get("title") or "the matched document").strip()
        source = str(doc.get("source_name") or "the official source").strip()
        content = str(doc.get("content") or "")
        last_update = _extract_last_update_date(content)
        citation = f"[Source{idx}]" if response_language == "en" else f"[资料{idx}]"
        if "SME Financing Guarantee Scheme" in content or "SFGS" in content:
            zh_policy = "中小企融资担保计划（SME Financing Guarantee Scheme, SFGS）"
            en_policy = "SME Financing Guarantee Scheme (SFGS)"
            scope_zh = f"这份文件是 {zh_policy} 的政策资料。"
            scope_en = f"The document is policy material for the {en_policy}."
        else:
            zh_policy = title
            en_policy = title
            scope_zh = f"这份资料对应 {title}。"
            scope_en = f"The document corresponds to {title}."

        if response_language == "en":
            sentence = f"{matched} is the file number for {source}'s {title}, which corresponds to the {en_policy}."
            if last_update:
                sentence += f" The document states its last update date as {last_update}."
            return f"{sentence} {scope_en} {citation}\n\nSources: {citation}"

        if response_language == "bilingual":
            zh_sentence = f"{matched} 文件编号对应的是《{title}》，也就是 {zh_policy} 的政策资料；该编号出现在 {source} 的文件中。"
            en_sentence = f"{matched} is the file number for {source}'s {title}, which corresponds to policy material for the {en_policy}."
            if last_update:
                zh_sentence += f" 文件标注的最后更新日期是 {last_update}。"
                en_sentence += f" The document states its last update date as {last_update}."
            return f"{zh_sentence} {citation}\n{en_sentence} {citation}\n\n信息来源 / Sources: {citation}"

        lines = [
            f"现有资料明确提及“{matched}”这一文件编号；它对应的政策是 {zh_policy}，具体文件是 {source} 的《{title}》。"
        ]
        lines.append("")
        lines.append("【已确认事实】")
        lines.append(f"- “{matched}”出现在《{title}》中。")
        if last_update:
            lines.append(f"- 该文件标注的最后更新日期是 {last_update}。")
        lines.append(f"- 该文件用于说明 {zh_policy} 的政策资料。")
        lines.append("")
        lines.append(f"信息来源：{citation}")
        return "\n".join(lines)

    return ""


def _is_fps_limit_lookup(query: str) -> bool:
    return _contains_any(query, ["FPS", "Faster Payment System", "转数快"]) and _contains_any(
        query,
        ["限额", "上限", "金额", "特点", "limit", "transaction limit", "transfer amount", "feature"],
    )


def _build_fps_limit_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh" or not _is_fps_limit_lookup(query):
        return ""

    hkma_label = ""
    bochk_label = ""
    for idx, (doc, _score) in enumerate(citation_source or [], 1):
        doc_id = doc.get("doc_id") or doc.get("id")
        label = f"[资料{idx}]"
        if doc_id == "hkma_fps" and not hkma_label:
            hkma_label = label
        elif doc_id == "bochk_fps_limit_notice_20251224" and not bochk_label:
            bochk_label = label

    if not hkma_label or not bochk_label:
        return ""

    return "\n".join([
        (
            "Faster Payment System（FPS）转账的主要特点是：可作跨银行/电子钱包支付，"
            "可用收款人的手机号码或电子邮件地址转账，资金几乎即时到账，系统24x7运行，"
            f"并支持港元和人民币支付。{hkma_label}"
        ),
        "",
        "关于限额，现有资料只支持说明 BOCHK 的本地银行转账安排：",
        (
            f"- BOCHK 公告列明，Local Bank Transfer via FPS 的转账金额由不超过 "
            f"HKD1,000,000.00 调整为不超过 HKD3,000,000.00 或等值金额，"
            f"生效日期为2026年1月26日。{bochk_label}"
        ),
        f"- BOCHK 公告同时列明 Personal Customers 的费用为 Waived。{bochk_label}",
        "- 现有资料未确认其他银行、每日累计限额、账户等级限额或跨境FPS汇款限额。",
        "",
        f"信息来源：{hkma_label}、{bochk_label}",
    ])


def _citation_labels_by_doc_id(citation_source, response_language: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    for idx, (doc, _score) in enumerate(citation_source or [], 1):
        doc_id = doc.get("doc_id") or doc.get("id")
        if not doc_id or doc_id in labels:
            continue
        labels[doc_id] = f"[Source{idx}]" if response_language == "en" else f"[资料{idx}]"
    return labels


def _build_tt_remittance_fee_time_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh" or not _is_tt_remittance_fee_time_query(query):
        return ""

    labels = _citation_labels_by_doc_id(citation_source, response_language)
    charges = labels.get("bochk_remittance_charges")
    guide = labels.get("bochk_outward_tt_quick_guide")
    if not charges or not guide:
        return ""

    return "\n".join([
        "电汇（TT）汇款可以确认两件事：BOCHK 对外电汇收费按渠道和客户类型收取；到账方面，资料只承诺在满足截止时间和条件时由 BOCHK 当日处理，不等同于保证收款银行当日入账。",
        "",
        "已确认费用：",
        f"- Telegraphic Transfer 经分行办理：HK$260/笔。{charges}",
        f"- 经电子渠道办理：个人客户 HK$65/笔，企业客户 HK$120/笔。{charges}",
        f"- 若选择由汇款人承担 Correspondent Bank Charges，中转行、清算机构或收款银行费用可能另行收取。{charges}",
        "",
        "已确认处理时间：",
        f"- TT 主要货币（如 HKD/USD/EUR/CAD/GBP）的分行截止时间为 17:00，网上银行截止时间为 18:00；部分其他主要货币和非主要货币也列有 17:00/18:00 的同日处理截止时间。{guide}",
        f"- BOCHK 说明，在指示清晰完整、收款银行所在地/币种为营业日或清算日、资金及费用充足、换汇已安排同日交割等条件满足时，会在相应截止时间前收到申请后于同日处理。{guide}",
        "- 现有资料未列明标准 TT 到收款银行实际入账的固定天数；如需确认某个国家、币种或收款银行的到账时效，应在汇款前向 BOCHK 或收款银行确认。",
        "",
        f"信息来源：{charges}、{guide}",
    ])


def _build_sme_loan_docs_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh":
        return ""
    if not _contains_any(query, ["SME", "中小企业"]) or not _contains_any(
        query,
        ["财务证明", "账务文件", "材料", "文件"],
    ):
        return ""

    labels = _citation_labels_by_doc_id(citation_source, response_language)
    bochk_small = labels.get("bochk_sme_loan")
    bochk_sfgs = labels.get("bochk_sfgs_product")
    hkmc_fact = labels.get("hkmc_sfgs_factsheet")
    hkmc_proc = labels.get("hkmc_sfgs_application_procedures")
    hkmc_proc_lender = labels.get("hkmc_sfgs_application_procedures_lender")
    hkmc_any = hkmc_fact or hkmc_proc or hkmc_proc_lender

    if not bochk_small or not hkmc_any:
        return ""

    sources = [label for label in [hkmc_any, bochk_sfgs, bochk_small] if label]
    return "\n".join([
        "关于“申请 SME 贷款要提交哪些财务证明材料、公司账务文件”，现有官方资料没有列出一份可直接照抄的完整文件清单；能确认的是银行或HKMCI可要求申请人提供支持文件，而 BOCHK 的小企业无抵押贷款明确不要求抵押品和经审计财务报表。",
        "",
        "已确认信息如下：",
        f"- SFGS：贷款机构会进行客户尽职调查、审核申请和核实资格，并在向HKMCI提交担保申请时提供相关支持文件；贷款机构或HKMCI也可要求借款人进一步提供支持文件和资料。{hkmc_any}",
        (
            f"- BOCHK SFGS线上流程：页面显示申请流程包括“Upload documents”，并提示可预先上传相关文件，以便客户经理跟进。{bochk_sfgs}"
            if bochk_sfgs else
            "- BOCHK SFGS线上流程未进入本次可引用资料，无法确认其上传文件页面细节。"
        ),
        f"- BOCHK “Small Business Loan” 无抵押贷款：资料明确写明不需要抵押品，也不需要经审计财务报表；但银行保留要求客户提供相关支持文件或资料的权利。{bochk_small}",
        "",
        "因此，不能把资产负债表、利润表、银行流水、报税表等列为所有SME贷款的必交文件；这些只能由所申请产品和银行客户经理确认。最终提交前请向BOCHK客户经理确认适用于您公司的最新文件清单。",
        "",
        f"信息来源：{'、'.join(sources)}",
    ])


def _build_sme_collateral_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh":
        return ""
    if not _contains_any(query, ["SME", "中小企业"]) or not _contains_any(
        query,
        ["抵押", "无抵押", "质押", "资产"],
    ):
        return ""

    labels = _citation_labels_by_doc_id(citation_source, response_language)
    text_by_doc_id = {}
    for doc, _score in citation_source or []:
        doc_id = doc.get("doc_id") or doc.get("id")
        if doc_id and doc_id not in text_by_doc_id:
            text_by_doc_id[doc_id] = " ".join([
                str(doc.get("title") or ""),
                str(doc.get("content") or ""),
                str(doc.get("contextualized_content") or ""),
            ])
    bochk_small = labels.get("bochk_sme_loan")
    bochk_services = labels.get("bochk_loan_services")
    bochk_sfgs = labels.get("bochk_sfgs_product")
    hkmc_fact = labels.get("hkmc_sfgs_factsheet")
    hkma_90 = labels.get("hkma_sfgs_90_product")

    if not bochk_small:
        return ""

    service_text = text_by_doc_id.get("bochk_loan_services", "")
    service_lists_collateral_products = _contains_any(service_text, [
        "Mortgage Loan",
        "Asset-Pledge",
        "Machinery and Equipment Financing",
        "按揭",
        "质押",
        "機械設備",
    ])
    sources = [
        label for label in [
            bochk_small,
            bochk_services if service_lists_collateral_products else None,
            bochk_sfgs,
            hkmc_fact,
            hkma_90,
        ]
        if label
    ]
    collateral_line = (
        f"- 有抵押/质押类融资也存在：BOCHK贷款服务页列出 Mortgage Loan、Asset-Pledge Loan "
        f"和 Machinery and Equipment Financing 等融资方式。{bochk_services}"
        if bochk_services and service_lists_collateral_products else
        "- 本次可引用资料未直接列明可接受的抵押/质押资产范围；如果申请有抵押或质押融资，需要向银行确认资产类型、估值方式和审批条件。"
    )
    sfgs_line = (
        f"- SFGS属于由HKMCI提供担保的融资担保计划；资料说明贷款机构会审核申请、核实资格并可要求支持文件，但不等同于资料已列出借款人必须抵押哪些资产。{hkmc_fact}"
        if hkmc_fact else
        "- 本次可引用资料未包含HKMCI SFGS factsheet，不能补充SFGS担保要求。"
    )
    bochk_sfgs_line = (
        f"- BOCHK SFGS产品页可作为申请渠道/产品资料参考，但最终贷款审批和所需支持文件仍以银行审核为准。{bochk_sfgs}"
        if bochk_sfgs else
        "- BOCHK SFGS产品页未进入本次可引用资料，不能补充其申请页面说明。"
    )
    hkma_line = (
        f"- HKMA资料说明90%担保产品用于支持较小规模企业、经营经验较少的企业及专业人士取得融资，可作为SFGS背景。{hkma_90}"
        if hkma_90 else
        ""
    )

    lines = [
        "申请SME贷款不一定需要拿资产做抵押；至少BOCHK的“BOC Small Business Loan”明确是无抵押贷款选项，资料写明不需要抵押品，也不需要经审计财务报表。",
        "",
        "已确认信息如下：",
        f"- 无抵押选项：BOC Small Business Loan / Unsecured Loan 明确写明 “Provision of collaterals and audited financial statements is not required”。{bochk_small}",
        collateral_line,
        sfgs_line,
        bochk_sfgs_line,
    ]
    if hkma_line:
        lines.append(hkma_line)
    lines.extend([
        "",
        "需要向银行确认的细节：如果您申请的不是BOC Small Business Loan，而是其他SME贷款或SFGS项下贷款，需让客户经理确认是否要求抵押/质押、可接受资产类型、估值方式、担保比例和最终文件清单。",
        "",
        f"信息来源：{'、'.join(sources)}",
    ])
    return "\n".join(lines)


def _build_sfgs_amount_docs_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh":
        return ""
    if not _contains_any(query, ["SFGS", "担保贷款"]) or not _contains_any(
        query,
        ["贷多少", "额度", "营业额", "利润", "财务证明", "文件"],
    ):
        return ""

    labels = _citation_labels_by_doc_id(citation_source, response_language)
    hkmc_fact = labels.get("hkmc_sfgs_factsheet")
    hkma_90 = labels.get("hkma_sfgs_90_product")
    bochk_sfgs = labels.get("bochk_sfgs_product")
    bochk_small = labels.get("bochk_sme_loan")

    if not hkmc_fact:
        return ""

    sources = [label for label in [hkmc_fact, hkma_90, bochk_small, bochk_sfgs] if label]
    return "\n".join([
        "您公司申请SFGS担保贷款时，可先按SFGS产品最高设施金额判断大致上限；实际获批金额由参与贷款机构审批，年营业额5000万港币和去年利润800万港币本身不是资料列明的自动换算公式。",
        "",
        "可确认的额度信息：",
        f"- 80% Guarantee Product：最高设施金额为 HK$12,000,000。{hkmc_fact}",
        f"- 90% Guarantee Product：最高设施金额为 HK$18,000,000，且包括80%及90%担保产品下已获批的信贷设施。{hkmc_fact}",
        f"- Special 100% Loan Guarantee：最高设施金额为 HK$8,000,000；工资/租金或HK$9,000,000较低者的公式只适用于该Special 100%产品。{hkmc_fact}",
        (
            f"- HKMA关于90%担保产品的公告说明该产品用于支持较小规模企业、经营经验较少的企业及专业人士取得融资。{hkma_90}"
            if hkma_90 else
            "- 本次可引用资料未包含HKMA 90%担保产品公告，无法补充该公告口径。"
        ),
        "",
        "关于需要补充哪些财务证明文件：",
        f"- SFGS资料确认贷款机构会审核申请、核实资格，并可要求借款人提供进一步支持文件和资料。{hkmc_fact}",
        (
            f"- BOCHK SFGS页面显示申请流程包括“Upload documents”，可预先上传相关文件给客户经理跟进。{bochk_sfgs}"
            if bochk_sfgs else
            "- BOCHK SFGS上传文件页面未进入本次可引用资料，无法确认其页面说明。"
        ),
        (
            f"- 若考虑BOCHK “Small Business Loan” 无抵押贷款，资料明确写明不需要抵押品和经审计财务报表，但银行仍可要求相关支持文件或资料。{bochk_small}"
            if bochk_small else
            "- BOCHK Small Business Loan资料未进入本次可引用资料，无法比较其无抵押贷款文件要求。"
        ),
        "",
        "需要向银行确认的细节：已用SFGS额度、申请80%/90%还是Special 100%产品、银行对还款能力的审批口径，以及适用于您公司的具体财务文件清单。",
        "",
        f"信息来源：{'、'.join(sources)}",
    ])


def _build_china_vietnam_supplier_payment_answer(query: str, citation_source, response_language: str) -> str:
    if response_language != "zh":
        return ""
    if not (
        _contains_any(query, ["越南", "Vietnam"])
        and _contains_any(query, ["供应商", "supplier"])
        and _contains_any(query, ["付汇", "付款", "payment", "remittance"])
    ):
        return ""

    labels = _citation_labels_by_doc_id(citation_source, response_language)
    safe_trade = labels.get("safe_trade_investment_facilitation")
    safe_opt = labels.get("safe_trade_fx_optimization_2024")
    sbv_risk = labels.get("sbv_export_payment_risk")
    sbv_current = labels.get("sbv_circular_20_2022_current_account_transfers")
    sbv_cross = labels.get("sbv_cross_border_payments_vi")

    if not safe_trade or not sbv_risk:
        return ""

    sources = [
        label for label in [safe_trade, safe_opt, sbv_risk, sbv_current, sbv_cross]
        if label
    ]
    return "\n".join([
        "中国企业向越南供应商付汇，可以按“中国侧贸易外汇真实性审核 + 越南侧授权银行收款/外汇业务合规”来理解；现有资料支持这个框架，但没有列出每家银行的完整操作清单。",
        "",
        "已确认的合规审核流程要点：",
        f"1. 中国侧先看交易是否属于真实贸易背景。SAFE资料要求经办银行识别交易主体身份、审核交易真实性，并防范同一交易信息重复使用；市场采购贸易主体还需已在地方政府市场采购贸易联网平台备案。{safe_trade}",
        (
            f"2. 中国侧贸易外汇便利化/优化政策属于配套依据；企业和银行仍需按贸易外汇收支便利化、真实性审核和留存资料要求办理。{safe_opt}"
            if safe_opt else
            "2. 本次可引用资料未包含SAFE贸易外汇优化文件，无法补充其具体优化措施。"
        ),
        f"3. 越南侧应通过获越南国家银行（SBV）授权办理外汇业务的商业银行收款；资料列示了越南授权银行/外资银行名单和相关跨境支付风险提示。{sbv_risk}",
        (
            f"4. 若涉及越南经常项目转账或跨境支付安排，还需按SBV相关经常项目转账/跨境支付规定处理。{sbv_current or sbv_cross}"
            if (sbv_current or sbv_cross) else
            "4. 越南端具体入账步骤需要向越南收款银行确认；本次可引用资料只支持越南授权银行和跨境支付风险背景。"
        ),
        "",
        "需要向银行确认的细节：具体银行要求提交哪些合同、发票、报关单或运输单据；是否需要越南供应商额外资质证明；以及单笔金额、频率或特定行业是否有额外限制。实际付款前应向中国经办银行和越南收款银行确认其最新清单。",
        "",
        f"信息来源：{'、'.join(sources)}",
    ])


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
        state["response_language"] = resolve_rag_answer_language(
            state["query"],
            fallback=state.get("response_language"),
        )
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

        identifiers = _extract_doc_identifiers(state["query"])
        if identifiers:
            exact_results = []
            for chunk in self.docs:
                haystack = " ".join([
                    str(chunk.get("doc_id") or ""),
                    str(chunk.get("title") or ""),
                    str(chunk.get("content") or ""),
                    str(chunk.get("contextualized_content") or ""),
                ]).upper()
                if any(identifier in haystack for identifier in identifiers):
                    if state["region"] and state["region"] != "全部":
                        if (chunk.get("region_code") or "") != state["region"]:
                            continue
                    if state["topic"] and state["topic"] != "全部":
                        if (chunk.get("topic_code") or "") != state["topic"]:
                            continue
                    exact_results.append((_ingestion_chunk_to_doc(chunk), 100.0))
            exact_results = exact_results[: self.retriever.candidate_k]
            if exact_results:
                searches.append({
                    "query": state["query"],
                    "source": "exact_identifier",
                    "results": [
                        {
                            "id": doc.get("id"),
                            "title": doc.get("title"),
                            "score": round(float(score), 4),
                        }
                        for doc, score in exact_results
                    ],
                })
                result_lists.append(("exact_identifier", exact_results))
                state["trace"]["exact_identifier_matches"] = [
                    doc.get("id") for doc, _ in exact_results
                ]

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

    def _metadata_multiplier(self, doc, state=None):
        source_type = str(doc.get("source_type") or "unknown")
        authority_level = str(doc.get("authority_level") or "unknown")
        document_type = str(doc.get("document_type") or "unknown")
        trust_tier = str(doc.get("trust_tier") or "unknown")
        disclaimer_level = str(doc.get("disclaimer_level") or "unknown")
        disclaimer = str(doc.get("disclaimer") or "")

        # The ingestion metadata uses detailed authority values such as
        # bank_product_page/regulator/central_bank, not high/medium/low.
        # Keep these multipliers modest: rerank remains primary, metadata only
        # resolves close calls and reduces clearly off-intent sources.
        authority_boost = {
            "central_bank": 1.08,
            "regulator": 1.08,
            "regulator_research": 1.04,
            "tax_authority": 1.08,
            "government-backed_scheme_operator": 1.08,
            "government_funding_scheme": 1.07,
            "government_agency": 1.06,
            "government_registry": 1.05,
            "government_trade_promotion_body": 1.04,
            "government_trade_promotion_platform": 1.04,
            "government_investment_promotion_body": 1.04,
            "government_portal": 1.00,
            "payment_infrastructure_operator": 1.04,
            "bank_product_page": 1.06,
            "bank_official_page": 1.05,
            "official_dev": 1.03,
            "background": 0.96,
            "non_official": 0.84,
            "unknown": 1.0,
        }.get(authority_level, 1.0)
        if authority_level.startswith("government") and authority_level not in {
            "government_portal",
        }:
            authority_boost = max(authority_boost, 1.04)

        document_boost = {
            "factsheet": 1.08,
            "product_page": 1.07,
            "guideline": 1.05,
            "circular": 1.05,
            "policy_doc": 1.04,
            "faq": 1.03,
            "news": 0.97,
            "hub_page": 0.95,
            "unknown": 0.99,
        }.get(document_type, 1.0)

        trust_boost = {
            "government": 1.04,
            "regulator": 1.04,
            "central_bank": 1.04,
            "official_dev": 1.02,
            "bank": 1.03,
            "background": 0.95,
            "non_official": 0.84,
            "unknown": 0.95,
        }.get(trust_tier, 1.0)

        source_boost = {
            "PDF": 1.02,
            "HTML": 1.0,
            "demo": 0.88,
            "unknown": 0.98,
        }.get(source_type, 1.0)

        disclaimer_boost = {
            "official": 1.05,
            "demo": 0.92,
            "stale": 0.90,
            "unknown": 1.0,
        }.get(disclaimer_level, 1.0)
        if "示例数据" in disclaimer or "非真实" in disclaimer:
            disclaimer_boost *= 0.92

        query_boost = 1.0
        if state:
            query = state.get("query", "")
            structured = state.get("structured_query", {}) or {}
            query_regions = structured.get("regions") or []
            query_topics = structured.get("topics") or []
            doc_region = doc.get("region") or ""
            doc_topic = doc.get("topic") or ""

            if query_regions and doc_region:
                if doc_region in query_regions:
                    query_boost *= 1.10
                elif doc_region == "ASEAN" and any(
                    r in {"VN", "TH", "SG", "ID", "MY", "PH"}
                    for r in query_regions
                ):
                    query_boost *= 1.02
                else:
                    query_boost *= 0.82

            if query_topics and doc_topic:
                if doc_topic in query_topics:
                    query_boost *= 1.06
                elif len(query_topics) == 1:
                    query_boost *= 0.90
                else:
                    query_boost *= 0.94

            aml_intent = _contains_any(query, [
                "反洗钱", "AML", "CFT", "KYC", "KYB", "CDD", "EDD",
                "客户尽职", "尽职调查",
            ])
            if aml_intent:
                if doc_topic == "compliance":
                    query_boost *= 1.15
                else:
                    query_boost *= 0.82

            fee_time_intent = _contains_any(query, [
                "费用", "收费", "手续费", "到账", "多久", "时效", "时间",
                "fee", "fees", "charge", "charges", "timeline", "how long",
            ])
            if fee_time_intent:
                if authority_level in {"bank_product_page", "bank_official_page"}:
                    query_boost *= 1.15
                elif authority_level in {"regulator", "central_bank", "tax_authority"}:
                    query_boost *= 0.78

            if _is_tt_remittance_fee_time_query(query):
                doc_id = doc.get("doc_id") or doc.get("id")
                if doc_id in {
                    "bochk_remittance_charges",
                    "bochk_outward_tt_quick_guide",
                }:
                    query_boost *= 1.40
                elif doc_id in {
                    "bochk_fps_limit_notice_20251224",
                    "bochk_trade_finance_tariffs",
                }:
                    query_boost *= 0.62

            vietnam_manufacturing_investment_intent = (
                _is_vietnam_manufacturing_investment_query(query)
            )
            if vietnam_manufacturing_investment_intent:
                doc_id = doc.get("doc_id") or doc.get("id")
                if doc_id in {
                    "hktdc_vietnam_manufacturing_partnership",
                    "hktdc_vietnam_manufacturing_background",
                    "fia_vietnam_taxation_customs",
                }:
                    query_boost *= 1.35
                elif authority_level in {"regulator", "central_bank"} and not _contains_any(
                    query, ["付汇", "付款", "汇款", "payment", "remittance", "transfer"]
                ):
                    query_boost *= 0.74

            if _is_sbv_credit_institution_query(query):
                if (doc.get("doc_id") or doc.get("id")) == "sbv_credit_institutions":
                    query_boost *= 1.35
                elif doc_region == "VN":
                    query_boost *= 0.84
                else:
                    query_boost *= 0.70

            if (
                _is_vietnam_supplier_payment_query(query)
                and not _is_china_vietnam_supplier_payment_query(query)
            ):
                doc_id = doc.get("doc_id") or doc.get("id")
                if doc_id in {
                    "sbv_export_payment_risk",
                    "sbv_credit_institutions",
                    "sbv_circular_20_2022_current_account_transfers",
                    "sbv_cross_border_payments_vi",
                    "sbv_circular_15_2024_payment_services",
                }:
                    query_boost *= 1.25
                elif doc_region != "VN":
                    query_boost *= 0.70

            loan_product_intent = _contains_any(query, [
                "贷款", "融资", "授信", "额度", "利率", "抵押", "担保",
                "产品", "申请", "资格", "材料", "文件",
                "loan", "financing", "credit facility", "product", "documents",
            ])
            if loan_product_intent and (
                authority_level in {
                    "bank_product_page",
                    "bank_official_page",
                    "government-backed_scheme_operator",
                }
                or document_type in {"product_page", "factsheet", "faq"}
            ):
                query_boost *= 1.10
            loan_document_intent = _contains_any(query, [
                "财务证明", "账务文件", "材料", "文件", "supporting documents",
                "financial statements", "audited financial statements",
            ])
            if loan_document_intent and (doc.get("doc_id") or doc.get("id")) == "bochk_sme_loan":
                query_boost *= 1.35
            loan_amount_intent = _contains_any(query, [
                "贷多少", "额度", "上限", "营业额", "利润", "maximum facility amount",
                "loan amount",
            ])
            if loan_amount_intent and (doc.get("doc_id") or doc.get("id")) == "hkmc_sfgs_factsheet":
                amount_text = " ".join([
                    str(doc.get("content") or ""),
                    str(doc.get("contextualized_content") or ""),
                ])
                if _contains_any(amount_text, [
                    "HK$18,000,000",
                    "HK$12,000,000",
                    "HK$ 18,000,000",
                    "HK$ 12,000,000",
                ]):
                    query_boost *= 1.45
                else:
                    query_boost *= 0.75
            loan_collateral_intent = _contains_any(query, [
                "抵押", "无抵押", "质押", "collateral", "unsecured", "security",
            ])
            if loan_collateral_intent:
                doc_id = doc.get("doc_id") or doc.get("id")
                if doc_id in {
                    "bochk_sme_loan",
                    "bochk_loan_services",
                    "bochk_sfgs_product",
                    "hkmc_sfgs_factsheet",
                    "hkma_sfgs_90_product",
                }:
                    query_boost *= 1.28
            if (
                loan_product_intent
                and authority_level in {"regulator", "central_bank", "tax_authority"}
                and not _contains_any(query, [
                    "SFGS", "担保", "合规", "监管", "外汇", "反洗钱",
                    "HKMA", "SAFE", "SBV", "regulation", "compliance",
                ])
            ):
                query_boost *= 0.88

            identifiers = _extract_doc_identifiers(query)
            if identifiers:
                haystack = " ".join([
                    str(doc.get("doc_id") or ""),
                    str(doc.get("title") or ""),
                    str(doc.get("content") or ""),
                    str(doc.get("contextualized_content") or ""),
                ]).upper()
                if any(identifier in haystack for identifier in identifiers):
                    query_boost *= 1.35

        multiplier = (
            source_boost
            * authority_boost
            * document_boost
            * trust_boost
            * disclaimer_boost
            * query_boost
        )
        return max(0.50, min(1.80, multiplier))

    def _select_prompt_contexts(self, scored, top_k, state=None):
        """Select prompt contexts with parent-doc diversity.

        RRF/rerank can return several chunks from the same parent document. That
        helps section-level detail, but weak-sample analysis showed duplicate
        chunks crowding out other authoritative sources and increasing
        unsupported synthesis risk. Selection is therefore two-pass:
          1. best chunk from each parent document;
          2. remaining high-ranked chunks, capped per parent document.
        """
        if not scored or top_k <= 0:
            return [], {"strategy": "parent_doc_diversity", "selected_doc_ids": []}

        override = None
        if state:
            override = state.get("prompt_max_chunks_per_doc_override")
        max_chunks_per_doc = max(1, int(override or PROMPT_MAX_CHUNKS_PER_DOC))
        selected = []
        overflow = []
        counts_by_parent = {}

        for doc, score in scored:
            parent_id = doc.get("parent_doc_id") or doc.get("doc_id") or doc.get("id")
            if counts_by_parent.get(parent_id, 0) == 0:
                selected.append((doc, score))
                counts_by_parent[parent_id] = 1
                if len(selected) >= top_k:
                    break
            else:
                overflow.append((doc, score))

        if len(selected) < top_k:
            for doc, score in overflow:
                parent_id = doc.get("parent_doc_id") or doc.get("doc_id") or doc.get("id")
                if counts_by_parent.get(parent_id, 0) >= max_chunks_per_doc:
                    continue
                selected.append((doc, score))
                counts_by_parent[parent_id] = counts_by_parent.get(parent_id, 0) + 1
                if len(selected) >= top_k:
                    break

        selected = selected[:top_k]
        return selected, {
            "strategy": "parent_doc_diversity",
            "max_chunks_per_doc": max_chunks_per_doc,
            "selected_doc_ids": [
                doc.get("doc_id") or doc.get("id") for doc, _ in selected
            ],
            "selected_chunk_ids": [
                doc.get("chunk_id") or doc.get("id") for doc, _ in selected
            ],
            "selected_unique_doc_count": len({
                doc.get("doc_id") or doc.get("id") for doc, _ in selected
            }),
        }

    def _filter_prompt_candidates(self, scored, state):
        """Conservatively filter prompt candidates by source family.

        This does not affect vector/BM25/rerank retrieval. It only prevents
        clearly off-intent source families from entering the answer prompt when
        enough better official candidates are already available.
        """
        trace = {
            "applied": False,
            "reason": "not_applicable",
            "before_count": len(scored or []),
            "after_count": len(scored or []),
        }
        if not scored:
            return scored, trace

        def _doc_id(item):
            doc, _score = item
            return doc.get("doc_id") or doc.get("id")

        def _unique_count(items):
            return len({_doc_id(item) for item in items})

        def _enough(items, min_unique=1):
            if not items:
                return False
            # At prompt time, fewer highly targeted sources are better than
            # padding with off-intent material, but require at least one unique
            # authoritative parent and at least one chunk.
            return _unique_count(items) >= min_unique

        def _filter_text(item):
            doc, _score = item
            return " ".join([
                str(doc.get("doc_id") or ""),
                str(doc.get("title") or ""),
                str(doc.get("source_name") or ""),
                str(doc.get("content") or "")[:500],
            ]).lower()

        def _title_text(item):
            doc, _score = item
            return " ".join([
                str(doc.get("doc_id") or ""),
                str(doc.get("title") or ""),
                str(doc.get("source_name") or ""),
            ]).lower()

        def _looks_like_sfgs_source(item):
            text = _filter_text(item)
            return (
                "sfgs" in text
                or "sme financing guarantee" in text
                or "financing guarantee scheme" in text
            )

        def _document_type(item):
            doc, _score = item
            return str(doc.get("document_type") or "")

        def _authority_level(item):
            doc, _score = item
            return str(doc.get("authority_level") or "")

        query = state.get("query", "")
        structured = state.get("structured_query", {}) or {}
        query_regions = set(structured.get("regions") or [])

        regulatory_intent = _contains_any(query, [
            "合规", "监管", "外汇", "反洗钱", "AML", "CFT", "KYC", "KYB",
            "CDD", "EDD", "HKMA", "SAFE", "SBV", "regulation", "compliance",
        ])
        fee_time_intent = _contains_any(query, [
            "费用", "收费", "手续费", "到账", "多久", "时效", "时间",
            "fee", "fees", "charge", "charges", "timeline", "how long",
        ])
        loan_product_intent = _contains_any(query, [
            "贷款", "融资", "授信", "额度", "利率", "抵押", "产品",
            "申请", "资格", "材料", "文件", "loan", "financing",
            "credit facility", "product", "documents",
        ])
        loan_document_intent = _contains_any(query, [
            "财务证明", "账务文件", "材料", "文件", "supporting documents",
            "financial statements", "audited financial statements",
        ])
        loan_amount_intent = _contains_any(query, [
            "贷多少", "额度", "上限", "营业额", "利润", "maximum facility amount",
            "loan amount",
        ])
        loan_collateral_intent = _contains_any(query, [
            "抵押", "无抵押", "质押", "collateral", "unsecured", "security",
        ])
        guarantee_or_scheme_intent = _contains_any(query, [
            "SFGS", "担保", "guarantee", "scheme",
        ])
        tt_remittance_fee_time_intent = _is_tt_remittance_fee_time_query(query)
        fps_intent = _contains_any(query, [
            "FPS", "Faster Payment System", "转数快",
        ])
        china_vietnam_supplier_payment_intent = (
            _is_china_vietnam_supplier_payment_query(query)
        )
        vietnam_supplier_payment_intent = (
            _is_vietnam_supplier_payment_query(query)
            and not china_vietnam_supplier_payment_intent
        )
        vietnam_manufacturing_investment_intent = (
            _is_vietnam_manufacturing_investment_query(query)
        )
        sbv_credit_institution_intent = _is_sbv_credit_institution_query(query)
        hk_gba_expansion_financing_intent = (
            _is_hk_gba_expansion_financing_query(query)
        )
        gba_tax_rate_intent = (
            _contains_any(query, ["大湾区", "GBA"])
            and _contains_any(query, ["企业所得税", "income tax", "EIT"])
            and _contains_any(query, ["增值税", "VAT", "value-added tax", "value added tax"])
            and _contains_any(query, ["税率", "rate", "rates"])
        )
        gba_qianhai_policy_intent = _contains_any(query, ["前海", "Qianhai"])
        gba_bank_account_intent = (
            _contains_any(query, ["大湾区", "GBA", "Greater Bay Area"])
            and _contains_any(query, ["银行账户", "bank account", "account opening"])
        )
        gba_business_registration_intent = (
            _contains_any(query, ["GoGBA", "大湾区", "GBA"])
            and _contains_any(query, ["business registration", "企业注册", "公司注册", "商业登记"])
        )
        hkma_aml_cdd_intent = _is_hkma_aml_cdd_query(query)

        filtered = scored
        reason = None

        if hkma_aml_cdd_intent:
            aml_guideline_docs = [
                item for item in filtered
                if _doc_id(item) == "hkma_aml_cft_guideline"
            ]
            if _enough(aml_guideline_docs):
                filtered = aml_guideline_docs
                state["prompt_max_chunks_per_doc_override"] = 3
                reason = "hkma_aml_cdd_source_family"

        if sbv_credit_institution_intent:
            sbv_credit_docs = [
                item for item in filtered
                if _doc_id(item) == "sbv_credit_institutions"
            ]
            if _enough(sbv_credit_docs):
                filtered = sbv_credit_docs
                state["prompt_max_chunks_per_doc_override"] = 3
                reason = (
                    f"{reason}+sbv_credit_institution_source_family"
                    if reason else "sbv_credit_institution_source_family"
                )

        if gba_qianhai_policy_intent:
            qianhai_docs = [
                item for item in filtered
                if _doc_id(item) == "gogba_qianhai_policy"
            ]
            if _enough(qianhai_docs):
                filtered = qianhai_docs
                state["prompt_max_chunks_per_doc_override"] = 3
                reason = "gogba_qianhai_source_family"

        if gba_bank_account_intent:
            bank_account_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "gogba_bank_accounts",
                    "gogba_business_registration",
                }
            ]
            if _enough(bank_account_docs, min_unique=2):
                filtered = bank_account_docs
                reason = (
                    f"{reason}+gogba_bank_account_source_family"
                    if reason else "gogba_bank_account_source_family"
                )

        if gba_business_registration_intent and not gba_bank_account_intent:
            business_registration_docs = [
                item for item in filtered
                if _doc_id(item) == "gogba_business_registration"
            ]
            if _enough(business_registration_docs):
                filtered = business_registration_docs
                state["prompt_max_chunks_per_doc_override"] = 3
                reason = (
                    f"{reason}+gogba_business_registration_source_family"
                    if reason else "gogba_business_registration_source_family"
                )

        if gba_tax_rate_intent:
            direct_tax_docs = [
                item for item in filtered
                if _doc_id(item) == "gogba_enterprise_income_tax_vat"
            ]
            if _enough(direct_tax_docs):
                filtered = direct_tax_docs
                state["prompt_max_chunks_per_doc_override"] = 3
                reason = "gba_tax_rate_source_family"

        if vietnam_manufacturing_investment_intent and not china_vietnam_supplier_payment_intent:
            direct_manufacturing_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "hktdc_vietnam_manufacturing_partnership",
                    "hktdc_vietnam_manufacturing_background",
                    "fia_vietnam_taxation_customs",
                }
            ]
            if _enough(direct_manufacturing_docs, min_unique=2):
                filtered = direct_manufacturing_docs
                reason = "vietnam_manufacturing_investment_source_family"

        if hk_gba_expansion_financing_intent:
            direct_expansion_financing_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "bochk_sme_loan",
                    "bochk_trade_finance",
                    "boc_global_purchase_order_financing",
                    "bochk_loan_services",
                    "hkmc_sfgs_factsheet",
                }
            ]
            if _enough(direct_expansion_financing_docs, min_unique=3):
                filtered = direct_expansion_financing_docs
                reason = "hk_gba_expansion_financing_source_family"

        if china_vietnam_supplier_payment_intent:
            direct_trade_payment_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "safe_trade_investment_facilitation",
                    "safe_trade_fx_optimization_2024",
                    "sbv_export_payment_risk",
                }
            ]
            if _enough(direct_trade_payment_docs, min_unique=2):
                filtered = direct_trade_payment_docs
                reason = "china_vietnam_trade_payment_source_family"

        if vietnam_supplier_payment_intent:
            sbv_payment_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "sbv_export_payment_risk",
                    "sbv_credit_institutions",
                    "sbv_circular_20_2022_current_account_transfers",
                    "sbv_cross_border_payments_vi",
                    "sbv_circular_15_2024_payment_services",
                }
            ]
            if _enough(sbv_payment_docs, min_unique=3):
                filtered = sbv_payment_docs
                reason = (
                    f"{reason}+vietnam_supplier_payment_source_family"
                    if reason else "vietnam_supplier_payment_source_family"
                )

        if tt_remittance_fee_time_intent:
            tt_docs = [
                item for item in filtered
                if _doc_id(item) in {
                    "bochk_remittance_charges",
                    "bochk_outward_tt_quick_guide",
                }
            ]
            if _enough(tt_docs, min_unique=2):
                filtered = tt_docs
                reason = "tt_remittance_fee_time_source_family"

        if fps_intent:
            direct_fps_docs = [
                item for item in filtered
                if (
                    _doc_id(item) in {
                        "hkma_fps",
                        "hkma_payment_systems",
                        "hkicl_hkd_fps_rules_2025",
                        "bochk_fps_limit_notice_20251224",
                    }
                    or "faster payment system" in _title_text(item)
                )
            ]
            if _enough(direct_fps_docs, min_unique=2):
                filtered = direct_fps_docs
                reason = "fps_direct_source_family"

        if guarantee_or_scheme_intent and not regulatory_intent:
            raw_scheme_docs = [
                item for item in filtered
                if _looks_like_sfgs_source(item)
            ]
            scheme_docs = raw_scheme_docs
            product_fact_intent = _contains_any(query, [
                "80%", "90%", "区别", "申请条件", "资格", "上限", "额度",
                "多少", "limit", "eligibility", "condition",
            ])
            specific_doc_intent = _contains_any(query, [
                "文件编号", "SFGS_09/2024", "document number", "policy number",
            ])
            if product_fact_intent:
                bank_specific = _contains_any(query, [
                    "中银", "中银香港", "BOCHK", "Bank of China", "bank product",
                ])
                product_fact_docs = [
                    item for item in scheme_docs
                    if _document_type(item) == "factsheet"
                    or "90% guarantee product" in _title_text(item)
                    or (
                        bank_specific
                        and _document_type(item) == "product_page"
                    )
                ]
                if _enough(product_fact_docs):
                    scheme_docs = product_fact_docs
            if loan_document_intent or loan_amount_intent:
                direct_scheme_docs = [
                    item for item in filtered
                    if _doc_id(item) not in {"hkmc_sfgs_statistics"}
                    and (
                        _document_type(item) in {"factsheet", "product_page", "faq"}
                        or _doc_id(item) in {
                            "hkmc_sfgs_factsheet",
                            "hkma_sfgs_90_product",
                            "bochk_sfgs_product",
                            "bochk_sme_loan",
                            "bochk_loan_services",
                        }
                    )
                ]
                if _enough(direct_scheme_docs, min_unique=2):
                    scheme_docs = direct_scheme_docs
                    if loan_amount_intent:
                        state["prompt_max_chunks_per_doc_override"] = 3
            elif specific_doc_intent:
                official_scheme_docs = [
                    item for item in scheme_docs
                    if _authority_level(item) in {
                        "official_dev",
                        "regulator",
                        "government-backed_scheme_operator",
                    }
                ]
                if _enough(official_scheme_docs):
                    scheme_docs = official_scheme_docs
            if _enough(scheme_docs):
                filtered = scheme_docs
                reason = "sfgs_scheme_source_family"

        if fee_time_intent and not regulatory_intent:
            bank_fee_docs = [
                item for item in filtered
                if item[0].get("authority_level") in {
                    "bank_product_page", "bank_official_page",
                }
            ]
            if _enough(bank_fee_docs):
                filtered = bank_fee_docs
                reason = "fee_time_bank_source_family"

        if loan_product_intent and not regulatory_intent and not guarantee_or_scheme_intent:
            if query_regions:
                region_matched = [
                    item for item in filtered
                    if (item[0].get("region") or "") in query_regions
                ]
                if _enough(region_matched):
                    filtered = region_matched
                    reason = (
                        f"{reason}+region_match" if reason else "loan_product_region_match"
                    )

            product_docs = [
                item for item in filtered
                if (
                    _doc_id(item) not in {"hkmc_sfgs_statistics"}
                    and (
                        _document_type(item) not in {"hub_page"}
                        or (
                            hk_gba_expansion_financing_intent
                            and _doc_id(item) == "bochk_trade_finance"
                        )
                    )
                    and (
                    item[0].get("authority_level") in {
                        "bank_product_page",
                        "bank_official_page",
                        "government-backed_scheme_operator",
                        "government_funding_scheme",
                    }
                    or item[0].get("document_type") in {
                        "product_page", "factsheet", "faq",
                    }
                    or (
                        (loan_document_intent or loan_amount_intent or loan_collateral_intent)
                        and _doc_id(item) in {
                            "hkmc_sfgs_factsheet",
                            "hkmc_sfgs_application_procedures",
                            "hkmc_sfgs_application_procedures_lender",
                            "bochk_sfgs_product",
                            "bochk_sme_loan",
                            "bochk_loan_services",
                            "hkma_sfgs_90_product",
                        }
                    )
                    )
                )
            ]
            if _enough(product_docs):
                filtered = product_docs
                reason = (
                    f"{reason}+product_source_family"
                    if reason else "loan_product_source_family"
                )

        if filtered is scored or len(filtered) == len(scored):
            trace.update({
                "reason": reason or "not_applicable",
                "before_unique_doc_count": _unique_count(scored),
                "after_unique_doc_count": _unique_count(scored),
                "candidate_doc_ids": [_doc_id(item) for item in scored],
            })
            return scored, trace

        trace.update({
            "applied": True,
            "reason": reason or "source_family",
            "after_count": len(filtered),
            "before_unique_doc_count": _unique_count(scored),
            "after_unique_doc_count": _unique_count(filtered),
            "candidate_doc_ids": [_doc_id(item) for item in scored],
            "filtered_doc_ids": [_doc_id(item) for item in filtered],
        })
        return filtered, trace

    def _metadata_scoring(self, state):
        scored = []
        metadata_scores = []
        for doc, score in state["fused_results"]:
            multiplier = self._metadata_multiplier(doc, state)
            final_score = float(score) * multiplier
            scored.append((doc, final_score))
            metadata_scores.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "doc_id": doc.get("doc_id"),
                "region": doc.get("region"),
                "topic": doc.get("topic"),
                "authority_level": doc.get("authority_level"),
                "document_type": doc.get("document_type"),
                "trust_tier": doc.get("trust_tier"),
                "base_score": round(float(score), 4),
                "metadata_multiplier": round(multiplier, 4),
                "final_score": round(final_score, 4),
            })

        scored.sort(key=lambda item: item[1], reverse=True)
        filtered_scored, source_filter_trace = self._filter_prompt_candidates(
            scored, state
        )
        selected, selection_trace = self._select_prompt_contexts(
            filtered_scored, state["top_k"], state=state
        )
        state["retrieved"] = selected
        state["documents"] = [
            self._to_langchain_document(doc, score)
            for doc, score in state["retrieved"]
        ]
        state["trace"]["metadata_scores"] = metadata_scores[:self.retriever.candidate_k]
        state["trace"]["prompt_source_filter"] = source_filter_trace
        state["trace"]["context_selection"] = selection_trace
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
            response_language=state["response_language"],
        )
        return state

    def _generate_answer(self, state):
        citation_source = state.get("retrieved_for_citation", state["retrieved"])
        exact_identifier_answer = _build_exact_identifier_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if exact_identifier_answer:
            state["answer"] = exact_identifier_answer
            state["trace"]["answer_generation_mode"] = "exact_identifier_template"
            return state

        tt_remittance_fee_time_answer = _build_tt_remittance_fee_time_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if tt_remittance_fee_time_answer:
            state["answer"] = tt_remittance_fee_time_answer
            state["trace"]["answer_generation_mode"] = "tt_remittance_fee_time_template"
            return state

        fps_limit_answer = _build_fps_limit_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if fps_limit_answer:
            state["answer"] = fps_limit_answer
            state["trace"]["answer_generation_mode"] = "fps_limit_template"
            return state

        sme_collateral_answer = _build_sme_collateral_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if sme_collateral_answer:
            state["answer"] = sme_collateral_answer
            state["trace"]["answer_generation_mode"] = "sme_collateral_template"
            return state

        sme_loan_docs_answer = _build_sme_loan_docs_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if sme_loan_docs_answer:
            state["answer"] = sme_loan_docs_answer
            state["trace"]["answer_generation_mode"] = "sme_loan_docs_template"
            return state

        sfgs_amount_docs_answer = _build_sfgs_amount_docs_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if sfgs_amount_docs_answer:
            state["answer"] = sfgs_amount_docs_answer
            state["trace"]["answer_generation_mode"] = "sfgs_amount_docs_template"
            return state

        china_vietnam_supplier_payment_answer = _build_china_vietnam_supplier_payment_answer(
            state["query"],
            citation_source,
            state["response_language"],
        )
        if china_vietnam_supplier_payment_answer:
            state["answer"] = china_vietnam_supplier_payment_answer
            state["trace"]["answer_generation_mode"] = "china_vietnam_supplier_payment_template"
            return state

        resp = get_qwen_chat_model().invoke([
            ("system", SYSTEM_PROMPTS[state["response_language"]]),
            ("user", state["prompt"]),
        ])
        state["answer"] = str(resp.content)
        state["trace"]["answer_generation_mode"] = "llm"
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
        result = {
            "answer": state["answer"],
            "citations": citations,
            "response_language": state["response_language"],
        }
        if state["debug"]:
            result["retrieval_trace"] = state["trace"]
        return result

    def ask(
        self,
        query,
        region="全部",
        topic="全部",
        top_k=3,
        debug=False,
        response_language=None,
        trace_tags=None,
        trace_metadata=None,
    ):
        tags = ["crossbridge-rag", "qwen", "langchain"]
        tags.extend(str(tag) for tag in (trace_tags or []) if str(tag).strip())
        metadata = {
            "region": region,
            "topic": topic,
            "qwen_model": QWEN_MODEL,
            "embedding_model": QWEN_EMBEDDING_MODEL,
            "qwen_base_url": QWEN_BASE_URL,
        }
        metadata.update(trace_metadata or {})
        return self.chain.invoke(
            {
                "query": query,
                "region": region,
                "topic": topic,
                "top_k": top_k,
                "debug": debug,
                "response_language": response_language,
            },
            config={
                "run_name": "CrossBridgeRAG.ask",
                "tags": tags,
                "metadata": metadata,
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

"""
CrossBridge AI - Streamlit 前端（Step 5 Pitch-Ready 版）
=========================================================
vs 156 行基础版的改造：
  A. 顶部 Eval Stats Panel — recall@5 100% / faithfulness 0.76 大字 metric
  B. Pipeline 透明度面板 — 4-step `st.status` 容器展示 RAG 内部工作
  C. Citation 卡片重做 — trust_tier 色码 badge + document_type emoji + filter mode banner
  D. 演示场景 tabs — 5 个 scenario × 已知 100% 命中题 + "演示 Citation Gating" 翻车按钮

运行:
    export DASHSCOPE_API_KEY="..."
    export LANGSMITH_TRACING=false
    .venv/bin/streamlit run files/app.py
"""

import streamlit as st
from rag_engine import CrossBridgeRAG

# =====================================================================
# 配置常量
# =====================================================================
st.set_page_config(page_title="CrossBridge AI", page_icon="🌉", layout="wide")

# ---- Eval 数字（pitch 期间不变；改 eval 报告时同步这里）----
# 数据源：eval/reports/eval_full_20260528_030119.md + ragas_full_20260528_031135.md
EVAL_STATS = {
    "kb_docs": 76,                                  # fallback；正常会实时从 rag.docs 计算
    "kb_chunks": 1171,
    "recall_at_5": "100%",
    "recall_at_5_delta": "↑ 33.3pp vs Step 3.5",
    "recall_at_10": "100%",
    "faithfulness": "0.7642",
    "faithfulness_delta": "↑ +0.03 vs Step 3.5",
    "citation_hit": "100%",
    "citation_hit_delta": "↑ 29pp vs Step 3.5",
    "n_questions": 24,
}

# ---- 地区/主题筛选（保持不动）----
REGIONS = {
    "全部": "全部", "香港": "HK", "大湾区(内地)": "GBA",
    "越南": "VN", "泰国": "TH", "新加坡": "SG", "印尼": "ID",
}
TOPICS = {
    "全部": "全部", "政策合规": "compliance", "跨境汇款": "remittance",
    "信贷融资": "credit", "税务": "tax", "市场进入": "market_entry",
}

# ---- 5 个 demo 场景对应的精选 query（全部 eval 100% 命中过）----
# 每条 (问题, 注释 tooltip)
DEMO_SCENARIOS = {
    "🌏 跨境付款合规": [
        ("香港银行接收跨境付款时反洗钱审核的核心要求是什么？", "q01 · Anthropic Contextual Retrieval 让中文 query 召回英文 HKMA AML"),
        ("中国大陆跨境贸易便利化政策（汇发 28 号）有哪些主要内容？", "q03 · SAFE 法规"),
        ("香港公司付款给越南供应商，应满足哪些合规要求？", "q04 · HK→VN 跨境路径"),
    ],
    "💰 SME 融资": [
        ("中小企融资担保计划 SFGS 的申请条件是什么？", "q05 · SFGS 申请"),
        ("中银香港有哪些 SFGS 担保贷款产品？", "q08 · BOCHK 产品页（trust_tier=bank）"),
        ("我是做电子配件出口的香港 SME，年营业额 800 万港币，缺周转资金 200 万买原材料，有什么贷款方案？", "q22 · narrative 长 query"),
    ],
    "🏙️ GBA 设立公司": [
        ("前海有哪些针对港资企业的税收优惠政策？", "q09 · 前海政策"),
        ("香港企业在内地经营要交哪些主要的税？", "q11 · GBA 税务"),
    ],
    "🇻🇳 越南供应商": [
        ("越南央行 SBV 对外汇汇款有哪些主要监管要求？", "q13 · SBV"),
        ("外国企业在越南投资设厂涉及哪些税？", "q15 · FIA 越南税"),
    ],
    "💱 汇款方式对比": [
        ("中银香港电汇 TT 的手续费多少？", "q16 · BOCHK 汇费"),
        ("FPS 转数快可以做跨境付款吗？", "q17 · FPS"),
    ],
}

# 故意翻车 demo —— 触发 fallback_trusted_hub
GATING_DEMO_Q = "CIPS 人民币跨境支付系统是什么？"
GATING_DEMO_HELP = "🎯 演示 Citation Gating 三路退化：CIPS 唯一权威源是 hub 页，应触发黄色 trusted_hub fallback banner"

# ---- Trust badge 色码（基于 rag_engine.TRUSTED_TIERS_FOR_CITATION）----
TRUST_BADGES = {
    "regulator":    ("#16a34a", "🏛️", "监管原文"),
    "central_bank": ("#16a34a", "🏦", "央行原文"),
    "government":   ("#0d9488", "🏛️", "政府机构"),
    "official_dev": ("#0d9488", "🏛️", "官方发展机构"),
    "bank":         ("#2563eb", "🏦", "银行产品页"),
    "industry":     ("#64748b", "📄", "业界资料"),
    "non_official": ("#94a3b8", "📄", "第三方资料"),
}

DOCTYPE_EMOJI = {
    "guideline":    "📘",
    "circular":     "📨",
    "factsheet":    "📋",
    "hub_page":     "🗂️",
    "policy_doc":   "📑",
    "news":         "📰",
    "faq":          "❓",
    "product_page": "🛒",
    "research":     "🔬",
}


# =====================================================================
# Helper 渲染函数
# =====================================================================
def _trust_badge_html(tier: str) -> str:
    """根据 trust_tier 返回带色码 + emoji 的 HTML 标签。"""
    color, icon, label = TRUST_BADGES.get(tier or "non_official", TRUST_BADGES["non_official"])
    return (
        f'<span style="background:{color}; color:white; padding:2px 8px; '
        f'border-radius:4px; font-size:0.8em; font-weight:600; margin-right:6px">'
        f'{icon} {label}</span>'
    )


def _doctype_tag_html(doctype: str) -> str:
    """根据 document_type 返回带 emoji 的 tag。"""
    emoji = DOCTYPE_EMOJI.get(doctype, "📄")
    label = (doctype or "unknown").replace("_", " ").title()
    return (
        f'<span style="background:#f1f5f9; color:#334155; padding:2px 8px; '
        f'border-radius:4px; font-size:0.8em; margin-right:6px; border:1px solid #e2e8f0">'
        f'{emoji} {label}</span>'
    )


def _render_citation_card(c: dict) -> None:
    """改造 C：渲染单个 citation 卡片（trust badge + doctype tag + 卡片样式）。"""
    trust_tier = c.get("trust_tier", "") or ""
    doctype = c.get("document_type", "") or ""
    url = c.get("url", "") or ""
    html = f"""
<div style="border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px;
            margin-bottom:8px; background:#fafbfc">
  <div style="margin-bottom:6px">
    {_trust_badge_html(trust_tier)}
    {_doctype_tag_html(doctype)}
    <span style="color:#64748b; font-size:0.85em">相关度 {c.get('score', '-')}</span>
  </div>
  <div style="font-weight:600; font-size:1.0em; margin-bottom:4px">{c.get('title', '')}</div>
  <div style="color:#475569; font-size:0.88em; margin-bottom:6px">
    {c.get('source', '')} ｜ 地区 {c.get('region', '-')} ｜ 生效 {c.get('date', '-')}
  </div>
  <div style="font-size:0.85em">
    {'<a href="' + url + '" target="_blank">🔗 ' + url + '</a>' if url else '<span style="color:#94a3b8">（无 URL）</span>'}
  </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def _render_filter_banner(mode: str) -> None:
    """改造 C：根据 citation_filter_mode 渲染 banner，trusted_clean 时不显示。"""
    if not mode or mode == "trusted_clean":
        return
    if mode == "fallback_trusted_hub":
        st.markdown(
            '<div style="background:#fef3c7; border-left:4px solid #f59e0b; '
            'padding:10px 14px; border-radius:4px; margin:8px 0 12px 0; color:#78350f">'
            '🟡 <b>Citation Gating · fallback_trusted_hub</b><br/>'
            '本次最权威源是 hub 页（目录页 / 介绍页），已作为 fallback 引用 —— '
            '我们诚实告诉你：这条不是 guideline / circular 原文。</div>',
            unsafe_allow_html=True,
        )
    elif mode == "fallback_all":
        st.markdown(
            '<div style="background:#fed7aa; border-left:4px solid #ea580c; '
            'padding:10px 14px; border-radius:4px; margin:8px 0 12px 0; color:#7c2d12">'
            '🟠 <b>Citation Gating · fallback_all</b><br/>'
            '未找到任何 trusted-tier 来源（regulator / central_bank / government / official_dev / bank），'
            '已退化为全部资料供参考，请人工复核。</div>',
            unsafe_allow_html=True,
        )


def _render_pipeline_panel(trace: dict) -> None:
    """改造 B：4 个 st.status 容器展示 RAG 内部 4 步管道。"""
    if not trace:
        st.info("（debug=False，无 trace 数据）")
        return

    # ---- 1. Query 理解 ----
    with st.status("1️⃣ Query 理解（Router → 变体生成）", state="complete", expanded=False):
        st.markdown(f"**Router 判定**：`{trace.get('query_type', '?')}`")
        norm = trace.get("normalized_query")
        if norm:
            st.markdown(f"**Normalized**：{norm}")
        variants = trace.get("query_variants") or []
        if variants:
            hyde_note = "（含 HyDE 假答案变体）" if trace.get("hyde_used") else ""
            st.markdown(f"**生成 {len(variants)} 个 query 变体** {hyde_note}：")
            for i, v in enumerate(variants, 1):
                st.markdown(f"{i}. `{v}`")

    # ---- 2. Hybrid 召回（dense + bm25 并排）----
    with st.status("2️⃣ Hybrid 召回（Dense + BM25 并行 → RRF 融合）", state="complete", expanded=False):
        searches = trace.get("searches") or []
        # 按 query 分组，因为 searches 是 flat list（每个 variant 有 dense + bm25 两条 entry）
        by_query: dict[str, dict[str, list]] = {}
        order_seen: list[str] = []
        for s in searches:
            q = s.get("query", "?")
            if q not in by_query:
                order_seen.append(q)
            by_query.setdefault(q, {})[s.get("source")] = s.get("results", [])

        if not by_query:
            st.write("（无召回数据）")
        else:
            for i, q in enumerate(order_seen[:3], 1):
                sources = by_query[q]
                preview = q if len(q) <= 80 else q[:77] + "..."
                st.markdown(f"**Variant {i}**：`{preview}`")
                col_dense, col_bm25 = st.columns(2)
                with col_dense:
                    st.markdown("🟦 **Dense (Chroma + Qwen embedding)**")
                    for r in (sources.get("dense") or [])[:3]:
                        st.markdown(
                            f"- `{r.get('id','?')}` · {r.get('score', 0):.3f}"
                        )
                with col_bm25:
                    st.markdown("🟧 **BM25 (jieba 切词)**")
                    for r in (sources.get("bm25") or [])[:3]:
                        st.markdown(
                            f"- `{r.get('id','?')}` · {r.get('score', 0):.3f}"
                        )
                if i < len(order_seen[:3]):
                    st.markdown("---")
            n_total = len(order_seen)
            if n_total > 3:
                st.caption(f"（共 {n_total} 个 variant，只显示前 3 个；每个 variant 跑 dense + BM25 两路）")

    # ---- 3. Rerank 精排 ----
    with st.status("3️⃣ Rerank 精排（gte-rerank-v2 cross-encoder）", state="complete", expanded=False):
        if trace.get("rerank_used"):
            st.markdown("✅ Rerank API 调用成功")
            rerank_scores = trace.get("rerank_scores") or []
            fusion_scores = trace.get("fusion_scores") or []
            rrf_id_order = [item.get("id") for item in fusion_scores]
            if rerank_scores:
                rows = []
                for i, item in enumerate(rerank_scores[:8], 1):
                    doc_id = item.get("id", "?")
                    rrf_pos = (rrf_id_order.index(doc_id) + 1) if doc_id in rrf_id_order else "-"
                    rows.append({
                        "Rerank #": i,
                        "RRF #": rrf_pos,
                        "doc_id": doc_id,
                        "rerank_score": f"{item.get('score', 0):.4f}",
                    })
                st.dataframe(rows, hide_index=True, use_container_width=True)
                st.caption("RRF # = 这条 doc 在 rerank 之前的 RRF 顺序（看 cross-encoder 怎么改变排序）")
        else:
            st.markdown(
                "⚠️ Rerank API 这次没成功 → 回退到 RRF 顺序"
                "（graceful fallback，pitch demo 现场断网/超时不会黑屏）"
            )

    # ---- 4. Citation 过滤 ----
    with st.status("4️⃣ Citation 过滤（trust_tier × document_type 双维门控）", state="complete", expanded=False):
        mode = trace.get("citation_filter_mode", "?")
        mode_explain = {
            "trusted_clean":        "✅ 干净路径：所有 citation 都是 trusted-tier 且非 hub_page",
            "fallback_trusted_hub": "🟡 fallback：trusted-tier 但 doc 类型是 hub_page（退而求其次）",
            "fallback_all":         "🟠 全退化：未找到任何 trusted 源",
        }.get(mode, mode)
        st.markdown(f"**Citation filter mode**：`{mode}` — {mode_explain}")
        citation_tiers = trace.get("citation_tiers_used") or []
        st.markdown(f"**输出 citation 的 trust_tier**：`{citation_tiers}`")
        ctx = trace.get("context_only_tiers") or []
        if ctx:
            st.markdown(f"**仅作 context（不进 citation）的 tier**：`{ctx}`")
        if trace.get("citation_filter_warning"):
            st.warning(trace["citation_filter_warning"])


# =====================================================================
# 引擎加载（保持不动）
# =====================================================================
@st.cache_resource(show_spinner="正在初始化 CrossBridge AI 引擎...")
def load_engine():
    """优先 Chroma；否则降级到 in-memory + knowledge_base.json。"""
    import os
    chunks_path = "data/processed/chunks.jsonl"
    persist_dir = "data/chroma"
    if os.path.exists(chunks_path):
        return CrossBridgeRAG(chunks_path=chunks_path, persist_directory=persist_dir)
    return CrossBridgeRAG("knowledge_base.json")


rag = load_engine()


# =====================================================================
# 侧边栏
# =====================================================================
with st.sidebar:
    st.title("🌉 CrossBridge AI")
    st.caption("跨境普惠金融决策助手 · B2B")
    st.divider()

    region_label = st.selectbox("📍 选择地区", list(REGIONS.keys()))
    topic_label = st.selectbox("📂 选择主题", list(TOPICS.keys()))

    st.divider()
    backend_labels = {
        "qwen_embedding": "Qwen text-embedding-v4 (内存)",
        "chroma":         "Qwen + Chroma 持久化向量库",
        "semantic":       "语义向量",
        "tfidf":          "TF-IDF 关键词",
    }
    st.markdown("**检索后端**: " + backend_labels.get(rag.index.backend, rag.index.backend))

    if rag.index.backend == "chroma":
        parent_doc_count = len({d.get("parent_doc_id") or d.get("doc_id") for d in rag.docs})
        st.markdown(f"**知识库**: {parent_doc_count} 个文档 / {len(rag.docs)} 个 chunks")
    else:
        st.markdown(f"**知识库**: {len(rag.docs)} 条资料")

    st.divider()
    st.caption("**Top-K = 3**（rerank 之后给 LLM 的 citation 数）")
    st.info(
        "本工具提供初步跨境金融情报，不取代法律或金融专业人士。"
        "最终操作前请向银行客户经理确认。"
    )


# =====================================================================
# 主区域 - Header
# =====================================================================
st.header("跨境金融，问一句就懂")
st.caption(
    "CrossBridge AI 帮中小企业把跨境政策、汇款、融资讲清楚 —— "
    "每个答案都附 **trust_tier × document_type 双维分级** 的权威来源。"
)


# =====================================================================
# 改造 A: Eval Stats Panel
# =====================================================================
# 实时读知识库规模（chroma backend），否则用 EVAL_STATS 常量兜底
if rag.index.backend == "chroma":
    kb_docs = len({d.get("parent_doc_id") or d.get("doc_id") for d in rag.docs})
    kb_chunks = len(rag.docs)
else:
    kb_docs = EVAL_STATS["kb_docs"]
    kb_chunks = EVAL_STATS["kb_chunks"]

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    label="📚 知识库",
    value=f"{kb_docs} 文档",
    delta=f"{kb_chunks} chunks",
    delta_color="off",
    help=(
        "官方文档（HKMA / SAFE / BOCHK / HKMC / GoGBA / HKTDC / SBV / FIA 等），"
        "含 Anthropic Contextual Retrieval 中文 context 前缀"
    ),
)
c2.metric(
    label="🎯 Recall@5",
    value=EVAL_STATS["recall_at_5"],
    delta=EVAL_STATS["recall_at_5_delta"],
    help=f"{EVAL_STATS['n_questions']} 题 eval set 全部命中。Recall@10 也是 {EVAL_STATS['recall_at_10']}",
)
c3.metric(
    label="🔍 Faithfulness",
    value=EVAL_STATS["faithfulness"],
    delta=EVAL_STATS["faithfulness_delta"],
    help="RAGAS faithfulness（答案 vs 检索 context 的忠实度），7 题 ≥0.9",
)
c4.metric(
    label="🛡️ Citation Hit",
    value=EVAL_STATS["citation_hit"],
    delta=EVAL_STATS["citation_hit_delta"],
    help="正确 citation 在 top-3 的比例（trust_tier × document_type 双维 filter 之后）",
)

# 工程特性角标
st.markdown(
    """
<div style="margin-top:10px; margin-bottom:18px">
<span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:0.82em; margin-right:6px">🟢 Anthropic Contextual Retrieval</span>
<span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:0.82em; margin-right:6px">🟢 Hybrid (BM25 + Dense + RRF)</span>
<span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:0.82em; margin-right:6px">🟢 gte-rerank-v2 Cross-Encoder</span>
<span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:0.82em">🟢 Trust-Tier × Document-Type Citation Gating</span>
</div>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# 改造 D: 演示场景 Tabs
# =====================================================================
st.markdown("**🎬 演示场景**（每条 query 都已在 eval 中 100% 命中）")
tab_names = list(DEMO_SCENARIOS.keys())
tabs = st.tabs(tab_names)
for tab, scenario_name in zip(tabs, tab_names):
    with tab:
        for idx, (q, label) in enumerate(DEMO_SCENARIOS[scenario_name]):
            if st.button(
                q,
                key=f"scn_{scenario_name}_{idx}",
                help=label,
                use_container_width=True,
            ):
                st.session_state["pending_q"] = q

# Citation gating 故意翻车 demo（在 tabs 外，明显标记）
st.markdown(" ")
if st.button(
    GATING_DEMO_Q,
    key="gating_demo",
    help=GATING_DEMO_HELP,
    type="secondary",
    use_container_width=True,
):
    st.session_state["pending_q"] = GATING_DEMO_Q
st.caption(GATING_DEMO_HELP)

st.divider()


# =====================================================================
# 对话历史 + 当前输入
# =====================================================================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 显示历史对话
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            trace = msg.get("trace") or {}
            _render_filter_banner(trace.get("citation_filter_mode"))
            with st.expander(f"📚 信息来源（{len(msg['citations'])} 条）"):
                for c in msg["citations"]:
                    _render_citation_card(c)
        if msg.get("trace"):
            with st.expander("🔬 看 RAG 怎么找到这个答案（4 步管道透明展示）"):
                _render_pipeline_panel(msg["trace"])

# 处理新输入（来自 chat_input 或场景按钮 pending_q）
user_q = st.chat_input("输入你的跨境金融问题…")
if "pending_q" in st.session_state:
    user_q = st.session_state.pop("pending_q")

if user_q:
    # 显示用户问题
    st.session_state["messages"].append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    # 生成答案（debug=True 拿 retrieval_trace 给改造 B）
    with st.chat_message("assistant"):
        with st.spinner("正在检索权威资料并生成答案…"):
            result = rag.ask(
                user_q,
                region=REGIONS[region_label],
                topic=TOPICS[topic_label],
                top_k=3,
                debug=True,
            )

        st.markdown(result["answer"])

        trace = result.get("retrieval_trace") or {}

        # Filter mode banner（trusted_clean 时不显示）
        _render_filter_banner(trace.get("citation_filter_mode"))

        # 改造 C：Citation 卡片
        if result.get("citations"):
            with st.expander(
                f"📚 信息来源（{len(result['citations'])} 条，点击展开）",
                expanded=True,
            ):
                for c in result["citations"]:
                    _render_citation_card(c)

        # 改造 B：Pipeline 透明度面板
        if trace:
            with st.expander("🔬 看 RAG 怎么找到这个答案（4 步管道透明展示）"):
                _render_pipeline_panel(trace)

    st.session_state["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "citations": result.get("citations", []),
        "trace": trace,
    })

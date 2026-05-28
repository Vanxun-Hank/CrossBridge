"""
files/ingestion.py — Stage 3 of the RAG data pipeline (Chunking).

读 data/metadata_index.json + data/*.md，把每篇文档切成可检索的 chunks，
输出到 data/processed/chunks.jsonl，每行一个 chunk + 完整 metadata。

Step 2 之后会再加 --persist，把 chunks 灌进 Chroma。当前只支持 JSONL 输出，
让用户先肉眼审一遍切得对不对。

用法:
    .venv/bin/python files/ingestion.py --input data \\
                                        --output data/processed/chunks.jsonl \\
                                        --no-vector \\
                                        --sample 10
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------------------------
# 1. YAML frontmatter 剥离
# ---------------------------------------------------------------------------

YAML_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_yaml_frontmatter(text: str) -> str:
    """剥掉开头的 YAML frontmatter block；没有就原样返回。"""
    match = YAML_FRONTMATTER_PATTERN.match(text)
    if match:
        return text[match.end() :]
    return text


# ---------------------------------------------------------------------------
# 2. 结构化 metadata 提取（regex）
#    仅对监管/政策类文档命中率高，其他短文档允许字段为空。
# ---------------------------------------------------------------------------

CHAPTER_PATTERNS = [
    re.compile(r"Chapter\s+(\d+)", re.IGNORECASE),
    re.compile(r"第\s*([一二三四五六七八九十百千万0-9]+)\s*章"),
]
# 形如 "4.12" / "4.12.3"，常见于 HKMA / SAFE 文档段落编号
SECTION_PATTERN = re.compile(r"(?<![\w.])(\d{1,2}\.\d{1,3}(?:\.\d{1,3})?)(?!\d)")
ARTICLE_PATTERN = re.compile(r"第\s*([一二三四五六七八九十百千万0-9]+)\s*条")
# PDF 转换器留下的页头："## Page 23"
PAGE_PATTERN = re.compile(r"##\s*Page\s+(\d+)", re.IGNORECASE)

# ---------------------------------------------------------------------------
# 2a. region / topic vocabulary 映射
#     metadata_index.json 里是丰富 tag（"Hong Kong" / "AML/CFT"），
#     而 rag_engine + app.py UI 用紧凑代码（"HK" / "compliance"）。
#     ingestion 时把 list-valued tag 映射成标量 *_code 字段，
#     便于 Chroma metadata filter 和 sidebar 选择器对接。
# ---------------------------------------------------------------------------

# region tag (来自 metadata_index.json) -> UI region code
REGION_MAP = {
    "Hong Kong": "HK",
    "Mainland China": "GBA",
    "Greater Bay Area": "GBA",
    "Shenzhen": "GBA",
    "Guangzhou": "GBA",
    "Zhuhai": "GBA",
    "Hengqin": "GBA",
    "Qianhai": "GBA",
    "Vietnam": "VN",
    "Thailand": "TH",
    "Singapore": "SG",
    "Malaysia": "MY",
    "Philippines": "PH",
    "Indonesia": "ID",
    "ASEAN": "ASEAN",
    # cross-border 不映射，跨境主题保持中性
}

# topic tag -> UI topic code（compliance / remittance / credit / tax / market_entry）
TOPIC_MAP = {
    # compliance
    "AML/CFT": "compliance",
    "customer due diligence": "compliance",
    "banking compliance": "compliance",
    "KYB": "compliance",
    "investment compliance": "compliance",
    "foreign exchange regulation": "compliance",
    "foreign contractor withholding tax": "compliance",
    # remittance / 跨境支付
    "telegraphic transfer": "remittance",
    "remittance fees": "remittance",
    "payment systems": "remittance",
    "RTGS": "remittance",
    "FPS": "remittance",
    "CHATS": "remittance",
    "payment infrastructure": "remittance",
    "system linkages": "remittance",
    "FPS rulebook": "remittance",
    "indirect participant": "remittance",
    "foreign exchange": "remittance",
    "cross-border trade": "remittance",
    "cross-border payment": "remittance",
    "trade facilitation": "remittance",
    "trade foreign exchange": "remittance",
    "import export": "remittance",
    "CIPS": "remittance",
    "RMB clearing": "remittance",
    "current account": "remittance",
    "capital account": "remittance",
    "one-way transfer": "remittance",
    "current account transfer": "remittance",
    # credit / 融资
    "SME loan": "credit",
    "SME finance": "credit",
    "SME lending": "credit",
    "financing guarantee": "credit",
    "credit facility": "credit",
    "trade finance": "credit",
    "working capital": "credit",
    "Commercial Data Interchange": "credit",
    "guarantee ratio": "credit",
    "eligibility": "credit",
    # tax
    "tax": "tax",
    "profits tax": "tax",
    "corporate tax": "tax",
    "enterprise income tax": "tax",
    "VAT": "tax",
    "customs": "tax",
    "taxation": "tax",
    "territorial source principle": "tax",
    # market_entry
    "business registration": "market_entry",
    "market entry": "market_entry",
    "market expansion": "market_entry",
    "GBA expansion": "market_entry",
    "Vietnam market entry": "market_entry",
    "foreign investment": "market_entry",
    "manufacturing investment": "market_entry",
    "restricted investment": "market_entry",
    "manufacturing": "market_entry",
    "investment": "market_entry",
    "company setup": "market_entry",
    "company incorporation": "market_entry",
    "SME banking": "market_entry",
    "business account": "market_entry",
    "bank account opening": "market_entry",
    "account opening": "market_entry",
    "digital banking": "market_entry",
    "government funding": "market_entry",
    "preferential policy": "market_entry",
    "Qianhai": "market_entry",
    "Hengqin": "market_entry",
    "Cross-boundary WMC": "market_entry",
}


def _map_region(region_list) -> str:
    """选第一个能映射上 UI vocab 的；都映射不上返回空串。"""
    if not region_list:
        return ""
    if isinstance(region_list, str):
        region_list = [region_list]
    for r in region_list:
        code = REGION_MAP.get(r)
        if code:
            return code
    return ""


def _map_topic(topic_list) -> str:
    if not topic_list:
        return ""
    if isinstance(topic_list, str):
        topic_list = [topic_list]
    for t in topic_list:
        code = TOPIC_MAP.get(t)
        if code:
            return code
    return ""


# ---------------------------------------------------------------------------
# Step 3.5：trust_tier + document_type 推断器
#   - Codex 爬虫计划的 trust_tier vocab，但完全 data-driven 推断（不调 LLM）
#   - 解决 Step 3 边缘 case：Banking Made Easy 等 hub 页噪声会被识别为 hub_page
# ---------------------------------------------------------------------------

TRUST_TIER_LEVELS = [
    "government", "regulator", "central_bank",
    "official_dev", "bank", "industry", "background", "non_official",
]
DOCUMENT_TYPES = [
    "guideline", "circular", "factsheet", "product_page",
    "hub_page", "faq", "news", "policy_doc", "unknown",
]

# authority_level → trust_tier 的直接映射表。这是最干净的信号
#   metadata_index.json 里 authority_level 实际有 15+ 种取值，
#   比 Codex 提的 trust_tier 还细，直接映射比规则推断更准
_AUTH_TO_TIER = {
    "central_bank": "central_bank",
    "regulator": "regulator",
    "regulator_research": "regulator",
    "tax_authority": "regulator",
    "payment_infrastructure_operator": "official_dev",
    "bank_product_page": "bank",
    "bank_official_page": "bank",
}


def infer_trust_tier(parent: dict) -> str:
    """从 authority_level（真正的 source-type 字段）+ issuer 推断 trust_tier。"""
    explicit = (parent.get("trust_tier") or "").strip().lower()
    if explicit in TRUST_TIER_LEVELS:
        return explicit

    auth = (parent.get("authority_level") or "").strip().lower()
    issuer = (parent.get("issuer") or "").lower()

    if auth in _AUTH_TO_TIER:
        return _AUTH_TO_TIER[auth]
    if auth.startswith("government"):
        # government_trade_promotion_platform / body, government_funding_scheme,
        # government_registry, government_agency, government_portal,
        # government-backed_scheme_operator, government_investment_promotion_body
        return "official_dev"

    # issuer 兜底（authority_level 缺失时）
    central_bank_markers = ["monetary authority", "central bank", "state bank of vietnam",
                            "hkma", "央行", "金融管理局"]
    if any(m in issuer for m in central_bank_markers):
        return "central_bank"
    if "bank of china" in issuer or "bochk" in issuer:
        return "bank"
    return "non_official"


# 已知的 hub 页 doc_id 模式。这些是 Step 3 测试时排到 top-1 但其实是导航噪声的
_HUB_DOC_ID_MARKERS = [
    "banking_made_easy",          # hkma_banking_made_easy
    "setting_up_business",        # investhk_setting_up_business
    "trade_finance",              # bochk_trade_finance（"Trade Finance Overview"，导航页）
    "_overview",                  # boc_thailand_overview / 其他 *_overview
    "introduction",               # cips_introduction / boc_thailand_overview "Introduction"
]


def infer_document_type(parent: dict) -> str:
    """从 doc_id + title + URL + authority_level 推断 document_type。"""
    doc_id = (parent.get("id") or "").lower()
    title = (parent.get("title") or "").lower()
    url = (parent.get("source_url") or "").lower()
    auth = (parent.get("authority_level") or "").strip().lower()

    # 1. 已知 hub 页（Step 3 边缘 case 根治）
    if any(m in doc_id for m in _HUB_DOC_ID_MARKERS):
        return "hub_page"

    # 2. 文档类型关键字（标题强信号）
    if "factsheet" in title or "fact sheet" in title:
        return "factsheet"
    if "guideline" in title or "指引" in title or "guidance" in title:
        return "guideline"
    if "circular" in title or "通知" in title or "通告" in title:
        return "circular"
    if "faq" in title or "frequently asked" in title:
        return "faq"

    # 3. URL 模式
    if "/news" in url or "/press" in url:
        return "news"

    # 4. authority_level 兜底
    if auth in ("bank_product_page", "bank_official_page"):
        return "product_page"
    if auth in ("regulator", "regulator_research", "central_bank", "tax_authority"):
        return "policy_doc"
    if auth.startswith("government") or auth == "payment_infrastructure_operator":
        return "policy_doc"
    return "unknown"


# 噪声 pattern：先剥掉，再抽 section 号，避免把文件大小 / 版本号当成段落号
NOISE_PATTERNS = [
    re.compile(r"\(PDF File,[^)]*\)", re.IGNORECASE),           # (PDF File, 67.3 KB)
    re.compile(r"\(\s*\d[\d.]*\s*(?:KB|MB|GB|TB)\s*\)", re.IGNORECASE),  # (10.5 MB)
    re.compile(r"\d+\.\d+\s*(?:KB|MB|GB|TB|%|港元|元|美元|人民币)", re.IGNORECASE),
    re.compile(r"v\d+\.\d+(?:\.\d+)?", re.IGNORECASE),          # v1.2.3
]

# section 抽到的 token 看起来像噪声时再做一次保险过滤
SECTION_TAIL_UNIT = re.compile(r"^\s*(?:KB|MB|GB|TB|%|million|billion|港元|元|美元|人民币|kg|km|°)", re.IGNORECASE)


def _clean_for_structural(text: str) -> str:
    """剥掉已知噪声 pattern，专供 regex 抽段落号用，不影响 chunk 正文。"""
    cleaned = text
    for pat in NOISE_PATTERNS:
        cleaned = pat.sub(" ", cleaned)
    return cleaned


def extract_structural_metadata(chunk_text: str) -> dict:
    out: dict = {}
    cleaned = _clean_for_structural(chunk_text)

    for pat in CHAPTER_PATTERNS:
        m = pat.search(cleaned)
        if m:
            out["chapter"] = m.group(1)
            break

    # 找第一个看起来真的是段落号的 section 候选（排除文件大小等噪声尾巴）
    for m in SECTION_PATTERN.finditer(cleaned):
        tail = cleaned[m.end() : m.end() + 12]
        if SECTION_TAIL_UNIT.match(tail):
            continue
        out["section"] = m.group(1)
        break

    if "section" not in out:
        article_match = ARTICLE_PATTERN.search(cleaned)
        if article_match:
            out["section"] = f"第{article_match.group(1)}条"

    page_match = PAGE_PATTERN.search(chunk_text)  # page 用原文，保留 "## Page N"
    if page_match:
        out["page"] = page_match.group(1)
    return out


# ---------------------------------------------------------------------------
# 3. Token-aware splitter
# ---------------------------------------------------------------------------

def build_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    """
    用 tiktoken cl100k_base 算 token 长度。Qwen 的真实 tokenizer 不同，
    但对中英混合文本而言 token 计数足够接近，用来定 chunk 大小没问题。
    """
    enc = tiktoken.get_encoding("cl100k_base")

    def _token_len(s: str) -> int:
        return len(enc.encode(s, disallowed_special=()))

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=_token_len,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", ". ", " ", ""],
        is_separator_regex=False,
    )


# ---------------------------------------------------------------------------
# 4. Chunk 构造
# ---------------------------------------------------------------------------

def build_chunk_record(
    *,
    parent: dict,
    chunk_index: int,
    chunk_text: str,
    char_start: int,
    char_end: int,
) -> dict:
    """合并 doc-level metadata + chunk-level + structural（regex 抽到的）。"""
    structural = extract_structural_metadata(chunk_text)
    region_list = parent.get("region", []) or []
    topic_list = parent.get("topic", []) or []
    return {
        # doc-level（从 metadata_index.json 继承）
        "doc_id": parent["id"],
        "parent_doc_id": parent["id"],
        "title": parent.get("title"),
        "issuer": parent.get("issuer"),
        "authority_level": parent.get("authority_level"),
        "region": region_list,                                    # 原始 list（保留富信息）
        "topic": topic_list,
        "region_code": _map_region(region_list),                  # UI vocab 标量（HK/GBA/VN/...）
        "topic_code": _map_topic(topic_list),                     # UI vocab 标量（compliance/remittance/...）
        "source_url": parent.get("source_url"),
        "document_url": parent.get("document_url"),
        "source_type": parent.get("source_type"),
        "language": parent.get("language"),
        "demo_relevance": parent.get("demo_relevance"),
        "publish_date": parent.get("publish_date"),
        "effective_date": parent.get("effective_date"),
        # Step 3.5：Codex 计划对齐的 trust 分级 + 文档类型（推断，不调 LLM）
        "trust_tier": infer_trust_tier(parent),
        "document_type": infer_document_type(parent),
        # chunk-level（新生成）
        "chunk_id": f"{parent['id']}__c{chunk_index:04d}",
        "chunk_index": chunk_index,
        "char_start": char_start,
        "char_end": char_end,
        "content": chunk_text,
        # 内容指纹：crawler 周期 ingest 时用来判断 doc 是否真变了。
        # 12 位 sha1 截断够区分（碰撞概率 ~10^-15 量级）且 metadata 体积小
        "content_hash": hashlib.sha1(chunk_text.encode("utf-8")).hexdigest()[:12],
        # structural（可能为空）
        "chapter": structural.get("chapter"),
        "section": structural.get("section"),
        "page": structural.get("page"),
    }


def chunk_document(parent: dict, md_path: Path, splitter) -> list[dict]:
    raw = md_path.read_text(encoding="utf-8")
    body = strip_yaml_frontmatter(raw)

    pieces = splitter.split_text(body)
    records: list[dict] = []
    cursor = 0
    for i, piece in enumerate(pieces):
        # 在原文里定位 piece，便于后续 cite 精准回溯
        idx = body.find(piece, cursor)
        if idx < 0:
            # splitter 有时会规范化空白，定位失败时退化到 cursor
            idx = cursor
        rec = build_chunk_record(
            parent=parent,
            chunk_index=i,
            chunk_text=piece,
            char_start=idx,
            char_end=idx + len(piece),
        )
        # 把 full doc body 缓存进 chunk record，contextual generation 用完即删
        rec["_full_doc_text"] = body
        records.append(rec)
        cursor = idx + 1
    return records


# ---------------------------------------------------------------------------
# Step 4c.C: Anthropic Contextual Retrieval
#   每个 chunk 在 embed/index 前，先让 LLM 生成 50-100 字"文档级 context 前缀"，
#   这样英文 doc 也能被中文 query 匹配（解决 q01: HKMA AML 全英文 / 中文 query）。
#   Anthropic 实测：contextual embedding + contextual BM25 + rerank 把 retrieval
#   错误率压 67%。
# ---------------------------------------------------------------------------

# Anthropic 官方推荐 prompt（中文调整：让 context 走中文以服务中文 query）
CHUNK_CONTEXT_PROMPT_TEMPLATE = """<document title="{doc_title}" issuer="{doc_issuer}">
{doc_content}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{chunk_content}
</chunk>

请用 1-2 句**中文**简洁说明这个 chunk 在整篇文档中的语境，目的是帮助检索匹配。
要包含：
1. 来源文档的机构和主题（如 "HKMA 反洗钱指引 §4.12"）
2. chunk 所在的章节或议题（如 "客户尽职调查 EDD 强化部分"）
不要复述 chunk 原文，只输出简短中文 context（约 50-80 字），不要解释。"""

CONTEXT_DOC_MAX_CHARS = int(os.environ.get("CB_CONTEXT_DOC_MAX_CHARS", "12000"))


def generate_chunk_context(
    chunk_text: str,
    full_doc_text: str,
    doc_title: str,
    doc_issuer: str,
    *,
    model: str = "qwen-plus",
) -> str:
    """调 LLM 生成单个 chunk 的中文 context 前缀。失败返回空串（caller 用原 chunk）。"""
    from openai import OpenAI  # 延迟 import 避免 --no-vector 模式无依赖

    if not chunk_text or not full_doc_text:
        return ""

    # 文档太长时截断（保留前段）。qwen-plus 上下文够用，但 LLM 调用成本随长度线性涨
    doc_excerpt = full_doc_text[:CONTEXT_DOC_MAX_CHARS]

    prompt = CHUNK_CONTEXT_PROMPT_TEMPLATE.format(
        doc_title=doc_title or "Unknown",
        doc_issuer=doc_issuer or "Unknown",
        doc_content=doc_excerpt,
        chunk_content=chunk_text,
    )

    try:
        client = OpenAI(
            api_key=os.environ["DASHSCOPE_API_KEY"],
            base_url=os.environ.get(
                "QWEN_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[Context] failed for {doc_title!r}/{chunk_text[:30]!r}: {type(e).__name__}: {e}")
        return ""


def add_contextual_content_to_chunks(
    records: list[dict],
    *,
    parallel_threads: int = 5,
    model: str = "qwen-plus",
) -> tuple[int, int]:
    """并发为每个 record 加 `contextualized_content` 字段（embed/BM25 用）。
    `content` 字段不动 —— LLM 生成答案时看的还是干净原文。

    返回 (成功数, 失败数)。失败的 chunk 仍然有 contextualized_content（= 原 content）。
    """
    import concurrent.futures as cf

    if not records:
        return (0, 0)

    print(f"[Context] 用 {model} 给 {len(records)} chunks 生成 context "
          f"(并发 {parallel_threads})")
    ok = fail = 0

    def _process(rec: dict) -> tuple[str, bool]:
        full = rec.pop("_full_doc_text", "") or rec.get("content", "")
        ctx = generate_chunk_context(
            rec["content"], full,
            rec.get("title", ""), rec.get("issuer", ""),
            model=model,
        )
        if ctx:
            # Anthropic 模板：context 前缀 + 空行 + 原 chunk
            rec["contextualized_content"] = f"{ctx}\n\n{rec['content']}"
            return rec["chunk_id"], True
        else:
            # 失败时 fallback 用原 content（不污染、不丢内容）
            rec["contextualized_content"] = rec["content"]
            return rec["chunk_id"], False

    with cf.ThreadPoolExecutor(max_workers=parallel_threads) as ex:
        futures = [ex.submit(_process, rec) for rec in records]
        for i, fut in enumerate(cf.as_completed(futures), 1):
            _, success = fut.result()
            if success:
                ok += 1
            else:
                fail += 1
            if i % 50 == 0 or i == len(records):
                print(f"  [Context] {i}/{len(records)} done (ok={ok} fail={fail})")
    return ok, fail


# ---------------------------------------------------------------------------
# 5. Markdown 文件路径解析
# ---------------------------------------------------------------------------

def resolve_md_path(doc: dict, input_root: Path) -> Optional[Path]:
    """metadata_index 里 markdown_file 是工程根相对路径，做一些容错。"""
    candidates: list[Path] = []
    rel = doc.get("markdown_file")
    if rel:
        candidates.append(Path(rel))
        candidates.append(input_root / Path(rel).name)
    candidates.append(input_root / f"{doc['id']}.md")
    for p in candidates:
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------------------
# 6. CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Stage 3 chunker: data/*.md -> data/processed/chunks.jsonl"
    )
    ap.add_argument("--input", default="data",
                    help="数据根目录，必须包含 metadata_index.json 和 *.md")
    ap.add_argument("--output", default="data/processed/chunks.jsonl")
    ap.add_argument("--chunk-size", type=int, default=800,
                    help="token 数（cl100k_base 估算）")
    ap.add_argument("--chunk-overlap", type=int, default=120)
    ap.add_argument("--limit", type=int, default=None,
                    help="只处理前 N 篇文档（快速 smoke test）")
    ap.add_argument("--sample", type=int, default=10,
                    help="跑完打印 N 个随机 chunk 样本，肉眼审")
    ap.add_argument("--seed", type=int, default=42,
                    help="random sample 用的种子，方便复现")
    ap.add_argument("--no-vector", action="store_true",
                    help="(Step 1) 只产出 chunks.jsonl，不灌 Chroma。")
    ap.add_argument("--persist", action="store_true",
                    help="(Step 2) 写入 Chroma 持久化向量库。")
    ap.add_argument("--persist-dir", default="data/chroma",
                    help="Chroma 持久化目录（默认 data/chroma）")
    ap.add_argument("--with-context", action="store_true",
                    help="(Step 4c.C) 给每个 chunk 用 LLM 生成中文 context 前缀（"
                         "Anthropic Contextual Retrieval）。embed/BM25 用 contextualized "
                         "版本，但 LLM 生成答案时仍用原 content。~¥35/1171 chunks。")
    ap.add_argument("--context-model", default="qwen-plus",
                    help="生成 chunk context 用的 LLM (默认 qwen-plus)")
    ap.add_argument("--context-threads", type=int, default=5,
                    help="并发线程数 (默认 5)")
    args = ap.parse_args(argv)

    input_root = Path(args.input)
    index_file = input_root / "metadata_index.json"
    if not index_file.exists():
        print(f"[ingestion] ERROR: {index_file} not found", file=sys.stderr)
        return 1

    docs: list[dict] = json.loads(index_file.read_text(encoding="utf-8"))
    if args.limit:
        docs = docs[: args.limit]

    splitter = build_splitter(args.chunk_size, args.chunk_overlap)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_chunks = 0
    per_doc_counts: list[tuple[str, int]] = []
    all_records: list[dict] = []
    started_at = datetime.now(timezone.utc).isoformat()

    for doc in docs:
        md_path = resolve_md_path(doc, input_root)
        if md_path is None:
            print(f"[ingestion] WARN: markdown not found for {doc['id']}", file=sys.stderr)
            continue
        records = chunk_document(doc, md_path, splitter)
        per_doc_counts.append((doc["id"], len(records)))
        total_chunks += len(records)
        all_records.extend(records)

    # Step 4c.C: 用 LLM 给每个 chunk 加中文 context 前缀
    if args.with_context:
        ok, fail = add_contextual_content_to_chunks(
            all_records,
            parallel_threads=args.context_threads,
            model=args.context_model,
        )
        print(f"[Context] 完成：{ok} 成功 / {fail} 失败")
    else:
        # 没启用 contextual retrieval：丢掉缓存的 _full_doc_text，不写入磁盘
        for r in all_records:
            r.pop("_full_doc_text", None)

    with output_path.open("w", encoding="utf-8") as f:
        for r in all_records:
            # 写盘前再保险清理一次内部字段
            r.pop("_full_doc_text", None)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[ingestion] wrote {total_chunks} chunks across {len(per_doc_counts)} docs -> {output_path}")
    print(f"[ingestion] chunk_size={args.chunk_size} overlap={args.chunk_overlap} started_at={started_at}")
    print()
    print("[ingestion] chunks per doc:")
    for doc_id, count in per_doc_counts:
        print(f"  {count:>4}  {doc_id}")

    if args.sample and all_records:
        random.seed(args.seed)
        n = min(args.sample, len(all_records))
        print()
        print(f"[ingestion] {n} 个随机 chunk 样本（请肉眼审）：")
        print("=" * 88)
        for r in random.sample(all_records, n):
            preview = r["content"].replace("\n", " ")[:280]
            bits: list[str] = []
            if r.get("chapter"):
                bits.append(f"Ch.{r['chapter']}")
            if r.get("section"):
                bits.append(f"§{r['section']}")
            if r.get("page"):
                bits.append(f"p.{r['page']}")
            structural = " ".join(bits) if bits else "(no structural tag)"
            print(
                f"\n[{r['chunk_id']}]"
                f"\n  region={r['region']}  topic={r['topic']}"
                f"\n  authority={r['authority_level']}  lang={r['language']}  {structural}"
                f"\n  content: {preview}{'...' if len(r['content']) > 280 else ''}"
            )
        print("=" * 88)

    if args.persist:
        print()
        print(f"[ingestion] --persist：把 {len(all_records)} 个 chunks 灌进 Chroma "
              f"(persist_dir={args.persist_dir})")
        # 延迟 import 避免 --no-vector 模式拖慢启动
        from rag_engine import ChromaVectorIndex
        index = ChromaVectorIndex(args.persist_dir)
        added = index.add(all_records, skip_existing=True)
        print(f"[ingestion] Chroma 当前 collection 总数: {len(index)} (本次新增 {added})")

    return 0


if __name__ == "__main__":
    sys.exit(main())

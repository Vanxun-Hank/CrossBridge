"""Local fallback for Function 5 Policy & Compliance Q&A.

The production path in ``files/rag_engine.py`` uses Qwen embeddings, Chroma,
BM25, DashScope rerank, and Qwen generation. That path is still preferred.

This module exists for one practical reason: Function 5 must be runnable on a
fresh machine even when API keys, LangChain, Chroma, or DashScope connectivity
are unavailable. It keeps the same ``ask(...)`` contract as ``CrossBridgeRAG``
and returns grounded answers with official-source citations from the local
``data/processed/chunks.jsonl`` corpus.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    import jieba  # type: ignore

    jieba.initialize()
except Exception:  # pragma: no cover - deterministic fallback
    jieba = None


TRUSTED_TIERS_FOR_CITATION = {
    "government",
    "regulator",
    "central_bank",
    "official_dev",
    "bank",
}
NON_CITABLE_DOCUMENT_TYPES = {"hub_page"}

DISCLAIMER_ZH = (
    "CrossBridge AI 仅提供中小企业跨境融资的初步智能参考和操作指引；"
    "所有评估结果、政策解读和优化建议均不取代银行正式审查或专业金融/法律判断。"
    "最终贷款审批结果及合规标准以承办银行官方规定和国家金融监管规则为准。"
)
DISCLAIMER_EN = (
    "CrossBridge AI provides preliminary intelligent reference and operational "
    "guidance only. It does not replace official bank review or professional "
    "financial/legal advice. Final loan approval and compliance standards are "
    "subject to the hosting bank's official rules and applicable financial "
    "regulations."
)

_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
_LATIN_RE = re.compile(r"[A-Za-z0-9_/\-§#.\[\]（）()]+")
_SPACE_RE = re.compile(r"\s+")

REGION_TERMS = {
    "HK": ["香港", "hong kong", "hk", "hkma", "bochk", "hkmc"],
    "GBA": ["大湾区", "大灣區", "内地", "內地", "中国", "中國", "深圳", "前海", "mainland", "china", "safe"],
    "VN": ["越南", "vietnam", "sbv"],
    "TH": ["泰国", "泰國", "thailand", "bot"],
    "SG": ["新加坡", "singapore", "mas"],
    "ID": ["印尼", "印度尼西亚", "印度尼西亞", "indonesia"],
}

TOPIC_TERMS = {
    "compliance": ["合规", "合規", "监管", "監管", "反洗钱", "反洗錢", "aml", "cft", "cdd", "edd", "kyc", "kyb", "尽职", "盡職", "risk"],
    "remittance": ["汇款", "匯款", "付款", "付汇", "付匯", "电汇", "電匯", "tt", "fps", "cips", "payment", "remittance"],
    "credit": ["贷款", "貸款", "融资", "融資", "sfgs", "担保", "擔保", "loan", "finance", "financing"],
    "tax": ["税", "稅", "关税", "關稅", "退税", "退稅", "tariff", "customs", "tax", "vat"],
    "market_entry": ["注册", "註冊", "开户", "開戶", "投资", "投資", "设立", "設立", "incorporation", "setup", "investment"],
}

TOPIC_EXPANSIONS = {
    "compliance": "AML CDD EDD KYB official regulator compliance risk customer due diligence",
    "remittance": "cross-border payment remittance telegraphic transfer foreign exchange bank review",
    "credit": "SME financing loan guarantee scheme eligibility application documents",
    "tax": "tariff customs tax export tax rebate VAT corporate income tax official",
    "market_entry": "company setup business registration bank account opening investment official",
}


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    tokens: list[str] = []
    tokens.extend(token.lower() for token in _LATIN_RE.findall(text))
    for segment in _CJK_RE.findall(text):
        if jieba is not None:
            tokens.extend(token for token in jieba.cut_for_search(segment) if token.strip())
        else:
            tokens.extend(list(segment))
    return [token.strip().lower() for token in tokens if token.strip()]


def _clean_text(text: str, *, limit: int = 420) -> str:
    cleaned = _SPACE_RE.sub(" ", str(text or "")).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "..."


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _detect_response_language(query: str, fallback: str | None = None) -> str:
    value = str(query or "")
    if re.search(r"\bbilingual\b|中英|雙語|双语", value, re.IGNORECASE):
        return "bilingual"
    if re.search(r"用英文|in english|answer in english|reply in english", value, re.IGNORECASE):
        return "en"
    if re.search(r"用中文|in chinese|answer in chinese|reply in chinese", value, re.IGNORECASE):
        return "zh"
    if fallback in {"zh", "en", "bilingual"}:
        return fallback
    cjk_count = len(_CJK_RE.findall(value))
    latin_count = sum(len(token) for token in _LATIN_RE.findall(value) if not token.isupper())
    return "en" if latin_count > cjk_count * 2 and latin_count > 8 else "zh"


def _classify_query(query: str) -> tuple[list[str], list[str]]:
    regions = [code for code, terms in REGION_TERMS.items() if _contains_any(query, terms)]
    topics = [code for code, terms in TOPIC_TERMS.items() if _contains_any(query, terms)]
    return regions, topics


def _expand_query(query: str) -> list[str]:
    regions, topics = _classify_query(query)
    variants = [query]
    if topics:
        variants.append(query + " " + " ".join(TOPIC_EXPANSIONS[t] for t in topics if t in TOPIC_EXPANSIONS))
    if regions:
        variants.append(query + " official policy " + " ".join(regions))
    variants.append(query + " official source compliance guidance")

    seen: set[str] = set()
    out: list[str] = []
    for variant in variants:
        normalized = variant.strip()
        if normalized and normalized not in seen:
            out.append(normalized)
            seen.add(normalized)
    return out[:3]


def _chunk_to_doc(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": chunk.get("chunk_id") or chunk.get("doc_id"),
        "title": chunk.get("title", ""),
        "content": chunk.get("content", ""),
        "source_name": chunk.get("source_name") or chunk.get("issuer", ""),
        "source_url": chunk.get("source_url") or chunk.get("document_url") or "",
        "region": chunk.get("region_code", ""),
        "topic": chunk.get("topic_code", ""),
        "effective_date": chunk.get("effective_date") or chunk.get("publish_date") or "-",
        "publish_date": chunk.get("publish_date") or "-",
        "source_type": chunk.get("source_type") or "unknown",
        "authority_level": chunk.get("authority_level") or "",
        "doc_id": chunk.get("doc_id", ""),
        "parent_doc_id": chunk.get("parent_doc_id") or chunk.get("doc_id") or "",
        "chunk_id": chunk.get("chunk_id", ""),
        "chunk_index": chunk.get("chunk_index", 0),
        "chapter": chunk.get("chapter", ""),
        "section": chunk.get("section", ""),
        "page": chunk.get("page", ""),
        "trust_tier": chunk.get("trust_tier") or "non_official",
        "document_type": chunk.get("document_type") or "unknown",
    }


class LocalComplianceRAG:
    """Runnable local Function 5 engine with BM25, RRF, and citation gating."""

    def __init__(self, chunks_path: str | Path):
        self.chunks_path = Path(chunks_path)
        self.docs = self._load_chunks(self.chunks_path)
        if not self.docs:
            raise RuntimeError(f"No policy chunks found at {self.chunks_path}")
        self.index = SimpleNamespace(backend="local_bm25_rrf")
        self._tokenized_docs = [
            _tokenize(self._index_text(chunk))
            for chunk in self.docs
        ]
        self._doc_lens = [len(tokens) for tokens in self._tokenized_docs]
        self._avgdl = sum(self._doc_lens) / max(1, len(self._doc_lens))
        self._doc_freq: Counter[str] = Counter()
        for tokens in self._tokenized_docs:
            self._doc_freq.update(set(tokens))

    @staticmethod
    def _load_chunks(path: Path) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
        return chunks

    @staticmethod
    def _index_text(chunk: dict[str, Any]) -> str:
        parts = [
            chunk.get("title", ""),
            chunk.get("issuer", ""),
            " ".join(chunk.get("region") or []),
            " ".join(chunk.get("topic") or []),
            chunk.get("contextualized_content") or chunk.get("content") or "",
            chunk.get("chapter", ""),
            chunk.get("section", ""),
        ]
        return "\n".join(str(part) for part in parts if part)

    def _bm25_scores(self, query: str) -> list[float]:
        query_terms = _tokenize(query)
        if not query_terms:
            return [0.0] * len(self.docs)

        n_docs = len(self.docs)
        k1 = 1.5
        b = 0.75
        scores = [0.0] * n_docs
        for term in query_terms:
            df = self._doc_freq.get(term, 0)
            if not df:
                continue
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for i, tokens in enumerate(self._tokenized_docs):
                freq = tokens.count(term)
                if not freq:
                    continue
                denom = freq + k1 * (1.0 - b + b * self._doc_lens[i] / max(self._avgdl, 1.0))
                scores[i] += idf * (freq * (k1 + 1.0)) / denom
        return scores

    def _rank_variant(self, query: str, *, region: str, topic: str, fetch_k: int) -> list[tuple[dict[str, Any], float]]:
        scores = self._bm25_scores(query)
        ranked: list[tuple[int, float]] = []
        for i, score in enumerate(scores):
            if score <= 0:
                continue
            chunk = self.docs[i]
            if region and region != "全部" and (chunk.get("region_code") or "") != region:
                continue
            if topic and topic != "全部" and (chunk.get("topic_code") or "") != topic:
                continue
            ranked.append((i, float(score)))

        ranked.sort(key=lambda item: item[1], reverse=True)
        return [(_chunk_to_doc(self.docs[i]), score) for i, score in ranked[:fetch_k]]

    @staticmethod
    def _rrf_fuse(result_lists: list[list[tuple[dict[str, Any], float]]], *, rrf_k: int = 60) -> list[tuple[dict[str, Any], float]]:
        scores: dict[str, float] = defaultdict(float)
        docs: dict[str, dict[str, Any]] = {}
        for results in result_lists:
            for rank, (doc, _score) in enumerate(results, start=1):
                doc_key = str(doc.get("chunk_id") or doc.get("id"))
                scores[doc_key] += 1.0 / (rrf_k + rank)
                docs.setdefault(doc_key, doc)
        fused = [(docs[key], score) for key, score in scores.items()]
        fused.sort(key=lambda item: item[1], reverse=True)
        return fused

    @staticmethod
    def _dedupe_by_parent(results: list[tuple[dict[str, Any], float]], *, max_per_doc: int = 2) -> list[tuple[dict[str, Any], float]]:
        counts: Counter[str] = Counter()
        out: list[tuple[dict[str, Any], float]] = []
        for doc, score in results:
            parent = str(doc.get("parent_doc_id") or doc.get("doc_id") or doc.get("id"))
            if counts[parent] >= max_per_doc:
                continue
            counts[parent] += 1
            out.append((doc, score))
        return out

    def _retrieve(self, query: str, *, region: str, topic: str, top_k: int) -> tuple[list[tuple[dict[str, Any], float]], dict[str, Any]]:
        query_variants = _expand_query(query)
        result_lists = [
            self._rank_variant(variant, region=region, topic=topic, fetch_k=max(10, top_k * 4))
            for variant in query_variants
        ]
        fused = self._rrf_fuse(result_lists)
        selected = self._dedupe_by_parent(fused)[: max(1, top_k)]
        trace = {
            "mode": "local_fallback",
            "query_variants": query_variants,
            "retrieved_doc_ids": [doc.get("doc_id") or doc.get("id") for doc, _ in selected],
            "rerank_used": False,
            "citation_filter_applied": True,
        }
        return selected, trace

    @staticmethod
    def _citation_gate(results: list[tuple[dict[str, Any], float]]) -> tuple[list[tuple[dict[str, Any], float]], list[tuple[dict[str, Any], float]], str]:
        trusted_clean: list[tuple[dict[str, Any], float]] = []
        trusted_hub: list[tuple[dict[str, Any], float]] = []
        untrusted: list[tuple[dict[str, Any], float]] = []
        for doc, score in results:
            tier = doc.get("trust_tier") or "non_official"
            dtype = doc.get("document_type") or "unknown"
            if tier not in TRUSTED_TIERS_FOR_CITATION:
                untrusted.append((doc, score))
            elif dtype in NON_CITABLE_DOCUMENT_TYPES:
                trusted_hub.append((doc, score))
            else:
                trusted_clean.append((doc, score))

        if trusted_clean:
            return trusted_clean, trusted_hub + untrusted, "trusted_clean"
        if trusted_hub:
            return trusted_hub, untrusted, "fallback_trusted_hub"
        return results, [], "fallback_all"

    @staticmethod
    def _citation_label(index: int, response_language: str) -> str:
        if response_language == "en":
            return f"[Source{index}]"
        if response_language == "bilingual":
            return f"[资料{index}/Source{index}]"
        return f"[资料{index}]"

    @staticmethod
    def _scenario_risks(query: str, response_language: str) -> list[str]:
        lowered = query.lower()
        if response_language == "en":
            if _contains_any(lowered, ["aml", "cdd", "edd", "kyc", "money laundering"]):
                return [
                    "CDD/EDD evidence may be required when the customer profile, transaction purpose, or source of funds is unclear.",
                    "Banks may escalate unusual cross-border payments for sanctions, AML/CFT, or suspicious-transaction review.",
                ]
            if _contains_any(lowered, ["payment", "remittance", "tt", "supplier"]):
                return [
                    "Weak trade-background evidence can delay bank processing or trigger enhanced review.",
                    "Counterparty, invoice, contract, and payment-purpose mismatches are common review issues.",
                ]
            return ["Treat the answer as preliminary guidance and verify the latest rule with the bank or regulator before execution."]

        if _contains_any(lowered, ["aml", "cdd", "edd", "kyc", "反洗钱", "反洗錢", "尽职", "盡職"]):
            return [
                "客户身份、交易目的或资金来源不清晰时，银行可能要求补充 CDD/EDD 材料。",
                "异常跨境付款可能被升级做制裁、AML/CFT 或可疑交易审查。",
            ]
        if _contains_any(lowered, ["付款", "汇款", "匯款", "电汇", "電匯", "供应商", "供應商", "tt"]):
            return [
                "贸易背景证据不足会拖慢银行处理，甚至触发强化审查。",
                "合同、发票、收款方名称、付款用途不一致，是常见退回或补件风险。",
            ]
        if _contains_any(lowered, ["贷款", "貸款", "融资", "融資", "sfgs", "担保", "擔保"]):
            return [
                "担保比例、最高额度和申请材料通常受官方计划条款及银行审批共同约束。",
                "营业额、现金流、负债和还款来源不清晰时，银行可能要求补充财务证明。",
            ]
        return ["本回答是初步政策参考；实际操作前仍需按银行与监管机构的最新要求复核。"]

    @staticmethod
    def _operational_suggestions(response_language: str) -> list[str]:
        if response_language == "en":
            return [
                "Prepare contracts, invoices, shipping/customs documents, counterparty details, and source-of-funds evidence before approaching the bank.",
                "Save the cited official sources and ask the relationship manager to confirm whether any bank-specific checklist applies.",
                "If a fact is not covered by the cited sources, treat it as unconfirmed rather than relying on a generic AI answer.",
            ]
        return [
            "先整理合同、发票、物流/报关文件、交易对手资料和资金来源证明，再向银行提交。",
            "保存下方官方来源链接，并请客户经理确认是否还有银行内部补充清单。",
            "如果下方来源没有覆盖某个细节，应视为“资料库暂未确认”，不要把通用 AI 回答当作正式规则。",
        ]

    def _build_answer(
        self,
        query: str,
        citation_source: list[tuple[dict[str, Any], float]],
        *,
        response_language: str,
        citation_mode: str,
    ) -> str:
        if not citation_source:
            if response_language == "en":
                return (
                    "The current local policy corpus does not contain a directly relevant official source. "
                    "Please verify with the bank or competent regulator before taking action.\n\n"
                    f"Disclaimer: {DISCLAIMER_EN}"
                )
            return (
                "当前本地政策资料库暂未检索到与问题直接相关的官方来源。建议先向承办银行或主管监管机构确认后再操作。\n\n"
                f"免责声明：{DISCLAIMER_ZH}"
            )

        labels = {
            doc.get("chunk_id") or doc.get("id"): self._citation_label(i, response_language)
            for i, (doc, _score) in enumerate(citation_source, start=1)
        }

        if response_language == "en":
            lines = [
                "**Authoritative Answer**",
                "Based on the retrieved official sources, the relevant compliance points are:",
            ]
            for doc, _score in citation_source[:3]:
                label = labels.get(doc.get("chunk_id") or doc.get("id"), "")
                lines.append(f"- {doc.get('title')}: {_clean_text(doc.get('content', ''), limit=320)} {label}")
            lines.extend(["", "**Targeted Compliance Risk Alerts**"])
            lines.extend(f"- {risk}" for risk in self._scenario_risks(query, response_language))
            lines.extend(["", "**Operational Suggestions**"])
            lines.extend(f"- {suggestion}" for suggestion in self._operational_suggestions(response_language))
            if citation_mode != "trusted_clean":
                lines.extend(["", f"Note: citation mode is `{citation_mode}` because no cleaner official source was retrieved in the top results."])
            lines.extend(["", f"Disclaimer: {DISCLAIMER_EN}"])
            return "\n".join(lines)

        if response_language == "bilingual":
            zh = self._build_answer(query, citation_source, response_language="zh", citation_mode=citation_mode)
            en = self._build_answer(query, citation_source, response_language="en", citation_mode=citation_mode)
            return zh + "\n\n---\n\n" + en

        lines = [
            "**权威回答**",
            "根据已检索到的官方/银行来源，可以先按以下要点理解：",
        ]
        for doc, _score in citation_source[:3]:
            label = labels.get(doc.get("chunk_id") or doc.get("id"), "")
            lines.append(f"- **{doc.get('title')}**：{_clean_text(doc.get('content', ''), limit=320)} {label}")
        lines.extend(["", "**针对性合规风险提示**"])
        lines.extend(f"- {risk}" for risk in self._scenario_risks(query, response_language))
        lines.extend(["", "**操作建议**"])
        lines.extend(f"- {suggestion}" for suggestion in self._operational_suggestions(response_language))
        if citation_mode != "trusted_clean":
            lines.extend(["", f"提示：当前 citation mode 为 `{citation_mode}`，说明 top results 中没有更干净的官方原文来源，系统已按可信来源优先退化。"])
        lines.extend(["", f"**固定免责声明**：{DISCLAIMER_ZH}"])
        return "\n".join(lines)

    @staticmethod
    def _format_citations(citation_source: list[tuple[dict[str, Any], float]]) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        seen: set[str] = set()
        for doc, score in citation_source:
            key = str(doc.get("parent_doc_id") or doc.get("doc_id") or doc.get("id"))
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                {
                    "title": doc.get("title", ""),
                    "source": doc.get("source_name", ""),
                    "url": doc.get("source_url", ""),
                    "date": doc.get("effective_date") or doc.get("publish_date") or "-",
                    "region": doc.get("region", ""),
                    "score": round(float(score), 3),
                    "trust_tier": doc.get("trust_tier", ""),
                    "document_type": doc.get("document_type", ""),
                }
            )
        return citations

    def ask(
        self,
        query: str,
        region: str = "全部",
        topic: str = "全部",
        top_k: int = 3,
        debug: bool = False,
        response_language: str | None = None,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        language = _detect_response_language(query, response_language)
        retrieved, trace = self._retrieve(query, region=region, topic=topic, top_k=max(3, top_k))
        citation_source, context_only, citation_mode = self._citation_gate(retrieved)
        trace.update(
            {
                "citation_filter_mode": citation_mode,
                "retrieved_citation_doc_ids": [
                    doc.get("doc_id") or doc.get("id") for doc, _score in citation_source
                ],
                "context_only_doc_ids": [
                    doc.get("doc_id") or doc.get("id") for doc, _score in context_only
                ],
            }
        )
        result = {
            "answer": self._build_answer(
                query,
                citation_source,
                response_language=language,
                citation_mode=citation_mode,
            ),
            "citations": self._format_citations(citation_source),
            "response_language": language,
        }
        if debug:
            result["retrieval_trace"] = trace
        return result


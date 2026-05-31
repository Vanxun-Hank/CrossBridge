#!/usr/bin/env python3
"""Enrich the BOCHK official catalog from current BOCHK/HKMC public sources.

Missing public terms remain null. The script stores field-level provenance,
writes a Markdown diff report, and upserts the resulting catalog into SQLite.
When DASHSCOPE_API_KEY is configured it also records a qwen-plus page-level
extraction pass; deterministic extraction remains the reviewed write path.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
import requests
from pypdf import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.crawl_bochk_products import clean_text
from server.business.catalog import seed_catalog_products

CATALOG_PATH = ROOT / "data" / "official_products" / "bochk_products_latest.json"
REPORT_PATH = ROOT / "data" / "official_products" / "enrichment_report.md"
RAW_DIR = ROOT / "data" / "raw" / "official_products"
DB_PATH = ROOT / "data" / "crossbridge_app.db"
TIMEOUT = 30
ALLOWED_HOSTS = {"www.bochk.com", "bochk.com", "www.hkmc.com.hk", "hkmc.com.hk"}
PROMO_SUFFIX = "，以 BOCHK 最新公告为准"
ORIGINAL_PRODUCT_IDS = {
    "bochk_small_business_loan_unsecured",
    "bochk_sfgs_80_guarantee_product",
    "bochk_import_loan",
    "bochk_import_invoice_financing",
    "bochk_trust_receipt_facilities",
    "bochk_packing_loan",
    "bochk_pre_shipment_financing",
    "bochk_export_invoice_discounting",
    "bochk_supply_chain_finance_solution",
}
ORIGINAL_NULL_FIELDS = {
    "bochk_small_business_loan_unsecured": {"loan_limit_min_hkd", "interest_rate_text", "required_documents"},
    "bochk_sfgs_80_guarantee_product": {"loan_limit_min_hkd", "interest_rate_text", "required_documents"},
    "bochk_import_loan": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "repayment_method_text", "required_documents", "application_thresholds"},
    "bochk_import_invoice_financing": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "repayment_method_text", "application_thresholds"},
    "bochk_trust_receipt_facilities": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "required_documents", "application_thresholds"},
    "bochk_packing_loan": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "repayment_method_text", "application_thresholds"},
    "bochk_pre_shipment_financing": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "application_thresholds"},
    "bochk_export_invoice_discounting": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "repayment_method_text", "application_thresholds"},
    "bochk_supply_chain_finance_solution": {"loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "repayment_method_text", "required_documents", "application_thresholds"},
}

SOURCE_SPECS = {
    "unsecured": "https://www.bochk.com/en/loan/loan/unsecured.html",
    "sfgs": "https://www.bochk.com/dam/smeinone/loan/en.html",
    "overview": "https://www.bochk.com/en/corporate/tradefinance/overview.html",
    "import": "https://www.bochk.com/en/corporate/tradefinance/import.html",
    "export": "https://www.bochk.com/en/corporate/tradefinance/export.html",
    "supply_chain": "https://www.bochk.com/en/loan/loan/tradefinance/supply_chain_finance_solution.html",
    "tariffs": "https://www.bochk.com/dam/corporatebanking/tfs_tariffs_en.pdf",
    "sfgs_factsheet": "https://www.hkmc.com.hk/files/product/6/SFGS%20Factsheet_Eng%20eff%2023%20Sep%202024.pdf",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pdf_text(content: bytes) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)


def visible_text(content: bytes, url: str, content_type: str) -> str:
    if url.lower().endswith(".pdf") or "pdf" in content_type.lower():
        return pdf_text(content)
    return clean_text(content)


def fetch_sources(previous_catalog: dict) -> dict[str, dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = requests.Session()
    session.headers["User-Agent"] = "CrossBridge-BOCHK-Official-Enrichment/1.0"
    sources: dict[str, dict] = {}
    source_specs = dict(SOURCE_SPECS)
    referenced_urls = {
        ref["source_url"]
        for item in previous_catalog.get("products", [])
        for ref in item.get("source_refs", [])
        if ref.get("source_url")
    }
    for index, url in enumerate(sorted(referenced_urls - set(source_specs.values())), start=1):
        source_specs[f"existing_ref_{index}"] = url
    print(f"[enrich-bochk] loaded {len(referenced_urls)} source_refs[*].source_url values from the previous catalog")
    for source_id, url in source_specs.items():
        if urlparse(url).hostname not in ALLOWED_HOSTS:
            raise ValueError(f"Refusing non-official source URL: {url}")
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        content = response.content
        content_type = response.headers.get("content-type", "")
        suffix = ".pdf" if url.lower().endswith(".pdf") or "pdf" in content_type.lower() else ".html"
        raw_path = RAW_DIR / f"{timestamp}_{source_id}{suffix}"
        raw_path.write_bytes(content)
        sources[source_id] = {
            "id": source_id,
            "url": url,
            "checked_at": now_iso(),
            "content_hash": hashlib.sha256(content).hexdigest(),
            "content_type": content_type,
            "http_status": response.status_code,
            "raw_file_path": str(raw_path.relative_to(ROOT)),
            "text": visible_text(content, url, content_type),
        }
        print(f"[enrich-bochk] fetched {source_id}: {response.status_code}")
    return sources


def require_fragments(source: dict, fragments: list[str]) -> None:
    missing = [fragment for fragment in fragments if fragment not in source["text"]]
    if missing:
        raise RuntimeError(f"{source['id']} missing expected official fragments: {missing}")


def source_ref(source: dict) -> dict:
    return {
        "source_url": source["url"],
        "source_checked_at": source["checked_at"],
        "source_content_hash": source["content_hash"],
        "extracted_at": source["checked_at"],
    }


def qwen_page_extractions(sources: dict[str, dict]) -> tuple[str, dict[str, dict]]:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("[enrich-bochk] DASHSCOPE_API_KEY is not configured; qwen-plus pass skipped")
        return "deterministic_official_text_fallback", {}
    base_url = os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
    model = os.environ.get("QWEN_MODEL", "qwen-plus")
    schema = {
        "loan_limit_min_hkd": None,
        "loan_limit_max_hkd": None,
        "loan_limit_text": None,
        "interest_rate_text": None,
        "tenor_text": None,
        "repayment_method_text": None,
        "required_documents": [],
        "application_thresholds": [],
    }
    results = {}
    for source_id, source in sources.items():
        prompt = (
            "Extract only terms explicitly stated in this official BOCHK/HKMC source. "
            "Do not infer, estimate, or convert examples into product-wide terms. "
            "Return JSON with a products array. Each product has product_name and fields shaped like: "
            f"{json.dumps(schema)}. Missing scalar fields must be null and missing lists empty. "
            "Preserve promotional-rate end dates. Source text follows:\n\n"
            + source["text"][:90_000]
        )
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "You extract auditable official product facts. Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        results[source_id] = json.loads(response.json()["choices"][0]["message"]["content"])
        print(f"[enrich-bochk] qwen-plus extracted {source_id}")
    return f"{model}_plus_reviewed_deterministic_write", results


def extraction_fields(product: dict, source: dict) -> dict:
    extracted_at = product["extracted_at"]
    fields = {}
    for key in (
        "loan_limit_min_hkd",
        "loan_limit_max_hkd",
        "loan_limit_text",
        "interest_rate_text",
        "tenor_text",
        "repayment_method_text",
        "required_documents",
        "application_thresholds",
    ):
        value = product.get(key)
        fields[key] = {
            "value": value,
            "source_url": source["url"],
            "extracted_at": extracted_at,
            "reason": None if value not in (None, []) else "官方页面未明确列明",
        }
    return fields


def product(
    *,
    product_id: str,
    name_zh: str,
    name_en: str,
    source: dict,
    scenarios: list[str],
    purposes: list[str],
    description_zh: str,
    description_en: str,
    loan_limit_min_hkd: int | None = None,
    loan_limit_max_hkd: int | None = None,
    loan_limit_text: str | None = None,
    interest_rate_text: str | None = None,
    tenor_text: str | None = None,
    repayment_method_text: str | None = None,
    required_documents: list[str] | None = None,
    application_thresholds: list[str] | None = None,
    fee_text: str | None = None,
    public_guidance: list[str] | None = None,
    extra_sources: list[dict] | None = None,
) -> dict:
    extracted_at = now_iso()
    limit_en = f"Up to HK${loan_limit_max_hkd:,}" if loan_limit_max_hkd is not None else None
    interest_en = None
    if interest_rate_text and "2026-03-31" in interest_rate_text:
        interest_en = "Promotional rate: 25 bps annualised interest-rate discount for online applications (until 2026-03-31); subject to BOCHK's latest announcement"
    elif interest_rate_text and "2026-06-30" in interest_rate_text:
        interest_en = "Promotional rate: 25 bps annualised interest-rate discount for online applications (until 2026-06-30); subject to BOCHK's latest announcement. Standard rate is subject to BOCHK final approval."
    tenor_en = {
        "最长 60 个月": "Up to 60 months",
        "最长 10 年": "Up to 10 years",
        "短期贷款；公开页面未列明具体天数": "Short-term loan; the public page does not state a specific number of days",
        "短期融资；公开页面未列明具体天数": "Short-term financing; the public page does not state a specific number of days",
    }.get(tenor_text)
    item = {
        "id": product_id,
        "product_name": name_zh,
        "product_description": description_zh,
        "business_scenario": scenarios[0],
        "scenarios": scenarios,
        "purposes": purposes,
        "loan_limit_min_hkd": loan_limit_min_hkd,
        "loan_limit_max_hkd": loan_limit_max_hkd,
        "min_requested_amount_hkd": loan_limit_min_hkd,
        "max_requested_amount_hkd": loan_limit_max_hkd,
        "min_annual_turnover_hkd": None,
        "loan_limit_text": loan_limit_text,
        "interest_rate_text": interest_rate_text,
        "tenor_text": tenor_text,
        "repayment_method_text": repayment_method_text,
        "required_documents": required_documents or [],
        "application_thresholds": application_thresholds or [],
        "fee_text": fee_text,
        "public_guidance": public_guidance or [],
        "source_url": source["url"],
        "source_title": name_en,
        "source_checked_at": source["checked_at"],
        "source_content_hash": source["content_hash"],
        "source_refs": [source_ref(source), *(source_ref(x) for x in (extra_sources or []))],
        "extracted_at": extracted_at,
        "review_status": "source_verified_pending_human_review",
        "review_notes": ["Only explicitly published official-source terms are populated; absent terms remain null."],
        "demo_only": False,
        "active": True,
        "localization": {
            "en": {
                "product_name": name_en,
                "product_description": description_en,
                "loan_limit_text": limit_en,
                "interest_rate_text": interest_en,
                "tenor_text": tenor_en,
                "repayment_method_text": None,
                "fee_text": None,
                "public_guidance": [],
                "required_documents": [],
                "application_thresholds": [],
            }
        },
    }
    item["field_extractions"] = extraction_fields(item, source)
    return item


def build_products(s: dict[str, dict]) -> list[dict]:
    require_fragments(s["unsecured"], ["Loan amount up to HK$2 million", "Repayment period of up to 60 months", "Promotion period is from 1 January 2026 to 31 March 2026"])
    require_fragments(s["sfgs"], ["HK$18 million", "10 Years", "Promotion period: From now until 30 June 2026"])
    require_fragments(s["import"], ["L/C Issuance", "Import Loan", "Trust Receipt Facilities", "Import Invoice Financing"])
    require_fragments(s["export"], ["Export Bills Advance", "Packing Loan", "Pre-shipment Financing", "Export Invoice Discounting"])
    require_fragments(s["overview"], ["Guarantee / Bond / Standby L/C", "Forfaiting", "Factoring"])
    require_fragments(s["supply_chain"], ["Invoice Payment", "SC Pre-shipment Financing"])
    require_fragments(s["tariffs"], ["Import invoice financing 1/4% on financing amount HK$500", "Packing loan 1/8% on financing amount HK$350", "Pre-shipment financing 1/4% on financing amount HK$450", "Export invoice discounting 1/4% on financing amount HK$500"])
    require_fragments(s["sfgs_factsheet"], ["10% per", "The non-revolving Facility shall be repaid by instalments"])

    cross_border = ["overseas_procurement", "cross_border_ecommerce", "export_trade", "overseas_investment"]
    imp = ["overseas_procurement", "cross_border_ecommerce"]
    exp = ["export_trade"]
    p = []
    add = lambda **kw: p.append(product(**kw))
    add(product_id="bochk_small_business_loan_unsecured", name_zh="中银「小企业贷款」无抵押贷款", name_en='BOC "Small Business Loan" Unsecured Loan', source=s["unsecured"], scenarios=cross_border, purposes=["working_capital"], description_zh="灵活无抵押小企业贷款。", description_en="Flexible unsecured SME loan.", loan_limit_max_hkd=2_000_000, loan_limit_text="最高 HK$2,000,000", interest_rate_text=f"促销利率：网上渠道申请可享年利率减 25 个基点（截止 2026-03-31）{PROMO_SUFFIX}", tenor_text="最长 60 个月", repayment_method_text="分期贷款、循环贷款或两者组合", application_thresholds=["适用于经营 2 年或以上的企业"])
    add(product_id="bochk_sfgs_80_guarantee_product", name_zh="中小企融资担保计划 - 八成担保产品", name_en="SME Financing Guarantee Scheme - 80% Guarantee Product", source=s["sfgs"], extra_sources=[s["sfgs_factsheet"]], scenarios=cross_border, purposes=["working_capital"], description_zh="经 BOCHK 申请的中小企融资担保计划八成担保产品。", description_en="BOCHK application path for the SFGS 80% Guarantee Product.", loan_limit_max_hkd=18_000_000, loan_limit_text="最高 HK$18,000,000", interest_rate_text=f"促销利率：网上渠道申请可享年利率减 25 个基点（截止 2026-06-30）{PROMO_SUFFIX}；标准利率以 BOCHK 最终审批为准", tenor_text="最长 10 年", repayment_method_text="非循环融资分期偿还；每次偿还本金间隔不超过 3 个月", application_thresholds=["适用于在香港经营至少 1 年的企业", "申请期以 HKMC 不时公布为准"])
    add(product_id="bochk_import_loan", name_zh="进口贷款", name_en="Import Loan", source=s["import"], scenarios=imp, purposes=["procurement_payment", "working_capital"], description_zh="进口托收项下即时付款资金不足时取得货物或单据。", description_en="Import-collection financing when immediate liquidity is insufficient.")
    add(product_id="bochk_import_invoice_financing", name_zh="进口发票融资", name_en="Import Invoice Financing", source=s["import"], extra_sources=[s["tariffs"]], scenarios=imp, purposes=["procurement_payment", "working_capital"], description_zh="赊账采购项下凭供应商发票申请融资。", description_en="Open-account import financing against a supplier invoice.", required_documents=["供应商发票"], fee_text="手续费：融资金额的 1/4%，最低 HK$500")
    add(product_id="bochk_trust_receipt_facilities", name_zh="信托收据融资", name_en="Trust Receipt Facilities", source=s["import"], scenarios=imp, purposes=["procurement_payment", "working_capital"], description_zh="信用证项下付款前取得货物或装运单据。", description_en="Take possession of goods or shipping documents under an L/C before payment.", repayment_method_text="可于信托收据到期日还款")
    add(product_id="bochk_packing_loan", name_zh="打包贷款", name_en="Packing Loan", source=s["export"], extra_sources=[s["tariffs"]], scenarios=exp, purposes=["order_fulfillment", "working_capital"], description_zh="以信用证作担保的装运前生产成本融资。", description_en="Pre-shipment production-cost financing secured by an L/C.", required_documents=["信用证"], fee_text="手续费：融资金额的 1/8%，最低 HK$350")
    add(product_id="bochk_pre_shipment_financing", name_zh="装运前融资", name_en="Pre-shipment Financing", source=s["export"], extra_sources=[s["tariffs"]], scenarios=exp, purposes=["order_fulfillment", "working_capital"], description_zh="收到采购订单后的原材料及营运开支融资。", description_en="Financing for raw materials and overheads after receipt of a purchase order.", repayment_method_text="装运后可通过出口发票贴现、出口押汇或信用证项下出口汇票议付／贴现等方式还款", required_documents=["采购订单或销售合同"], fee_text="手续费：融资金额的 1/4%，最低 HK$450")
    add(product_id="bochk_export_invoice_discounting", name_zh="出口发票贴现", name_en="Export Invoice Discounting", source=s["export"], extra_sources=[s["tariffs"]], scenarios=exp, purposes=["working_capital"], description_zh="交付货物后凭发票和交付证明取得短期贷款。", description_en="Short-term financing against an invoice and evidence of delivery.", tenor_text="短期贷款；公开页面未列明具体天数", required_documents=["发票", "货物交付证明"], fee_text="手续费：融资金额的 1/4%，最低 HK$500")
    add(product_id="bochk_supply_chain_finance_solution", name_zh="供应链融资方案", name_en="Supply Chain Finance Solution", source=s["supply_chain"], scenarios=imp + ["export_trade"], purposes=["procurement_payment", "order_fulfillment", "working_capital"], description_zh="面向核心买方和供应商的综合供应链融资方案。", description_en="Comprehensive supply-chain solution for anchor buyers and suppliers.")

    add(product_id="bochk_lc_issuance", name_zh="信用证开立", name_en="L/C Issuance", source=s["import"], scenarios=imp, purposes=["procurement_payment"], description_zh="根据买方指示向供应商开立信用证。", description_en="Issue an L/C to the supplier on the buyer's instructions.")
    add(product_id="bochk_back_to_back_lc", name_zh="背对背信用证", name_en="Back-to-Back L/C", source=s["import"], scenarios=imp + exp, purposes=["procurement_payment", "order_fulfillment"], description_zh="中间商凭原信用证开立涉及同批货物的另一张信用证。", description_en="Back-to-back L/C for intermediaries.", required_documents=["原信用证（master L/C）"])
    add(product_id="bochk_export_bills_advance", name_zh="出口押汇", name_en="Export Bills Advance", source=s["export"], scenarios=exp, purposes=["working_capital"], description_zh="货物装运后，凭出口托收单据获得现金垫款。", description_en="Cash advance against export bills after shipment.", required_documents=["出口托收单据"])
    add(product_id="bochk_export_bills_lc_negotiation_discount", name_zh="信用证项下出口汇票议付／贴现", name_en="Negotiation / Discount of Export Bills Under L/C", source=s["export"], scenarios=exp, purposes=["working_capital"], description_zh="提交符合信用证条款的出口单据后获得融资。", description_en="Advance against export documents compliant with L/C terms.", required_documents=["信用证项下出口单据"])
    add(product_id="bochk_guarantee_bond_standby_lc", name_zh="担保／保函／备用信用证", name_en="Guarantee / Bond / Standby L/C", source=s["overview"], scenarios=cross_border, purposes=["working_capital"], description_zh="BOCHK 贸易服务概览列出的担保、保函及备用信用证服务。", description_en="Guarantee, bond and standby L/C service listed by BOCHK.")
    add(product_id="bochk_forfaiting", name_zh="福费廷", name_en="Forfaiting", source=s["overview"], scenarios=exp, purposes=["working_capital"], description_zh="BOCHK 贸易服务概览列出的福费廷服务。", description_en="Forfaiting service listed by BOCHK.")
    add(product_id="bochk_factoring", name_zh="保理", name_en="Factoring", source=s["overview"], scenarios=exp, purposes=["working_capital"], description_zh="BOCHK 贸易服务概览列出的保理服务。", description_en="Factoring service listed by BOCHK.")
    add(product_id="bochk_supply_chain_invoice_payment", name_zh="供应链发票付款", name_en="Supply Chain Invoice Payment", source=s["supply_chain"], scenarios=imp + ["export_trade"], purposes=["procurement_payment", "working_capital"], description_zh="核心买方确认付款后，BOCHK 无追索权购买供应商应收账款并提前付款。", description_en="Early supplier payment by non-recourse purchase of receivables after the anchor buyer's undertaking.", required_documents=["发票", "核心买方付款承诺"])
    add(product_id="bochk_supply_chain_pre_shipment_financing", name_zh="供应链装运前融资", name_en="SC Pre-shipment Financing", source=s["supply_chain"], scenarios=["export_trade"], purposes=["order_fulfillment", "working_capital"], description_zh="供应商在核心买方确认付款前取得短期融资。", description_en="Conditional short-term financing before anchor-buyer payment confirmation.", tenor_text="短期融资；公开页面未列明具体天数", required_documents=["核心买方提供的采购订单（PO）或经核心买方确认的销售订单（SO）"])
    return p


def is_missing(value) -> bool:
    return value is None or value == [] or (isinstance(value, str) and ("未列明" in value or "需客户经理确认" in value))


def write_report(old: dict, new: dict, mode: str) -> None:
    lines = [
        "# BOCHK 官方产品补全差异报告",
        "",
        f"- 生成时间：`{new['generated_at']}`",
        f"- 抽取模式：`{mode}`",
        f"- 产品数量：`{len(ORIGINAL_PRODUCT_IDS)}` → `{len(new['products'])}`（新增 `{len(new['products']) - len(ORIGINAL_PRODUCT_IDS)}`）",
        "- 规则：仅写入官方页面明确出现的内容；示例、可能值及估算值不写入筛选字段。",
        "",
        "## 新增产品",
        "",
    ]
    for item in new["products"]:
        if item["id"] not in ORIGINAL_PRODUCT_IDS:
            lines.append(f"- `{item['id']}`：{item['product_name']}")
    lines.extend(["", "## null → 有值", ""])
    keys = ["loan_limit_min_hkd", "loan_limit_max_hkd", "loan_limit_text", "interest_rate_text", "tenor_text", "repayment_method_text", "required_documents", "application_thresholds"]
    changed = 0
    for item in new["products"]:
        for key in keys:
            if key in ORIGINAL_NULL_FIELDS.get(item["id"], set()) and not is_missing(item.get(key)):
                lines.append(f"- `{item['id']}.{key}`：`{item[key]}`")
                changed += 1
    if not changed:
        lines.append("- 无")
    lines.extend(["", "## 仍为 null", ""])
    for item in new["products"]:
        missing = [key for key in keys if is_missing(item.get(key))]
        if missing:
            lines.append(f"- `{item['id']}`：{', '.join(f'`{key}`' for key in missing)}。原因：官方页面未明确列明。")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_db() -> None:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as db:
        seed_catalog_products(db, mode="official", path=CATALOG_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        active = conn.execute("SELECT COUNT(*) FROM loan_products WHERE active = 1 AND demo_only = 0").fetchone()[0]
    print(f"[enrich-bochk] SQLite synced: {active} active official products")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-fetch", action="store_true", help="Reuse the most recent raw snapshots only")
    parser.add_argument("--skip-db-sync", action="store_true")
    args = parser.parse_args()
    old = json.loads(CATALOG_PATH.read_text(encoding="utf-8")) if CATALOG_PATH.exists() else {"products": []}
    if args.skip_fetch:
        raise ValueError("--skip-fetch is reserved for a future snapshot selector")
    sources = fetch_sources(old)
    extraction_mode, qwen = qwen_page_extractions(sources)
    products = build_products(sources)
    catalog = {
        "catalog_status": "source_verified_pending_human_review",
        "catalog_version": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "generated_at": now_iso(),
        "issuer": "Bank of China (Hong Kong)",
        "extraction_mode": extraction_mode,
        "qwen_page_extractions": qwen,
        "products": products,
        "sources": [{k: v for k, v in source.items() if k != "text"} for source in sources.values()],
    }
    shutil.copy2(CATALOG_PATH, CATALOG_PATH.with_suffix(".json.bak")) if CATALOG_PATH.exists() else None
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(old, catalog, extraction_mode)
    if not args.skip_db_sync:
        sync_db()
    print(f"[enrich-bochk] wrote {len(products)} products and {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

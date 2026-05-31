#!/usr/bin/env python3
"""Crawl BOCHK public product pages into a reviewable Function 1 catalog.

The crawler intentionally keeps unpublished terms as unknown. It does not infer
eligibility, pricing, limits, or approval outcomes from examples or promotions.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "official_products"
RAW_DIR = ROOT / "data" / "raw" / "official_products"
LATEST_PATH = OUTPUT_DIR / "bochk_products_latest.json"
USER_AGENT = "CrossBridge-BOCHK-Product-Crawler/1.0"
TIMEOUT_SECONDS = 30
DOMAIN_DELAY_SECONDS = 1.0
OFFICIAL_HOSTS = {"bochk.com", "www.bochk.com"}

UNKNOWN_ZH = "BOCHK 公开页面未列明，需客户经理确认"
UNKNOWN_EN = "Not stated on the BOCHK public page; relationship-manager confirmation required"
APPROVAL_ZH = "实际资格、额度、利率及条款以 BOCHK 最终审批为准"
APPROVAL_EN = "Actual eligibility, limit, interest rate and terms are subject to BOCHK final approval"


class VisibleTextParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas"}
    BREAK_TAGS = {
        "address",
        "article",
        "aside",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif not self.skip_depth and tag in self.BREAK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and tag in self.BREAK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        joined = "".join(self.parts).replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", line).strip() for line in joined.splitlines()]
        return "\n".join(line for line in lines if line)


@dataclass(frozen=True)
class SourceSpec:
    id: str
    url: str
    title: str
    required_markers: tuple[str, ...]


SOURCES = (
    SourceSpec(
        id="bochk_small_business_loan_unsecured",
        url="https://www.bochk.com/en/loan/loan/unsecured.html",
        title='BOC "Small Business Loan" Unsecured Loan',
        required_markers=("Loan amount up to HK$2 million", "Repayment period of up to 60 months"),
    ),
    SourceSpec(
        id="bochk_sfgs_80_guarantee_product",
        url="https://www.bochk.com/dam/smeinone/loan/en.html",
        title="SME Financing Guarantee Scheme",
        required_markers=("80% Guarantee Product", "subject to BOCHK's final approval"),
    ),
    SourceSpec(
        id="bochk_trade_finance_overview",
        url="https://www.bochk.com/en/corporate/tradefinance/overview.html",
        title="BOCHK Trade Finance and Services",
        required_markers=("Import Loan", "Packing Loan", "Pre-shipment Financing"),
    ),
    SourceSpec(
        id="bochk_trade_finance_import",
        url="https://www.bochk.com/en/corporate/tradefinance/import.html",
        title="BOCHK Import Services",
        required_markers=("Import Loan", "Trust Receipt Facilities", "Import Invoice Financing"),
    ),
    SourceSpec(
        id="bochk_trade_finance_export",
        url="https://www.bochk.com/en/corporate/tradefinance/export.html",
        title="BOCHK Export Services",
        required_markers=("Packing Loan", "Pre-shipment Financing", "Export Invoice Discounting"),
    ),
    SourceSpec(
        id="bochk_trade_finance_tariffs",
        url="https://www.bochk.com/dam/corporatebanking/tfs_tariffs_en.pdf",
        title="BOCHK Trade Finance and Services Tariffs",
        required_markers=("Import invoice financing", "Export invoice discounting", "Supply Chain Finance Solution"),
    ),
    SourceSpec(
        id="bochk_supply_chain_finance_solution",
        url="https://www.bochk.com/en/loan/loan/tradefinance/supply_chain_finance_solution.html",
        title="BOCHK Supply Chain Finance Solution",
        required_markers=("Supply Chain Finance Solution",),
    ),
)


def clean_text(content: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(content.decode("utf-8", errors="replace"))
    return parser.text()


def clean_pdf_text(content: bytes) -> str:
    pages = [page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages]
    return "\n".join(pages)


def source_text(content: bytes, content_type: str, url: str) -> str:
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        return clean_pdf_text(content)
    return clean_text(content)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def parse_hkd_amount(amount: str, unit: str) -> int:
    value = float(amount.replace(",", ""))
    multiplier = {"": 1, "thousand": 1_000, "million": 1_000_000}.get(unit.lower(), 1)
    return int(value * multiplier)


def require_source_fragments(source: dict, fragments: tuple[str, ...]) -> None:
    missing = [fragment for fragment in fragments if fragment not in source["text"]]
    if missing:
        raise RuntimeError(f"{source['id']} missing public-detail fragments: {missing}")


def official_source(url: str) -> bool:
    return urlparse(url).hostname in OFFICIAL_HOSTS


def robots_allowed(session: requests.Session, url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    response = session.get(robots_url, timeout=TIMEOUT_SECONDS)
    if response.status_code >= 400:
        return True, f"robots_unavailable:{response.status_code}"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(response.text.splitlines())
    return parser.can_fetch(USER_AGENT, url), "robots_loaded"


def crawl_sources() -> dict[str, dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
    )
    crawled: dict[str, dict] = {}
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for index, spec in enumerate(SOURCES):
        if not official_source(spec.url):
            raise ValueError(f"Refusing non-BOCHK URL: {spec.url}")
        if index:
            time.sleep(DOMAIN_DELAY_SECONDS)
        allowed, robots_status = robots_allowed(session, spec.url)
        if not allowed:
            raise RuntimeError(f"robots.txt blocks {spec.url}")
        response = session.get(spec.url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        content = response.content
        content_type = response.headers.get("content-type", "")
        text = source_text(content, content_type, spec.url)
        missing_markers = [marker for marker in spec.required_markers if marker not in text]
        if missing_markers:
            raise RuntimeError(f"{spec.id} missing markers: {missing_markers}")
        suffix = ".pdf" if "pdf" in content_type.lower() or spec.url.lower().endswith(".pdf") else ".html"
        raw_path = RAW_DIR / f"{timestamp}_{spec.id}{suffix}"
        raw_path.write_bytes(content)
        crawled[spec.id] = {
            "id": spec.id,
            "url": spec.url,
            "title": spec.title,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": sha256(content),
            "http_status": response.status_code,
            "content_type": content_type,
            "robots_status": robots_status,
            "raw_file_path": str(raw_path.relative_to(ROOT)),
            "text": text,
        }
        print(f"[bochk-products] crawled {spec.id} {response.status_code}")
    return crawled


def source_ref(source: dict) -> dict:
    return {
        "source_url": source["url"],
        "source_title": source["title"],
        "source_checked_at": source["checked_at"],
        "source_content_hash": source["content_hash"],
    }


def localized(
    *,
    name_en: str,
    name_zh: str,
    description_en: str,
    description_zh: str,
    limit_en: str = UNKNOWN_EN,
    limit_zh: str = UNKNOWN_ZH,
    interest_en: str = UNKNOWN_EN,
    interest_zh: str = UNKNOWN_ZH,
    tenor_en: str = UNKNOWN_EN,
    tenor_zh: str = UNKNOWN_ZH,
    repayment_en: str = UNKNOWN_EN,
    repayment_zh: str = UNKNOWN_ZH,
    fee_en: str = UNKNOWN_EN,
    fee_zh: str = UNKNOWN_ZH,
    public_guidance_en: list[str] | None = None,
    public_guidance_zh: list[str] | None = None,
    required_documents_en: list[str] | None = None,
    required_documents_zh: list[str] | None = None,
    thresholds_en: list[str] | None = None,
    thresholds_zh: list[str] | None = None,
) -> dict:
    return {
        "product_name": name_zh,
        "product_description": description_zh,
        "loan_limit_text": limit_zh,
        "interest_rate_text": interest_zh,
        "tenor_text": tenor_zh,
        "repayment_method_text": repayment_zh,
        "fee_text": fee_zh,
        "public_guidance": public_guidance_zh or [],
        "required_documents": required_documents_zh or [],
        "application_thresholds": thresholds_zh or [APPROVAL_ZH],
        "localization": {
            "en": {
                "product_name": name_en,
                "product_description": description_en,
                "loan_limit_text": limit_en,
                "interest_rate_text": interest_en,
                "tenor_text": tenor_en,
                "repayment_method_text": repayment_en,
                "fee_text": fee_en,
                "public_guidance": public_guidance_en or [],
                "required_documents": required_documents_en or [],
                "application_thresholds": thresholds_en or [APPROVAL_EN],
            }
        },
    }


def official_product(
    *,
    product_id: str,
    source: dict,
    scenarios: list[str],
    purposes: list[str],
    values: dict,
    min_amount: int | None = None,
    max_amount: int | None = None,
    min_turnover: int | None = None,
    review_notes: list[str] | None = None,
    additional_sources: list[dict] | None = None,
) -> dict:
    notes = review_notes or []
    if max_amount is None:
        notes.append("Public page does not state a general loan-limit range; relationship-manager review required.")
    if min_turnover is None:
        notes.append("Public page does not state a turnover threshold; relationship-manager review required.")
    refs = [source_ref(source), *(source_ref(item) for item in (additional_sources or []))]
    return {
        "id": product_id,
        "business_scenario": scenarios[0],
        "scenarios": scenarios,
        "purposes": purposes,
        "min_requested_amount_hkd": min_amount,
        "max_requested_amount_hkd": max_amount,
        "min_annual_turnover_hkd": min_turnover,
        **values,
        **source_ref(source),
        "source_refs": refs,
        "review_status": "source_verified_pending_human_review",
        "review_notes": notes,
        "demo_only": False,
        "active": True,
    }


def build_catalog(sources: dict[str, dict]) -> dict:
    unsecured = sources["bochk_small_business_loan_unsecured"]
    unsecured_text = unsecured["text"]
    amount_match = re.search(r"Loan amount up to HK\$([\d,.]+)\s*(million|thousand)?", unsecured_text)
    tenor_match = re.search(r"Repayment period of up to (\d+) months", unsecured_text)
    age_match = re.search(r"corporate with (\d+) years or above business operation", unsecured_text)
    if not amount_match or not tenor_match or not age_match:
        raise RuntimeError("Unable to extract public unsecured-loan terms")
    unsecured_max = parse_hkd_amount(amount_match.group(1), amount_match.group(2) or "")
    unsecured_tenor = int(tenor_match.group(1))
    unsecured_age = int(age_match.group(1))

    overview = sources["bochk_trade_finance_overview"]
    import_services = sources["bochk_trade_finance_import"]
    export_services = sources["bochk_trade_finance_export"]
    tariffs = sources["bochk_trade_finance_tariffs"]
    require_source_fragments(
        import_services,
        (
            "Repayment can be made by the trust receipt due date",
            "you can obtain financing from us by presenting your supplier's invoice",
        ),
    )
    require_source_fragments(
        export_services,
        (
            'apply for our "Pre-shipment Financing" for procurement of raw materials and payment of overhead expenses',
            "short-term loan against your invoice and evidence of delivery of goods",
        ),
    )
    require_source_fragments(
        tariffs,
        (
            "Import invoice financing 1/4% on financing amount HK$500",
            "Packing loan 1/8% on financing amount HK$350",
            "Pre-shipment financing 1/4% on financing amount HK$450",
            "Export invoice discounting 1/4% on financing amount HK$500",
            "Service fee Subject to negotiation -",
        ),
    )
    sfgs = sources["bochk_sfgs_80_guarantee_product"]
    # The BOCHK "Loan Amount and Repayment Period at a Glance" table lists the public
    # ceiling for the 80% Guarantee Product. Anchor the hardcoded display values to the
    # live page text so the crawler fails loudly (rather than emitting stale terms) if
    # BOCHK changes the table layout.
    sfgs_glance = re.sub(r"\s+", " ", sfgs["text"])
    if not re.search(r"HK\$\s?18\s?million", sfgs_glance, re.I) or not re.search(
        r"\b10\s?Years?\b", sfgs_glance, re.I
    ):
        raise RuntimeError(
            "SFGS 80% Guarantee Product public terms (HK$18 million / 10 Years) not found "
            "on the BOCHK page; layout may have changed — review before emitting catalog."
        )
    sfgs_max_loan_amount = 18_000_000
    supply_chain = sources["bochk_supply_chain_finance_solution"]
    all_cross_border = [
        "overseas_procurement",
        "cross_border_ecommerce",
        "export_trade",
        "overseas_investment",
    ]
    products = [
        official_product(
            product_id="bochk_small_business_loan_unsecured",
            source=unsecured,
            scenarios=all_cross_border,
            purposes=["working_capital"],
            min_amount=None,
            max_amount=unsecured_max,
            min_turnover=None,
            values=localized(
                name_en='BOC "Small Business Loan" Unsecured Loan',
                name_zh="中银「小企业贷款」无抵押贷款",
                description_en="Flexible unsecured SME loan with instalment-loan and revolving-loan choices.",
                description_zh="提供分期贷款、循环贷款或两者组合的灵活无抵押小企业贷款。",
                limit_en=f"Up to HK${unsecured_max:,}",
                limit_zh=f"最高 HK${unsecured_max:,}",
                tenor_en=f"Up to {unsecured_tenor} months",
                tenor_zh=f"最长 {unsecured_tenor} 个月",
                repayment_en="Instalment loan, revolving loan, or a combination of the two",
                repayment_zh="分期贷款、循环贷款或两者组合",
                thresholds_en=[f"Applicable to corporations with {unsecured_age} years or above business operation", APPROVAL_EN],
                thresholds_zh=[f"适用于经营 {unsecured_age} 年或以上的企业", APPROVAL_ZH],
            ),
            review_notes=[
                "The page contains a dated online-channel discount promotion. The catalog intentionally excludes promotional pricing."
            ],
        ),
        official_product(
            product_id="bochk_sfgs_80_guarantee_product",
            source=sfgs,
            scenarios=all_cross_border,
            purposes=["working_capital"],
            max_amount=sfgs_max_loan_amount,
            values=localized(
                name_en="SME Financing Guarantee Scheme - 80% Guarantee Product",
                name_zh="中小企融资担保计划 - 八成担保产品",
                description_en="BOCHK application path for the HKMCI 80% Guarantee Product.",
                description_zh="经 BOCHK 申请的中小企融资担保计划八成担保产品。",
                limit_en="Up to HK$18,000,000",
                limit_zh="最高 HK$18,000,000",
                tenor_en="Up to 10 years",
                tenor_zh="最长 10 年",
                repayment_en="Instalment-loan example is shown; actual arrangement is subject to BOCHK final approval",
                repayment_zh="公开页面展示分期贷款示例；实际安排以 BOCHK 最终审批为准",
                thresholds_en=[
                    "Applicable to corporations with one year or above business operation",
                    "Application period is subject to HKMC announcements from time to time",
                    APPROVAL_EN,
                ],
                thresholds_zh=[
                    "适用于经营 1 年或以上的企业",
                    "申请期以香港按揭证券有限公司不时公布为准",
                    APPROVAL_ZH,
                ],
            ),
            review_notes=[
                'Loan limit (HK$18 million) and repayment period (10 years) are taken from the BOCHK "Loan Amount and Repayment Period at a Glance" table for the 80% Guarantee Product.'
            ],
        ),
        official_product(
            product_id="bochk_import_loan",
            source=import_services,
            scenarios=["overseas_procurement", "cross_border_ecommerce"],
            purposes=["procurement_payment", "working_capital"],
            values=localized(
                name_en="Import Loan",
                name_zh="进口贷款",
                description_en="BOCHK trade-finance service for import transactions.",
                description_zh="BOCHK 面向进口交易的贸易融资服务。",
                public_guidance_en=[
                    "For taking possession of goods or obtaining shipping documents without making immediate payment under Import Collection.",
                    "The public page states that the service can be used when liquidity is insufficient to settle payment immediately.",
                ],
                public_guidance_zh=[
                    "适用于进口托收项下，希望在未立即付款时取得货物或装运单据的情形。",
                    "公开页面说明：流动资金不足以立即结算款项时，可申请进口贷款。",
                ],
            ),
        ),
        official_product(
            product_id="bochk_import_invoice_financing",
            source=import_services,
            scenarios=["overseas_procurement", "cross_border_ecommerce"],
            purposes=["procurement_payment", "working_capital"],
            values=localized(
                name_en="Import Invoice Financing",
                name_zh="进口发票融资",
                description_en="BOCHK trade-finance service for import invoices.",
                description_zh="BOCHK 面向进口发票的贸易融资服务。",
                fee_en="Handling fee: 1/4% of financing amount, minimum HK$500",
                fee_zh="手续费：融资金额的 1/4%，最低 HK$500",
                public_guidance_en=[
                    "For purchasing goods from a supplier on an open-account basis.",
                ],
                public_guidance_zh=[
                    "适用于以赊账方式向供应商采购货物的情形。",
                ],
                required_documents_en=["Supplier invoice"],
                required_documents_zh=["供应商发票"],
            ),
            additional_sources=[tariffs],
        ),
        official_product(
            product_id="bochk_trust_receipt_facilities",
            source=import_services,
            scenarios=["overseas_procurement"],
            purposes=["procurement_payment", "working_capital"],
            values=localized(
                name_en="Trust Receipt Facilities",
                name_zh="信托收据融资",
                description_en="BOCHK trade-finance facility listed for import services.",
                description_zh="BOCHK 在进口服务中列出的信托收据融资。",
                repayment_en="Repayment can be made by the trust-receipt due date",
                repayment_zh="可于信托收据到期日还款",
                public_guidance_en=[
                    "For taking possession of goods and/or shipping documents under a Letter of Credit before payment.",
                    "Goods may be taken for sale or further processing.",
                ],
                public_guidance_zh=[
                    "适用于信用证项下在付款前取得货物及／或装运单据的情形。",
                    "取得的货物可用于销售或进一步加工。",
                ],
            ),
        ),
        official_product(
            product_id="bochk_packing_loan",
            source=export_services,
            scenarios=["export_trade"],
            purposes=["order_fulfillment", "working_capital"],
            values=localized(
                name_en="Packing Loan",
                name_zh="打包贷款",
                description_en="BOCHK trade-finance service listed for export transactions.",
                description_zh="BOCHK 在出口服务中列出的打包贷款。",
                fee_en="Handling fee: 1/8% of financing amount, minimum HK$350",
                fee_zh="手续费：融资金额的 1/8%，最低 HK$350",
                public_guidance_en=[
                    "Pre-shipment financing for production costs such as raw materials, shipping fees or manufacturing fees.",
                    "The public page states that the facility is secured by the Letter of Credit.",
                ],
                public_guidance_zh=[
                    "装运前用于支付生产成本，例如原材料、运输费用或制造费用。",
                    "公开页面说明：该融资以信用证作为担保。",
                ],
                required_documents_en=["Letter of Credit"],
                required_documents_zh=["信用证"],
            ),
            additional_sources=[tariffs],
        ),
        official_product(
            product_id="bochk_pre_shipment_financing",
            source=export_services,
            scenarios=["export_trade"],
            purposes=["order_fulfillment", "working_capital"],
            values=localized(
                name_en="Pre-shipment Financing",
                name_zh="装运前融资",
                description_en="BOCHK trade-finance service listed for pre-shipment export needs.",
                description_zh="BOCHK 面向出口装运前资金需求列出的融资服务。",
                fee_en="Handling fee: 1/4% of financing amount, minimum HK$450",
                fee_zh="手续费：融资金额的 1/4%，最低 HK$450",
                repayment_en="After shipment, repayment may be arranged with export invoice discounting, export-bills advance, negotiation/discount of export bills under L/C, or similar facilities",
                repayment_zh="货物装运后，可选择出口发票贴现、出口押汇、信用证项下出口汇票议付／贴现等方式灵活还款",
                public_guidance_en=[
                    "For extra financial support upon receipt of a Purchase Order.",
                    "Public-page examples include procurement of raw materials and payment of overhead expenses.",
                ],
                public_guidance_zh=[
                    "适用于收到采购订单后需要额外资金支持的情形。",
                    "公开页面列举的用途包括采购原材料及支付日常营运开支。",
                ],
                required_documents_en=["Purchase Order or Sales Contract"],
                required_documents_zh=["采购订单或销售合同"],
            ),
            additional_sources=[tariffs],
        ),
        official_product(
            product_id="bochk_export_invoice_discounting",
            source=export_services,
            scenarios=["export_trade"],
            purposes=["working_capital"],
            values=localized(
                name_en="Export Invoice Discounting",
                name_zh="出口发票贴现",
                description_en="BOCHK short-term loan service listed for export invoices after goods have been delivered.",
                description_zh="BOCHK 面向已交付货物的出口发票提供的短期贷款服务。",
                fee_en="Handling fee: 1/4% of financing amount, minimum HK$500",
                fee_zh="手续费：融资金额的 1/4%，最低 HK$500",
                tenor_en="Short-term loan; the public page does not state a specific number of days",
                tenor_zh="短期贷款；公开页面未列明具体天数",
                public_guidance_en=[
                    "For obtaining financing on an open-account basis after delivering goods to the buyer.",
                ],
                public_guidance_zh=[
                    "适用于赊账交易，并已向买方交付货物后的融资需求。",
                ],
                required_documents_en=["Invoice", "Evidence of delivery of goods"],
                required_documents_zh=["发票", "货物交付证明"],
            ),
            additional_sources=[tariffs],
        ),
        official_product(
            product_id="bochk_supply_chain_finance_solution",
            source=supply_chain,
            scenarios=["overseas_procurement", "cross_border_ecommerce", "export_trade"],
            purposes=["procurement_payment", "order_fulfillment", "working_capital"],
            values=localized(
                name_en="Supply Chain Finance Solution",
                name_zh="供应链融资方案",
                description_en="BOCHK supply-chain finance solution for corporate transaction flows.",
                description_zh="BOCHK 面向企业交易链路的供应链融资方案。",
                fee_en="Service fee: subject to negotiation",
                fee_zh="服务费：另行协商",
            ),
            additional_sources=[tariffs],
        ),
    ]
    return {
        "catalog_version": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issuer": "Bank of China (Hong Kong)",
        "catalog_status": "source_verified_pending_human_review",
        "products": products,
        "sources": [{key: value for key, value in source.items() if key != "text"} for source in sources.values()],
    }


def write_catalog(catalog: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"[bochk-products] wrote {len(catalog['products'])} products to {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=LATEST_PATH)
    args = parser.parse_args()
    sources = crawl_sources()
    write_catalog(build_catalog(sources), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data"
COLLECTED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat()


SOURCES = [
    {
        "id": "hkma_aml_cft_guideline",
        "raw_file": "01_hkma_aml_cft_guideline.pdf",
        "title": "AML-2 Guideline on Anti-Money Laundering and Counter-Financing of Terrorism (For Authorized Institutions)",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["AML/CFT", "customer due diligence", "banking compliance"],
        "source_url": "https://brdr.hkma.gov.hk/eng/doc-ldg/docId/20230525-4-EN",
        "document_url": "https://brdr.hkma.gov.hk/eng/doc-ldg/docId/getPdf/20230525-4-EN/AML-2.pdf",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Supports compliance checks for a Hong Kong SME making cross-border supplier payments.",
    },
    {
        "id": "hkma_payment_systems",
        "raw_file": "02_hkma_payment_systems.html",
        "title": "Payment Systems",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["payment systems", "RTGS", "FPS", "CHATS"],
        "source_url": "https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/financial-market-infrastructure/payment-systems/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Explains Hong Kong payment infrastructure referenced by cross-border payment workflows.",
    },
    {
        "id": "bochk_remittance_charges",
        "raw_file": "03_bochk_remittance_charges.html",
        "title": "BOCHK Remittance Charges",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["telegraphic transfer", "remittance fees", "business banking"],
        "source_url": "https://www.bochk.com/en/crossborder/remittance/charges.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides bank-side fee evidence for SME supplier remittance scenarios.",
    },
    {
        "id": "safe_trade_investment_facilitation",
        "raw_file": "04_safe_trade_investment_facilitation.html",
        "title": "国家外汇管理局关于进一步深化改革促进跨境贸易投资便利化的通知",
        "issuer": "State Administration of Foreign Exchange",
        "authority_level": "regulator",
        "region": ["Mainland China", "cross-border"],
        "topic": ["cross-border trade", "foreign exchange", "trade facilitation"],
        "source_url": "https://www.safe.gov.cn/safe/2023/1208/23788.html",
        "source_type": "HTML",
        "language": "zh-CN",
        "demo_relevance": "Supports Mainland China foreign exchange policy context for Shenzhen expansion.",
    },
    {
        "id": "hkmc_sfgs_factsheet",
        "raw_file": "05_hkmc_sfgs_factsheet.pdf",
        "title": "SME Financing Guarantee Scheme Factsheet",
        "issuer": "HKMC Insurance Limited",
        "authority_level": "government-backed_scheme_operator",
        "region": ["Hong Kong"],
        "topic": ["SME loan", "financing guarantee", "credit facility"],
        "source_url": "https://www.hkmc.com.hk/eng/our_business/sme_financing_guarantee_scheme.html",
        "document_url": "https://www.hkmc.com.hk/files/product/6/SFGS%20Factsheet_Eng%20eff%2023%20Sep%202024.pdf",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Provides official SME financing guarantee evidence for credit recommendations.",
    },
    {
        "id": "bochk_trade_finance",
        "raw_file": "06_bochk_trade_finance.html",
        "title": "BOCHK Trade Finance Overview",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["trade finance", "SME banking", "import export"],
        "source_url": "https://www.bochk.com/en/corporate/tradefinance/overview.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports bank product recommendations for import/export and supplier payment needs.",
    },
    {
        "id": "hkma_banking_made_easy",
        "raw_file": "07_hkma_banking_made_easy.html",
        "title": "Banking Made Easy Initiative",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong"],
        "topic": ["SME banking", "bank account opening", "digital banking"],
        "source_url": "https://www.hkma.gov.hk/eng/key-functions/banking/banking-regulatory-and-supervisory-regime/banking-made-easy-initiative/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports SME onboarding and banking access assumptions in the demo.",
    },
    {
        "id": "gogba_business_registration",
        "raw_file": "08_gogba_business_registration.pdf",
        "title": "GoGBA Guide: Business Registration",
        "issuer": "HKTDC GoGBA",
        "authority_level": "government_trade_promotion_platform",
        "region": ["Greater Bay Area", "Mainland China", "Shenzhen"],
        "topic": ["business registration", "market entry", "GBA expansion"],
        "source_url": "https://gogba.hktdc.com/doc/gotoguide/business_registration_en.pdf",
        "document_url": "https://gogba.hktdc.com/doc/gotoguide/business_registration_en.pdf",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Supports the Shenzhen setup path for a Hong Kong SME expanding into the GBA.",
    },
    {
        "id": "hktdc_vietnam_manufacturing_partnership",
        "raw_file": "09_hktdc_vietnam_manufacturing_partnership.html",
        "title": "Manufacturing Partnership and Investment",
        "issuer": "Hong Kong Trade Development Council",
        "authority_level": "government_trade_promotion_body",
        "region": ["Vietnam", "ASEAN", "cross-border"],
        "topic": ["Vietnam market entry", "manufacturing", "investment"],
        "source_url": "https://beltandroad.hktdc.com/en/sme-corner/manufacturing-partnership-and-investment",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports Vietnam supplier and expansion context in the pitch demo.",
    },
    {
        "id": "investhk_setting_up_business",
        "raw_file": "10_investhk_setting_up_business.html",
        "title": "Setting Up Business in Hong Kong",
        "issuer": "Invest Hong Kong",
        "authority_level": "government_investment_promotion_body",
        "region": ["Hong Kong"],
        "topic": ["company setup", "business registration", "tax", "market entry"],
        "source_url": "https://www.investhk.gov.hk/en/setting-up-business/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides Hong Kong company setup and operating baseline for the SME scenario.",
    },
    {
        "id": "hkma_cdi_about",
        "raw_file": "11_hkma_cdi_about.html",
        "title": "About CDI - Commercial Data Interchange",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong"],
        "topic": ["Commercial Data Interchange", "SME finance", "digital banking"],
        "source_url": "https://cdi.hkma.gov.hk/about-cdi/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Explains CDI as consent-based data infrastructure for SME lending and bank digitalisation.",
    },
    {
        "id": "hkma_cdi_launch",
        "raw_file": "12_hkma_cdi_launch.html",
        "title": "HKMA announces the official launch of Commercial Data Interchange",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong"],
        "topic": ["Commercial Data Interchange", "SME finance", "open data"],
        "source_url": "https://www.hkma.gov.hk/eng/news-and-media/press-releases/2022/10/20221024-3/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports the CDI launch context for SME credit data sharing use cases.",
    },
    {
        "id": "hkma_cdi_digitalisation_circular",
        "raw_file": "13_hkma_cdi_digitalisation_circular.pdf",
        "title": "Leveraging Commercial Data Interchange for digitalisation of banking processes",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong"],
        "topic": ["Commercial Data Interchange", "SME lending", "bank digitalisation"],
        "source_url": "https://www.hkma.gov.hk/eng/key-information/guidelines-and-circular/2023/20230215e1/",
        "document_url": "https://www.hkma.gov.hk/media/eng/doc/key-information/guidelines-and-circular/2023/20230215e1.pdf",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Provides regulatory evidence that CDI can streamline SME onboarding, credit approval, and monitoring.",
    },
    {
        "id": "hkma_fps",
        "raw_file": "14_hkma_fps.html",
        "title": "Faster Payment System (FPS)",
        "issuer": "Hong Kong Monetary Authority",
        "authority_level": "regulator",
        "region": ["Hong Kong"],
        "topic": ["payment systems", "FPS", "retail payments"],
        "source_url": "https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/financial-market-infrastructure/faster-payment-system-fps/",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Explains Hong Kong's instant retail payment infrastructure for SME payment scenarios.",
    },
    {
        "id": "hkicl_hkd_chats",
        "raw_file": "15_hkicl_hkd_chats.html",
        "title": "HKD Clearing System in Hong Kong",
        "issuer": "Hong Kong Interbank Clearing Limited",
        "authority_level": "payment_infrastructure_operator",
        "region": ["Hong Kong"],
        "topic": ["CHATS", "RTGS", "HKD clearing"],
        "source_url": "https://www.hkicl.com.hk/eng/our_services/clearing_system_in_hong_kong/real_time_gross_settlement_system/hkd_clearing_system_in_hong_kong.php",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides operator-level detail for HKD CHATS and RTGS clearing used in bank payment explanations.",
    },
    {
        "id": "cips_introduction",
        "raw_file": "16_cips_introduction.html",
        "title": "Introduction to CIPS",
        "issuer": "Cross-border Interbank Payment System",
        "authority_level": "payment_infrastructure_operator",
        "region": ["Mainland China", "cross-border"],
        "topic": ["CIPS", "RMB clearing", "cross-border payment"],
        "source_url": "https://www.cips.com.cn/en/about_us/about_cips/introduction/index.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports RMB cross-border payment route explanations involving Mainland China.",
    },
    {
        "id": "safe_current_account_fx_guideline_2020",
        "raw_file": "17_safe_current_account_fx_guideline_2020.pdf",
        "title": "经常项目外汇业务指引（2020年版）",
        "issuer": "State Administration of Foreign Exchange",
        "authority_level": "regulator",
        "region": ["Mainland China", "cross-border"],
        "topic": ["current account", "foreign exchange", "trade payment"],
        "source_url": "https://www.safe.gov.cn/",
        "source_type": "PDF",
        "language": "zh-CN",
        "demo_relevance": "Provides detailed Mainland China current-account FX rules for trade payment compliance checks.",
    },
    {
        "id": "safe_capital_account_fx_guideline_2024",
        "raw_file": "18_safe_capital_account_fx_guideline_2024.pdf",
        "title": "资本项目外汇业务指引（2024年版）",
        "issuer": "State Administration of Foreign Exchange",
        "authority_level": "regulator",
        "region": ["Mainland China", "cross-border"],
        "topic": ["capital account", "foreign exchange", "cross-border investment"],
        "source_url": "https://www.safe.gov.cn/",
        "source_type": "PDF",
        "language": "zh-CN",
        "demo_relevance": "Supports Mainland China capital-account FX context for market-entry and investment scenarios.",
    },
    {
        "id": "safe_trade_fx_optimization_2024",
        "raw_file": "19_safe_trade_fx_optimization_2024.html",
        "title": "国家外汇管理局关于进一步优化贸易外汇业务管理的通知",
        "issuer": "State Administration of Foreign Exchange",
        "authority_level": "regulator",
        "region": ["Mainland China", "cross-border"],
        "topic": ["trade foreign exchange", "cross-border trade", "regulatory facilitation"],
        "source_url": "https://www.safe.gov.cn/safe/2024/0407/24229.html",
        "source_type": "HTML",
        "language": "zh-CN",
        "demo_relevance": "Supports Mainland China trade FX optimisation and facilitation context for cross-border trade payments.",
    },
    {
        "id": "sbv_export_payment_risk",
        "raw_file": "20_sbv_export_payment_risk.html",
        "title": "Cross-border payments: an inevitable trend in the context of international integration and digital transformation",
        "issuer": "State Bank of Vietnam",
        "authority_level": "central_bank",
        "region": ["Vietnam", "cross-border"],
        "topic": ["cross-border payment", "digital transformation", "payment risk"],
        "source_url": "https://www.sbv.gov.vn/en/web/sbv_portal/w/cross-border-payments-an-inevitable-trend-in-the-context-of-international-integration-and-digital-transformation-1-1",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Adds Vietnam central-bank context for cross-border payment trends and risks.",
    },
    {
        "id": "bochk_sme_loan",
        "raw_file": "21_bochk_sme_loan.html",
        "title": "BOC Small Business Loan Unsecured Loan",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong"],
        "topic": ["SME loan", "working capital", "business banking"],
        "source_url": "https://www.bochk.com/en/smeinone/loan/small_business_loan.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports bank product recommendations for SME working-capital needs.",
    },
    {
        "id": "bochk_sfgs_product",
        "raw_file": "22_bochk_sfgs_product.html",
        "title": "SME Financing Guarantee Scheme",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong"],
        "topic": ["SME loan", "financing guarantee", "SFGS"],
        "source_url": "https://www.bochk.com/en/smeinone/loan/sme_financing_guarantee_scheme.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Connects official guarantee-scheme context to BOCHK's SME lending product surface.",
    },
    {
        "id": "bochk_business_integrated_account",
        "raw_file": "23_bochk_business_integrated_account.pdf",
        "title": "Business Integrated Account",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong"],
        "topic": ["business account", "SME banking", "account services"],
        "source_url": "https://www.bochk.com/en/smeinone/account/business_integrated_account.html",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Provides BOCHK business account evidence for SME onboarding and account-management workflows.",
    },
    {
        "id": "bochk_remote_account_opening",
        "raw_file": "24_bochk_remote_account_opening.html",
        "title": "Account Opening Request (HK and Overseas Companies)",
        "issuer": "Bank of China (Hong Kong)",
        "authority_level": "bank_product_page",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["account opening", "KYB", "business banking"],
        "source_url": "https://www.bochk.com/en/smeinone/account/account_opening_request.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports business account opening paths for Hong Kong and overseas companies.",
    },
    {
        "id": "hkmc_sfgs_overview",
        "raw_file": "25_hkmc_sfgs_overview.html",
        "title": "SME Financing Guarantee Scheme",
        "issuer": "HKMC Insurance Limited",
        "authority_level": "government-backed_scheme_operator",
        "region": ["Hong Kong"],
        "topic": ["SME loan", "financing guarantee", "SFGS"],
        "source_url": "https://www.hkmc.com.hk/eng/our_business/sme_financing_guarantee_scheme.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides scheme-level official context for guarantee-backed SME financing.",
    },
    {
        "id": "hkmc_sfgs_statistics",
        "raw_file": "26_hkmc_sfgs_statistics.html",
        "title": "SME Financing Guarantee Scheme Statistics",
        "issuer": "HKMC Insurance Limited",
        "authority_level": "government-backed_scheme_operator",
        "region": ["Hong Kong"],
        "topic": ["SME loan", "financing guarantee", "statistics"],
        "source_url": "https://www.hkmc.com.hk/eng/information_centre/statistics/sme_financing_guarantee_scheme_statistics.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Adds quantitative context for SFGS uptake and scheme scale.",
    },
    {
        "id": "tid_bud_fund",
        "raw_file": "27_tid_bud_fund.html",
        "title": "Dedicated Fund on Branding, Upgrading and Domestic Sales (BUD Fund)",
        "issuer": "Trade and Industry Department / Hong Kong Productivity Council",
        "authority_level": "government_funding_scheme",
        "region": ["Hong Kong", "Mainland China", "ASEAN", "cross-border"],
        "topic": ["government funding", "market expansion", "SME support"],
        "source_url": "https://www.bud.hkpc.org/en",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports SME market-expansion funding recommendations alongside bank financing paths.",
    },
    {
        "id": "cr_incorporation_local_limited_company",
        "raw_file": "28_cr_incorporation_local_limited_company.html",
        "title": "How to register a new company?",
        "issuer": "Companies Registry",
        "authority_level": "government_registry",
        "region": ["Hong Kong"],
        "topic": ["company incorporation", "business registration", "market entry"],
        "source_url": "https://www.cr.gov.hk/en/services/register-company.htm",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides official Hong Kong company-incorporation steps for market-entry workflows.",
    },
    {
        "id": "cr_local_company_incorporation_faq",
        "raw_file": "29_cr_local_company_incorporation_faq.html",
        "title": "FAQ - Local Limited Companies - Incorporation",
        "issuer": "Companies Registry",
        "authority_level": "government_registry",
        "region": ["Hong Kong"],
        "topic": ["company incorporation", "FAQ", "market entry"],
        "source_url": "https://www.cr.gov.hk/en/faq/local-company/incorporation.htm",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Adds practical Companies Registry FAQ evidence for Hong Kong setup questions.",
    },
    {
        "id": "ird_business_registration",
        "raw_file": "30_ird_business_registration.html",
        "title": "Business Registration",
        "issuer": "Inland Revenue Department",
        "authority_level": "tax_authority",
        "region": ["Hong Kong"],
        "topic": ["business registration", "tax", "market entry"],
        "source_url": "https://www.ird.gov.hk/eng/tax/bre.htm",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides official Hong Kong business-registration requirements for SME setup workflows.",
    },
    {
        "id": "ird_profits_tax",
        "raw_file": "31_ird_profits_tax.html",
        "title": "Profits Tax",
        "issuer": "Inland Revenue Department",
        "authority_level": "tax_authority",
        "region": ["Hong Kong"],
        "topic": ["profits tax", "corporate tax", "business taxation"],
        "source_url": "https://www.ird.gov.hk/eng/tax/bus_pft.htm",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports Hong Kong profits-tax explanations for SME financial planning.",
    },
    {
        "id": "ird_territorial_source_principle",
        "raw_file": "32_ird_territorial_source_principle.html",
        "title": "A Simple Guide on The Territorial Source Principle of Taxation",
        "issuer": "Inland Revenue Department",
        "authority_level": "tax_authority",
        "region": ["Hong Kong", "cross-border"],
        "topic": ["territorial source principle", "profits tax", "cross-border taxation"],
        "source_url": "https://www.ird.gov.hk/eng/paf/bus_pft_tsp.htm",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Supports cross-border tax caveats around Hong Kong-sourced profits.",
    },
    {
        "id": "gogba_bank_accounts",
        "raw_file": "33_gogba_bank_accounts.html",
        "title": "Setting up a business in the Greater Bay Area (II) - Opening a company bank account",
        "issuer": "HKTDC GoGBA",
        "authority_level": "government_trade_promotion_platform",
        "region": ["Greater Bay Area", "Mainland China", "Shenzhen"],
        "topic": ["bank account opening", "market entry", "GBA expansion"],
        "source_url": "https://www.go-gba.com/en/gotoguides/bank-accounts.html",
        "source_type": "HTML",
        "language": "en",
        "demo_relevance": "Provides GBA bank-account setup context for Hong Kong SMEs entering Mainland China.",
    },
    {
        "id": "gogba_enterprise_income_tax_vat",
        "raw_file": "34_gogba_enterprise_income_tax_vat.pdf",
        "title": "GoGBA Guide: Enterprise Income Tax",
        "issuer": "HKTDC GoGBA",
        "authority_level": "government_trade_promotion_platform",
        "region": ["Greater Bay Area", "Mainland China"],
        "topic": ["enterprise income tax", "VAT", "GBA expansion"],
        "source_url": "https://www.go-gba.com/doc/gotoguide/enterprise_income_tax_en.pdf",
        "document_url": "https://www.go-gba.com/doc/gotoguide/enterprise_income_tax_en.pdf",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Adds GBA tax baseline for Mainland China expansion planning.",
    },
    {
        "id": "gogba_qianhai_policy",
        "raw_file": "35_gogba_qianhai_policy.pdf",
        "title": "GoGBA Go-to Guide: Preferential Policies in the Greater Bay Area - Qianhai",
        "issuer": "HKTDC GoGBA",
        "authority_level": "government_trade_promotion_platform",
        "region": ["Greater Bay Area", "Mainland China", "Shenzhen", "Qianhai"],
        "topic": ["Qianhai", "preferential policy", "GBA expansion"],
        "source_url": "https://www.go-gba.com/en/gotoguides/qianhai.html",
        "source_type": "PDF",
        "language": "en",
        "demo_relevance": "Supports Qianhai-specific incentives and policy guidance for Shenzhen expansion.",
    },
]


class VisibleTextParser(HTMLParser):
    BLOCK_TAGS = {
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

    SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href and href.startswith(("http://", "https://")):
                self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if not self.skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            text = data.strip()
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return " ".join(self.parts)


def clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = []
    previous = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if lines and lines[-1]:
                lines.append("")
            continue
        if line == previous:
            continue
        previous = line
        lines.append(line)
    return "\n".join(lines).strip()


def html_to_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"<(script|style|noscript|svg|canvas)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<(head)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    parser = VisibleTextParser()
    parser.feed(raw)
    return clean_text(parser.text())


def pdf_to_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = clean_text(page.extract_text() or "")
        if page_text:
            pages.append(f"## Page {index}\n\n{page_text}")
    return "\n\n".join(pages).strip()


def yaml_scalar(value) -> str:
    if isinstance(value, list):
        return "\n".join(f"  - {json.dumps(item, ensure_ascii=False)}" for item in value)
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def write_markdown(source: dict) -> dict:
    raw_path = RAW_DIR / source["raw_file"]
    meta = dict(source)
    meta["collected_at"] = COLLECTED_AT
    meta["raw_file_path"] = str(raw_path.relative_to(ROOT))

    try:
        if source["source_type"] == "PDF":
            body = pdf_to_text(raw_path)
        else:
            body = html_to_text(raw_path)
        meta["extraction_status"] = "ok" if body else "empty"
    except Exception as exc:  # Keep the source represented even when extraction fails.
        body = ""
        meta["extraction_status"] = f"failed: {exc.__class__.__name__}: {exc}"

    if not body:
        body = (
            "Text extraction did not produce readable body content. "
            "Use the source_url or document_url in the metadata to re-fetch the document."
        )

    md_path = OUT_DIR / f"{source['id']}.md"
    frontmatter = ["---"]
    for key in [
        "id",
        "title",
        "issuer",
        "authority_level",
        "region",
        "topic",
        "source_url",
        "document_url",
        "source_type",
        "language",
        "demo_relevance",
        "collected_at",
        "raw_file_path",
        "extraction_status",
    ]:
        if key in meta:
            rendered = yaml_scalar(meta[key])
            if isinstance(meta[key], list) or "\n" in rendered:
                frontmatter.append(f"{key}:")
                frontmatter.append(rendered)
            else:
                frontmatter.append(f"{key}: {rendered}")
    frontmatter.append("---")
    md_path.write_text("\n".join(frontmatter) + f"\n\n# {source['title']}\n\n{body}\n", encoding="utf-8")

    index_record = dict(meta)
    index_record["markdown_file"] = str(md_path.relative_to(ROOT))
    index_record["body_chars"] = len(body)
    return index_record


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = OUT_DIR / "metadata_index.json"
    existing_index = []
    if index_path.exists():
        existing_index = json.loads(index_path.read_text(encoding="utf-8"))
    existing_by_id = {record["id"]: record for record in existing_index}

    index = []
    kept = 0
    added = 0
    source_ids = set()
    for source in SOURCES:
        source_ids.add(source["id"])
        if source["id"] in existing_by_id:
            index.append(existing_by_id[source["id"]])
            kept += 1
            continue
        index.append(write_markdown(source))
        added += 1

    # Preserve any hand-added records that are not represented in SOURCES yet.
    for record in existing_index:
        if record["id"] not in source_ids:
            index.append(record)
            kept += 1

    index_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[convert] kept {kept} existing records; added {added} new records -> {index_path}")


if __name__ == "__main__":
    main()

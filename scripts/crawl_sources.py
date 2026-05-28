from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CANDIDATES_PATH = DATA_DIR / "crawl_candidates.jsonl"
ERROR_LOG_PATH = DATA_DIR / "crawl_errors.jsonl"
METADATA_PATH = DATA_DIR / "metadata_index.json"
CHUNKS_PATH = PROCESSED_DIR / "chunks.jsonl"
USER_AGENT = os.environ.get("CB_CRAWLER_USER_AGENT", "CrossBridge-RAG-Crawler/1.0")
REQUEST_TIMEOUT = float(os.environ.get("CB_CRAWLER_TIMEOUT", "30"))
DEFAULT_DOMAIN_DELAY = float(os.environ.get("CB_CRAWLER_DOMAIN_DELAY", "1.0"))
SENSITIVE_DOMAIN_DELAY = float(os.environ.get("CB_CRAWLER_SENSITIVE_DELAY", "4.0"))
MAX_BYTES = int(os.environ.get("CB_CRAWLER_MAX_BYTES", str(30 * 1024 * 1024)))


SENSITIVE_DOMAIN_MARKERS = (
    "hkma.gov.hk",
    "mas.gov.sg",
    "bnm.gov.my",
    "bot.or.th",
    "sbv.gov.vn",
    "bsp.gov.ph",
    "safe.gov.cn",
    "pbc.gov.cn",
    "cbirc.gov.cn",
    "nfra.gov.cn",
)


@dataclass
class SourceSeed:
    id: str
    url: str
    title: str
    issuer: str
    authority_level: str
    region: list[str]
    topic: list[str]
    source_type: str = "HTML"
    language: str = "en"
    trust_tier: str = "trusted"
    country: str = ""
    subdivision: str = ""
    agency: str = ""
    crawl_frequency: str = "weekly"
    reason: str = ""
    document_url: str = ""
    demo_relevance: str = ""
    publish_date: str = ""
    effective_date: str = ""
    content_anchor: str = ""
    allow_short_body: bool = False
    extra_urls: list[str] = field(default_factory=list)


BOC_CORE_SEEDS: list[SourceSeed] = [
    SourceSeed(
        id="bochk_sme_loan",
        url="https://www.bochk.com/en/loan/loan/unsecured.html",
        title="BOC Small Business Loan Unsecured Loan",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong"],
        topic=["SME loan", "working capital", "business banking"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK current SME unsecured loan product page.",
        demo_relevance="Supports bank product recommendations for SME working-capital needs.",
    ),
    SourceSeed(
        id="bochk_sfgs_product",
        url="https://www.bochk.com/dam/smeinone/loan/en.html",
        title="SME Financing Guarantee Scheme",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "SFGS"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK current corporate loans page covering SME loan and SFGS.",
        demo_relevance="Connects official guarantee-scheme context to BOCHK's SME lending product surface.",
    ),
    SourceSeed(
        id="bochk_trade_finance",
        url="https://www.bochk.com/en/corporate/tradefinance/overview.html",
        title="BOCHK Trade Finance Overview",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong", "cross-border"],
        topic=["trade finance", "SME banking", "import export"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK official trade finance page.",
        demo_relevance="Supports bank product recommendations for import/export and supplier payment needs.",
    ),
    SourceSeed(
        id="bochk_remote_account_opening",
        url="https://www.bochk.com/en/smeinone/acopen/acopen.html",
        title="Account Opening Request (HK and Overseas Companies)",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong", "cross-border"],
        topic=["account opening", "KYB", "business banking"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK current official business account opening page.",
        demo_relevance="Supports business account opening paths for Hong Kong and overseas companies.",
    ),
    SourceSeed(
        id="bochk_business_integrated_account",
        url="https://www.bochk.com/en/smeinone/acopen/business.html",
        title="Business Integrated Account",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong"],
        topic=["business account", "SME banking", "account services"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK current business integrated account product page.",
        demo_relevance="Provides BOCHK business account evidence for SME onboarding and account-management workflows.",
    ),
    SourceSeed(
        id="hkmc_sfgs_overview",
        url="https://www.hkmc.com.hk/eng/our_business/sme_financing_guarantee_scheme.html",
        title="SME Financing Guarantee Scheme",
        issuer="HKMC Insurance Limited",
        authority_level="government-backed_scheme_operator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "SFGS"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMC",
        crawl_frequency="monthly",
        reason="Official SFGS scheme overview.",
        demo_relevance="Provides scheme-level official context for guarantee-backed SME financing.",
    ),
    SourceSeed(
        id="hkmc_sfgs_statistics",
        url="https://www.hkmc.com.hk/eng/information_centre/statistics/sme_financing_guarantee_scheme_statistics.html",
        title="SME Financing Guarantee Scheme Statistics",
        issuer="HKMC Insurance Limited",
        authority_level="government-backed_scheme_operator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "statistics"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMC",
        crawl_frequency="monthly",
        reason="Official SFGS statistics page.",
        demo_relevance="Adds quantitative context for SFGS uptake and scheme scale.",
    ),
    SourceSeed(
        id="hkma_cdi_about",
        url="https://cdi.hkma.gov.hk/about-cdi/",
        title="About CDI - Commercial Data Interchange",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["Commercial Data Interchange", "SME finance", "digital banking"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        reason="HKMA CDI official page relevant to SME lending efficiency.",
        demo_relevance="Explains CDI as consent-based data infrastructure for SME lending and bank digitalisation.",
    ),
    SourceSeed(
        id="hkma_cdi_launch",
        url="https://www.hkma.gov.hk/eng/news-and-media/press-releases/2022/10/20221024-3/",
        title="HKMA announces the official launch of Commercial Data Interchange",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["Commercial Data Interchange", "SME finance", "open data"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        reason="HKMA CDI launch press release.",
        demo_relevance="Supports the CDI launch context for SME credit data sharing use cases.",
    ),
    SourceSeed(
        id="hkma_cdi_digitalisation_circular",
        url="https://www.hkma.gov.hk/eng/key-information/guidelines-and-circular/2023/20230215e1/",
        document_url="https://www.hkma.gov.hk/media/eng/doc/key-information/guidelines-and-circular/2023/20230215e1.pdf",
        title="Leveraging Commercial Data Interchange for digitalisation of banking processes",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["Commercial Data Interchange", "SME lending", "bank digitalisation"],
        source_type="PDF",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        reason="HKMA circular PDF on CDI and SME banking process digitalisation.",
        demo_relevance="Provides regulatory evidence that CDI can streamline SME onboarding, credit approval, and monitoring.",
    ),
    SourceSeed(
        id="investhk_setting_up_business",
        url="https://www.investhk.gov.hk/en/setting-up-business/",
        title="Setting Up Business in Hong Kong",
        issuer="Invest Hong Kong",
        authority_level="government_investment_promotion_body",
        region=["Hong Kong"],
        topic=["company setup", "business registration", "tax", "market entry"],
        country="HK",
        subdivision="hk_sar",
        agency="InvestHK",
        crawl_frequency="monthly",
        reason="Official Hong Kong market-entry guide.",
        demo_relevance="Provides Hong Kong company setup and operating baseline for the SME scenario.",
    ),
    SourceSeed(
        id="tid_bud_fund",
        url="https://www.bud.hkpc.org/en",
        title="Dedicated Fund on Branding, Upgrading and Domestic Sales (BUD Fund)",
        issuer="Trade and Industry Department / Hong Kong Productivity Council",
        authority_level="government_funding_scheme",
        region=["Hong Kong", "Mainland China", "ASEAN", "cross-border"],
        topic=["government funding", "market expansion", "SME support"],
        country="HK",
        subdivision="hk_sar",
        agency="TID/HKPC",
        crawl_frequency="monthly",
        reason="Official Hong Kong SME market expansion funding scheme.",
        demo_relevance="Supports SME market-expansion funding recommendations alongside bank financing paths.",
    ),
    SourceSeed(
        id="mas_sme_financing",
        url="https://www.enterprisesg.gov.sg/financial-support",
        title="Enterprise Singapore Financial Support",
        issuer="Enterprise Singapore",
        authority_level="government_agency",
        region=["Singapore", "ASEAN"],
        topic=["SME finance", "government funding", "market expansion"],
        country="SG",
        agency="EnterpriseSG",
        reason="Singapore official enterprise financing support entry point.",
        demo_relevance="Supports Singapore SME financing official support queries.",
    ),
    SourceSeed(
        id="smecorp_financing_schemes",
        url="https://smecorp.gov.my/images/Publication/handbook/Financing_Schemes.pdf",
        title="Financing Schemes for SMEs in Malaysia",
        issuer="SME Corporation Malaysia",
        authority_level="government_agency",
        region=["Malaysia", "ASEAN"],
        topic=["SME finance", "government funding", "financing"],
        source_type="PDF",
        country="MY",
        agency="SME Corp Malaysia",
        crawl_frequency="monthly",
        reason="Malaysia official SME agency financing schemes handbook.",
        demo_relevance="Supports Malaysia SME financing policy queries.",
    ),
    SourceSeed(
        id="bot_sme_finance",
        url="https://www.bot.or.th/en/financial-innovation/sustainable-finance/household-and-sme/SME-financial-inclusion.html",
        title="SME Finance",
        issuer="Bank of Thailand",
        authority_level="central_bank",
        region=["Thailand", "ASEAN"],
        topic=["SME finance", "business loan", "central bank"],
        country="TH",
        agency="BOT",
        reason="Thailand central-bank SME finance official page.",
        demo_relevance="Supports Thailand SME financing policy queries.",
        content_anchor="Household and SME Financial Inclusion",
    ),
    SourceSeed(
        id="sbv_credit_institutions",
        url="https://www.sbv.gov.vn/en/web/sbv_portal/home",
        title="State Bank of Vietnam",
        issuer="State Bank of Vietnam",
        authority_level="central_bank",
        region=["Vietnam", "ASEAN"],
        topic=["central bank", "SME finance", "cross-border payment"],
        country="VN",
        agency="SBV",
        reason="Vietnam central-bank official entry point for financial policy discovery.",
        demo_relevance="Supports Vietnam official financial policy context.",
    ),
    SourceSeed(
        id="bsp_financial_inclusion",
        url="https://www.bsp.gov.ph/SitePages/InclusiveFinance/InclusiveFinance.aspx",
        title="Inclusive Finance",
        issuer="Bangko Sentral ng Pilipinas",
        authority_level="central_bank",
        region=["Philippines", "ASEAN"],
        topic=["financial inclusion", "SME finance", "central bank"],
        country="PH",
        agency="BSP",
        reason="Philippines central-bank inclusive finance official page.",
        demo_relevance="Supports Philippines SME finance and financial inclusion policy queries.",
    ),
]


BOC_EXPAND_SEEDS: list[SourceSeed] = [
    SourceSeed(
        id="bochk_loan_services",
        url="https://www.bochk.com/en/smeinone/loan.html",
        title="Loan Services",
        issuer="Bank of China (Hong Kong)",
        authority_level="bank_product_page",
        region=["Hong Kong"],
        topic=["SME loan", "trade finance", "business banking"],
        country="HK",
        subdivision="hk_sar",
        agency="BOCHK",
        reason="BOCHK SME in One loan services landing page.",
        demo_relevance="Broad BOCHK SME lending product navigation for loan-readiness answers.",
    ),
    SourceSeed(
        id="boc_singapore_corporate_banking",
        url="https://www.bankofchina.com/sg/cbservice/",
        title="Corporate Banking",
        issuer="Bank of China Singapore Branch",
        authority_level="bank_product_page",
        region=["Singapore", "ASEAN", "cross-border"],
        topic=["corporate banking", "SME banking", "trade finance"],
        country="SG",
        agency="BOC Singapore",
        reason="BOC Singapore corporate banking landing page.",
        demo_relevance="Supports Singapore-side BOC corporate banking product context.",
    ),
    SourceSeed(
        id="boc_singapore_corporate_loans",
        url="https://www.bankofchina.com/sg/cbservice/cb2/",
        title="Corporate Loans",
        issuer="Bank of China Singapore Branch",
        authority_level="bank_product_page",
        region=["Singapore", "ASEAN"],
        topic=["corporate loan", "business loan", "SME finance"],
        country="SG",
        agency="BOC Singapore",
        reason="BOC Singapore corporate loans page.",
        demo_relevance="Supports Singapore corporate loan product questions.",
    ),
    SourceSeed(
        id="boc_singapore_trade_finance",
        url="https://www.bankofchina.com/sg/cbservice/cb3/",
        title="Trade Finance",
        issuer="Bank of China Singapore Branch",
        authority_level="bank_product_page",
        region=["Singapore", "ASEAN", "cross-border"],
        topic=["trade finance", "trade settlement", "bank guarantee"],
        country="SG",
        agency="BOC Singapore",
        reason="BOC Singapore trade finance page.",
        demo_relevance="Supports import/export trade finance explanations for Singapore.",
    ),
    SourceSeed(
        id="boc_singapore_invoice_financing",
        url="https://www.bankofchina.com/sg/cbservice/cb3/cb22/201001/t20100125_955792.html",
        title="Invoice Financing",
        issuer="Bank of China Singapore Branch",
        authority_level="bank_product_page",
        region=["Singapore", "ASEAN", "cross-border"],
        topic=["invoice financing", "trade finance", "SME finance"],
        country="SG",
        agency="BOC Singapore",
        reason="BOC Singapore invoice financing product page.",
        demo_relevance="Supports SME invoice financing product recommendations.",
    ),
    SourceSeed(
        id="boc_singapore_rmb_corporate_banking",
        url="https://www.bankofchina.com/sg/cbservice/RMB/201411/t20141125_4199116.html",
        title="Corporate Banking RMB Services",
        issuer="Bank of China Singapore Branch",
        authority_level="bank_product_page",
        region=["Singapore", "ASEAN", "cross-border"],
        topic=["RMB services", "corporate banking", "cross-border payment"],
        country="SG",
        agency="BOC Singapore",
        reason="BOC Singapore corporate RMB services page.",
        demo_relevance="Supports RMB account and cross-border payment questions in Singapore.",
    ),
    SourceSeed(
        id="boc_thailand_corporate_saving",
        url="https://www.bankofchina.com/th/en/cbservice/cb1/201109/t20110908_1589815.html",
        title="Corporate Saving Deposit Account",
        issuer="Bank of China (Thai) Public Company Limited",
        authority_level="bank_product_page",
        region=["Thailand", "ASEAN"],
        topic=["business account", "corporate banking", "remittance"],
        country="TH",
        agency="BOC Thailand",
        reason="BOC Thailand corporate account opening page.",
        demo_relevance="Supports Thailand business account opening and remittance context.",
    ),
    SourceSeed(
        id="boc_thailand_advising_lc",
        url="https://www.bankofchina.com/th/en/cbservice/cb2/cb21/201109/t20110909_1589822.html",
        title="Advising of L/C",
        issuer="Bank of China (Thai) Public Company Limited",
        authority_level="bank_product_page",
        region=["Thailand", "ASEAN", "cross-border"],
        topic=["letter of credit", "trade settlement", "trade finance"],
        country="TH",
        agency="BOC Thailand",
        reason="BOC Thailand L/C advising trade settlement page.",
        demo_relevance="Supports import/export L/C workflow questions for Thailand.",
    ),
    SourceSeed(
        id="boc_thailand_performance_guarantee",
        url="https://www.bankofchina.com/th/en/cbservice/cb2/cb23/201109/t20110909_1589834.html",
        title="Performance Guarantee",
        issuer="Bank of China (Thai) Public Company Limited",
        authority_level="bank_product_page",
        region=["Thailand", "ASEAN", "cross-border"],
        topic=["bank guarantee", "trade finance", "contract performance"],
        country="TH",
        agency="BOC Thailand",
        reason="BOC Thailand performance guarantee page.",
        demo_relevance="Supports guarantee product explanations for trade and project contracts.",
    ),
    SourceSeed(
        id="boc_thailand_overview",
        url="https://www.bankofchina.com/th/en/aboutus/ab1/201110/t20111010_1589901.html",
        title="Introduction",
        issuer="Bank of China (Thai) Public Company Limited",
        authority_level="bank_official_page",
        region=["Thailand", "ASEAN"],
        topic=["corporate banking", "BOC network", "market entry"],
        country="TH",
        agency="BOC Thailand",
        reason="BOC Thailand official overview page.",
        demo_relevance="Provides BOC Thailand institutional context.",
    ),
    SourceSeed(
        id="boc_global_trade_finance_international_orgs",
        url="https://www.bankofchina.com/en/cbservice/cb3/cb35/200905/t20090520_1324114.html",
        title="Trade Finance Guaranteed by International Organizations",
        issuer="Bank of China",
        authority_level="bank_product_page",
        region=["Mainland China", "ASEAN", "cross-border"],
        topic=["trade finance", "international organization guarantee", "SME finance"],
        country="CN",
        agency="BOC",
        reason="BOC global trade finance page for emerging-market guarantee-backed products.",
        demo_relevance="Supports trade finance recommendations involving emerging markets.",
    ),
    SourceSeed(
        id="boc_global_domestic_lc",
        url="https://www.bankofchina.com/en/cbservice/cb3/cb34/200807/t20080701_1324130.html",
        title="Domestic L/C",
        issuer="Bank of China",
        authority_level="bank_product_page",
        region=["Mainland China", "cross-border"],
        topic=["letter of credit", "domestic trade financing", "trade settlement"],
        country="CN",
        agency="BOC",
        reason="BOC domestic L/C product page.",
        demo_relevance="Supports L/C and trade settlement explanations.",
    ),
    SourceSeed(
        id="boc_global_purchase_order_financing",
        url="https://www.bankofchina.com/en/cbservice/cb3/cb32/200908/t20090826_1324187.html",
        title="Purchase Order Financing",
        issuer="Bank of China",
        authority_level="bank_product_page",
        region=["Mainland China", "cross-border"],
        topic=["purchase order financing", "trade finance", "SME finance"],
        country="CN",
        agency="BOC",
        reason="BOC purchase order financing product page.",
        demo_relevance="Supports supplier financing and working-capital answers.",
    ),
    SourceSeed(
        id="hkma_sfgs_insight_2025",
        url="https://www.hkma.gov.hk/eng/news-and-media/insight/2025/12/20251223/",
        title="The SME Financing Guarantee Scheme",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "SFGS"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA inSight article on SFGS extension and repayment arrangements.",
        demo_relevance="Supports SFGS status and policy context.",
    ),
    SourceSeed(
        id="hkma_sfgs_extension_2024",
        url="https://www.hkma.gov.hk/eng/news-and-media/press-releases/2024/02/20240228-4/",
        title="SME Financing Guarantee Scheme extends application period",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "SFGS"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA/HKMC announcement on SFGS application period extension.",
        demo_relevance="Supports SFGS application-period answers.",
    ),
    SourceSeed(
        id="hkma_sfgs_90_product",
        url="https://www.hkma.gov.hk/eng/news-and-media/press-releases/2019/12/20191206-7/",
        title="SME Financing Guarantee Scheme - 90% Guarantee Product",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "90% Guarantee Product"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="Official announcement introducing SFGS 90% Guarantee Product.",
        demo_relevance="Supports comparison between SFGS guarantee products.",
    ),
    SourceSeed(
        id="hkma_sfgs_partial_principal_repayment",
        url="https://www.hkma.gov.hk/eng/news-and-media/press-releases/2023/10/20231025-4/",
        title="Partial principal repayment arrangement for SME Financing Guarantee Scheme",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "repayment arrangement"],
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="Official SFGS partial principal repayment arrangement announcement.",
        demo_relevance="Supports questions about repayment flexibility under SFGS.",
    ),
    SourceSeed(
        id="smelink_sfgs",
        url="https://www.smelink.gov.hk/en/web/sme-portal/w/sme-financing-guarantee-scheme.html",
        title="SME Financing Guarantee Scheme",
        issuer="SME Link / Hong Kong Government",
        authority_level="government_portal",
        region=["Hong Kong"],
        topic=["SME loan", "government funding", "financing guarantee"],
        country="HK",
        subdivision="hk_sar",
        agency="SME Link",
        crawl_frequency="monthly",
        reason="Hong Kong SME portal page for SFGS.",
        demo_relevance="Supports SME-facing government explanation of financing guarantee support.",
    ),
    SourceSeed(
        id="enterprisesg_efs",
        url="https://www.enterprisesg.gov.sg/financial-support/enterprise-financing-scheme",
        title="Enterprise Financing Scheme",
        issuer="Enterprise Singapore",
        authority_level="government_agency",
        region=["Singapore", "ASEAN"],
        topic=["SME finance", "working capital loan", "trade loan"],
        country="SG",
        agency="EnterpriseSG",
        reason="Singapore Enterprise Financing Scheme official page.",
        demo_relevance="Supports Singapore SME financing and eligibility answers.",
    ),
    SourceSeed(
        id="enterprisesg_efs_faq",
        url="https://www.enterprisesg.gov.sg/resources/all-faqs/enterprise-financing-scheme",
        title="FAQ: Enterprise Financing Scheme",
        issuer="Enterprise Singapore",
        authority_level="government_agency",
        region=["Singapore", "ASEAN"],
        topic=["SME finance", "FAQ", "government risk sharing"],
        country="SG",
        agency="EnterpriseSG",
        reason="Singapore Enterprise Financing Scheme FAQ.",
        demo_relevance="Supports practical EFS application and risk-share questions.",
    ),
    SourceSeed(
        id="enterprisesg_efs_fixed_assets",
        url="https://www.enterprisesg.gov.sg/financial-support/enterprise-financing-scheme---sme-fixed-assets",
        title="Enterprise Financing Scheme – SME Fixed Assets Loan",
        issuer="Enterprise Singapore",
        authority_level="government_agency",
        region=["Singapore", "ASEAN"],
        topic=["SME finance", "fixed asset loan", "overseas expansion"],
        country="SG",
        agency="EnterpriseSG",
        reason="Singapore EFS SME fixed assets loan page.",
        demo_relevance="Supports overseas expansion fixed-asset financing questions.",
    ),
    SourceSeed(
        id="hkma_cdi_research_2026",
        url="https://www.hkma.gov.hk/media/eng/publication-and-research/research/research-memorandums/2026/RM01.pdf",
        title="Assessing the Effects of Commercial Data Interchange on SME Lending",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator_research",
        region=["Hong Kong"],
        topic=["Commercial Data Interchange", "SME lending", "research"],
        source_type="PDF",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA research memorandum on CDI effects for SME lending.",
        demo_relevance="Supports evidence that CDI can improve SME lending outcomes.",
    ),
]


EVAL_GAP_FILL_SEEDS: list[SourceSeed] = [
    SourceSeed(
        id="sbv_cross_border_payments_vi",
        url="https://www.sbv.gov.vn/vi/web/sbv_portal/w/cross-border-payments-an-inevitable-trend-in-the-context-of-international-integration-and-digital-transformation-1-1",
        title="Cross-border payments: an inevitable trend in the context of international integration and digital transformation",
        issuer="State Bank of Vietnam",
        authority_level="central_bank",
        region=["Vietnam", "ASEAN", "cross-border"],
        topic=["cross-border payment", "foreign exchange regulation", "payment systems"],
        language="vi",
        trust_tier="central_bank",
        country="VN",
        agency="SBV",
        crawl_frequency="monthly",
        reason="SBV official cross-border payments and regulatory context.",
        demo_relevance="high",
    ),
    SourceSeed(
        id="sbv_circular_20_2022_current_account_transfers",
        url="https://www.sbv.gov.vn/vi/w/sbv557663",
        title="Circular No. 20/2022/TT-NHNN on one-way money transfer and payment for current transactions",
        issuer="State Bank of Vietnam",
        authority_level="central_bank",
        region=["Vietnam", "cross-border"],
        topic=["foreign exchange regulation", "current account transfer", "one-way transfer"],
        language="vi",
        trust_tier="central_bank",
        country="VN",
        agency="SBV",
        crawl_frequency="monthly",
        reason="SBV circular relevant to current-account and one-way cross-border transfers.",
        demo_relevance="high",
        publish_date="2022-12-30",
    ),
    SourceSeed(
        id="sbv_circular_15_2024_payment_services",
        url="https://www.sbv.gov.vn/en/web/sbv_portal/w/press-release-on-issuance-of-circular-no.-15/2024/tt-nhnn",
        title="Press release on issuance of Circular No. 15/2024/TT-NHNN",
        issuer="State Bank of Vietnam",
        authority_level="central_bank",
        region=["Vietnam"],
        topic=["payment systems", "payment services", "foreign exchange regulation"],
        language="en",
        trust_tier="central_bank",
        country="VN",
        agency="SBV",
        crawl_frequency="monthly",
        reason="SBV official press release on payment service circular.",
        demo_relevance="high",
        publish_date="2024-06-28",
    ),
    SourceSeed(
        id="sbv_payment_system_supervision_circular_20_2018",
        url="https://sbv.gov.vn/en/w/sbv353809-1",
        title="Circular No. 20/2018/TT-NHNN on oversight of payment systems",
        issuer="State Bank of Vietnam",
        authority_level="central_bank",
        region=["Vietnam"],
        topic=["payment systems", "payment infrastructure", "foreign exchange regulation"],
        language="en",
        trust_tier="central_bank",
        country="VN",
        agency="SBV",
        crawl_frequency="monthly",
        reason="SBV official circular on payment-system supervision.",
        demo_relevance="medium",
        publish_date="2018-08-30",
    ),
    SourceSeed(
        id="fia_vietnam_taxation_customs",
        url="https://fia.mof.gov.vn/en/Single/MenuID/793a43ff-0059-4504-b747-934193322015",
        title="Taxation and Customs",
        issuer="Foreign Investment Agency Vietnam",
        authority_level="government",
        region=["Vietnam"],
        topic=["foreign investment", "taxation", "customs"],
        language="en",
        trust_tier="government",
        country="VN",
        agency="FIA",
        crawl_frequency="monthly",
        reason="Vietnam official investment agency page for taxation and customs.",
        demo_relevance="high",
    ),
    SourceSeed(
        id="mpi_vietnam_foreign_direct_investment",
        url="https://www.mpi.gov.vn/en/pages/Foreign-Direct-Investment-289.aspx",
        title="Foreign Direct Investment",
        issuer="Ministry of Planning and Investment of Vietnam",
        authority_level="government",
        region=["Vietnam"],
        topic=["foreign investment", "manufacturing investment", "market entry"],
        language="en",
        trust_tier="government",
        country="VN",
        agency="MPI",
        crawl_frequency="monthly",
        reason="Vietnam MPI official FDI page.",
        demo_relevance="high",
    ),
    SourceSeed(
        id="mpi_vietnam_restricted_investment_fields",
        url="https://ipcs.mpi.gov.vn/linh-vuc-han-che-dau-tu/",
        title="Lĩnh vực hạn chế đầu tư",
        issuer="Ministry of Planning and Investment of Vietnam",
        authority_level="government",
        region=["Vietnam"],
        topic=["foreign investment", "restricted investment", "investment compliance"],
        language="vi",
        trust_tier="government",
        country="VN",
        agency="MPI",
        crawl_frequency="monthly",
        reason="Vietnam official restricted investment field list.",
        demo_relevance="high",
    ),
    SourceSeed(
        id="hkma_system_linkages",
        url="https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/financial-market-infrastructure/system-linkages/",
        title="System Linkages",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "cross-border"],
        topic=["payment systems", "system linkages", "RTGS"],
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA official page on cross-system payment infrastructure linkages.",
        demo_relevance="high",
    ),
    SourceSeed(
        id="hkicl_hkd_fps_rules_2025",
        url="https://www.hkicl.com.hk/files/page_file/126/10939/HKD%20FPS%20Rules_redacted%20version_Jun%202025_dist%20ver..pdf",
        title="HKD Faster Payment System Rules",
        issuer="Hong Kong Interbank Clearing Limited",
        authority_level="official_dev",
        region=["Hong Kong"],
        topic=["FPS", "FPS rulebook", "payment systems"],
        source_type="PDF",
        language="en",
        trust_tier="official_dev",
        country="HK",
        subdivision="hk_sar",
        agency="HKICL",
        crawl_frequency="monthly",
        reason="HKICL official HKD FPS rules PDF.",
        demo_relevance="high",
        publish_date="2025-06-01",
    ),
    SourceSeed(
        id="cips_indirect_participant_guide_2025",
        url="https://www.cips.com.cn/cips/2025-01/06/a76be85f8f9d462d8d18fdbb13a7d034/2025010617594998775.pdf",
        title="Guide for Indirect Participants of CIPS",
        issuer="Cross-border Interbank Payment System",
        authority_level="payment_infrastructure_operator",
        region=["Mainland China", "cross-border"],
        topic=["CIPS", "indirect participant", "cross-border payment"],
        source_type="PDF",
        language="en",
        trust_tier="official_dev",
        country="CN",
        agency="CIPS",
        crawl_frequency="monthly",
        reason="CIPS official guide for indirect participants and cross-border clearing access.",
        demo_relevance="high",
        publish_date="2025-01-06",
    ),
    SourceSeed(
        id="hkma_wmc_implementation_arrangements_2021",
        url="https://brdr.hkma.gov.hk/eng/doc-ldg/docId/20210910-4-EN",
        title="Implementation Arrangements for the Cross-boundary Wealth Management Connect Pilot Scheme",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "Greater Bay Area", "cross-border"],
        topic=["Cross-boundary WMC", "GBA expansion", "investment compliance"],
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA official BRDR entry for Cross-boundary WMC implementation arrangements.",
        demo_relevance="medium",
        publish_date="2021-09-10",
        effective_date="2021-09-10",
    ),
    SourceSeed(
        id="hkma_wmc_2024_circular",
        url="https://www.hkma.gov.hk/media/eng/doc/key-information/guidelines-and-circular/2024/20240124e2.pdf",
        title="Enhancements to Cross-boundary Wealth Management Connect Pilot Scheme",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "Greater Bay Area", "cross-border"],
        topic=["Cross-boundary WMC", "GBA expansion", "investment compliance"],
        source_type="PDF",
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA 2024 circular on Cross-boundary WMC enhancement arrangements.",
        demo_relevance="medium",
        publish_date="2024-01-24",
        effective_date="2024-02-26",
    ),
    SourceSeed(
        id="hkmc_sfgs_application_procedures_lender",
        url="https://www.hkmc.com.hk/files/product_file/6/617/SFGS%20Appln%20procedures%20for%20AI%20to%20become%20a%20PL%20v2%20%28clean%29.pdf",
        title="Application Procedures for an Authorized Institution to become a Participating Lender",
        issuer="HKMC Insurance Limited",
        authority_level="official_dev",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "eligibility"],
        source_type="PDF",
        language="en",
        trust_tier="official_dev",
        country="HK",
        subdivision="hk_sar",
        agency="HKMC",
        crawl_frequency="monthly",
        reason="HKMC official SFGS lender application procedures document.",
        demo_relevance="medium",
    ),
    SourceSeed(
        id="hktdc_vietnam_manufacturing_background",
        url="https://beltandroad.hktdc.com/en/sme-corner/manufacturing-partnership-and-investment",
        title="Manufacturing Partnership and Investment",
        issuer="Hong Kong Trade Development Council",
        authority_level="government_trade_promotion_body",
        region=["Vietnam", "ASEAN", "cross-border"],
        topic=["Vietnam market entry", "manufacturing investment", "foreign investment"],
        language="en",
        trust_tier="background",
        country="VN",
        agency="HKTDC",
        crawl_frequency="monthly",
        reason="Background-only Vietnam manufacturing investment context from HKTDC.",
        demo_relevance="low",
    ),
    SourceSeed(
        id="hkma_wmc_overview",
        url="https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/wealth-management-connect/",
        title="Cross-boundary Wealth Management Connect Scheme in the Guangdong-Hong Kong-Macao Greater Bay Area",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "Greater Bay Area", "cross-border"],
        topic=["Cross-boundary WMC", "GBA expansion", "investment compliance"],
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA official WMC overview page as a crawlable fallback for BRDR circulars.",
        demo_relevance="high",
        publish_date="2025-12-11",
        effective_date="2021-09-10",
    ),
    SourceSeed(
        id="hkma_wmc_northbound_banks",
        url="https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/wealth-management-connect/northbound-scheme/",
        title="The Northbound Scheme (Applicable to banks)",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "Greater Bay Area", "cross-border"],
        topic=["Cross-boundary WMC", "GBA expansion", "investment compliance"],
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA official WMC Northbound banking page.",
        demo_relevance="medium",
    ),
    SourceSeed(
        id="hkma_wmc_southbound_banks",
        url="https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/wealth-management-connect/southbound-scheme/",
        title="The Southbound Scheme (Applicable to banks)",
        issuer="Hong Kong Monetary Authority",
        authority_level="regulator",
        region=["Hong Kong", "Greater Bay Area", "cross-border"],
        topic=["Cross-boundary WMC", "GBA expansion", "investment compliance"],
        language="en",
        trust_tier="regulator",
        country="HK",
        subdivision="hk_sar",
        agency="HKMA",
        crawl_frequency="monthly",
        reason="HKMA official WMC Southbound banking page.",
        demo_relevance="medium",
    ),
    SourceSeed(
        id="hkicl_hkd_clearing_house_rules_2026",
        url="https://www.hkicl.com.hk/files/page_file/120/12213/HKD%20Clearing%20House%20Rules%20%28April%202026%29_redacted_clean.pdf",
        title="Hong Kong Dollar Clearing House Rules",
        issuer="Hong Kong Interbank Clearing Limited",
        authority_level="official_dev",
        region=["Hong Kong"],
        topic=["CHATS", "RTGS", "payment systems"],
        source_type="PDF",
        language="en",
        trust_tier="official_dev",
        country="HK",
        subdivision="hk_sar",
        agency="HKICL",
        crawl_frequency="monthly",
        reason="HKICL official HKD clearing house rules for CHATS/RTGS detail.",
        demo_relevance="high",
        publish_date="2026-04-01",
    ),
    SourceSeed(
        id="hkmc_sfgs_application_procedures",
        url="https://www.hkmc.com.hk/files/product_file/6/1051/SFGS%20Application%20Procedures%20202004_Eng.pdf",
        title="SME Financing Guarantee Scheme Application Procedures",
        issuer="HKMC Insurance Limited",
        authority_level="official_dev",
        region=["Hong Kong"],
        topic=["SME loan", "financing guarantee", "eligibility"],
        source_type="PDF",
        language="en",
        trust_tier="official_dev",
        country="HK",
        subdivision="hk_sar",
        agency="HKMC",
        crawl_frequency="monthly",
        reason="HKMC official SFGS application procedures PDF.",
        demo_relevance="high",
        publish_date="2020-04-01",
    ),
]


class VisibleTextParser(HTMLParser):
    BLOCK_TAGS = {
        "address", "article", "aside", "br", "dd", "div", "dl", "dt", "figcaption",
        "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr",
        "li", "main", "nav", "ol", "p", "section", "table", "td", "th", "tr", "ul",
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
            if href:
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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines: list[str] = []
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


def html_bytes_to_text(content: bytes) -> str:
    raw = content.decode("utf-8", errors="ignore")
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"<(script|style|noscript|svg|canvas)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<(head)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    parser = VisibleTextParser()
    parser.feed(raw)
    return clean_text(parser.text())


def trim_body_to_title(body: str, title: str) -> str:
    if not body or not title:
        return body
    pattern = re.compile(re.escape(title), re.IGNORECASE)
    matches = list(pattern.finditer(body))
    if not matches:
        return body
    # The fallback parser can include large site navigation before page content.
    # Prefer a later title occurrence when one exists near the first half of the page.
    min_remaining = min(500, max(100, len(body) // 10))
    viable = [
        m for m in matches
        if m.start() <= max(3000, len(body) // 2)
        and len(body) - m.start() >= min_remaining
    ]
    if not viable:
        return body
    later = [m for m in viable if m.start() > 1000]
    match = later[-1] if later else viable[0]
    if match.start() <= max(3000, len(body) // 2):
        return body[match.start():].strip()
    return body


def trim_body_to_anchor(body: str, anchor: str) -> str:
    if not body or not anchor:
        return body
    match = re.search(re.escape(anchor), body, re.IGNORECASE)
    if not match:
        return body
    remaining = body[match.start():].strip()
    if len(remaining) < min(500, max(100, len(body) // 10)):
        return body
    return remaining


def pdf_bytes_to_text(content: bytes, raw_path: Path) -> tuple[str, str]:
    raw_path.write_bytes(content)
    try:
        reader = PdfReader(str(raw_path))
        pages: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = clean_text(page.extract_text() or "")
            if page_text:
                pages.append(f"## Page {index}\n\n{page_text}")
        body = "\n\n".join(pages).strip()
    except Exception as exc:
        return "", f"failed: {exc.__class__.__name__}: {exc}"

    if body:
        return body, "ok"

    ocr_text = try_aliyun_ocr(raw_path)
    if ocr_text:
        return ocr_text, "ok_ocr"
    return "", "ocr_required_or_failed"


def try_aliyun_ocr(raw_path: Path) -> str:
    """OCR hook. Configure ALIYUN_OCR_COMMAND to run a local wrapper if needed."""
    command = os.environ.get("ALIYUN_OCR_COMMAND")
    if not command:
        return ""
    try:
        completed = subprocess.run(
            [command, str(raw_path)],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
            timeout=float(os.environ.get("ALIYUN_OCR_TIMEOUT", "120")),
        )
    except Exception:
        return ""
    if completed.returncode != 0:
        return ""
    return clean_text(completed.stdout)


def yaml_scalar(value) -> str:
    if isinstance(value, list):
        return "\n".join(f"  - {json.dumps(item, ensure_ascii=False)}" for item in value)
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def load_metadata() -> list[dict]:
    if not METADATA_PATH.exists():
        return []
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def write_metadata(records: list[dict]) -> None:
    METADATA_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stable_content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def domain_for(url: str) -> str:
    return urlparse(url).netloc.lower()


def file_type_for(url: str, content_type: str = "") -> str:
    lowered = urlparse(url).path.lower()
    ctype = content_type.lower()
    if lowered.endswith(".pdf") or "application/pdf" in ctype:
        return "PDF"
    return "HTML"


def raw_extension(source_type: str, url: str) -> str:
    if source_type == "PDF":
        return ".pdf"
    guessed = mimetypes.guess_extension(mimetypes.guess_type(url)[0] or "") or ".html"
    return ".html" if guessed not in {".htm", ".html"} else guessed


class RobotsCache:
    def __init__(self, session: requests.Session):
        self.session = session
        self.cache: dict[str, RobotFileParser] = {}
        self.status: dict[str, str] = {}

    def allowed(self, url: str) -> tuple[bool, str]:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.cache:
            rp = RobotFileParser()
            robots_url = urljoin(base, "/robots.txt")
            rp.set_url(robots_url)
            try:
                resp = self.session.get(robots_url, timeout=REQUEST_TIMEOUT)
                if resp.status_code >= 400:
                    rp.parse([])
                    self.status[base] = f"robots_unavailable:{resp.status_code}"
                else:
                    rp.parse(resp.text.splitlines())
                    self.status[base] = "ok"
            except Exception as exc:
                rp.parse([])
                self.status[base] = f"robots_error:{exc.__class__.__name__}"
            self.cache[base] = rp
        allowed = self.cache[base].can_fetch(USER_AGENT, url)
        return allowed, self.status.get(base, "unknown")


class DomainLimiter:
    def __init__(self):
        self.last_request: dict[str, float] = {}

    def wait(self, url: str) -> None:
        domain = domain_for(url)
        delay = SENSITIVE_DOMAIN_DELAY if any(marker in domain for marker in SENSITIVE_DOMAIN_MARKERS) else DEFAULT_DOMAIN_DELAY
        elapsed = time.monotonic() - self.last_request.get(domain, 0.0)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request[domain] = time.monotonic()


def seed_to_candidate(seed: SourceSeed, robots_allowed: bool, robots_status: str, existing: bool) -> dict:
    target_url = seed.document_url or seed.url
    return {
        "id": seed.id,
        "url": target_url,
        "source_url": seed.url,
        "document_url": seed.document_url,
        "domain": domain_for(target_url),
        "title_guess": seed.title,
        "source_type": seed.source_type,
        "issuer_guess": seed.issuer,
        "trust_tier_guess": seed.trust_tier,
        "authority_level": seed.authority_level,
        "country": seed.country,
        "subdivision": seed.subdivision,
        "agency": seed.agency,
        "publish_date": seed.publish_date,
        "effective_date": seed.effective_date,
        "robots_allowed": robots_allowed,
        "robots_status": robots_status,
        "file_type": seed.source_type,
        "reason": seed.reason,
        "already_in_metadata": existing,
        "checked_at": utc_now(),
    }


def load_seeds(source_set: str) -> list[SourceSeed]:
    if source_set == "boc_core":
        return BOC_CORE_SEEDS
    if source_set == "boc_expand":
        return BOC_EXPAND_SEEDS
    if source_set == "eval_gap_fill":
        return EVAL_GAP_FILL_SEEDS
    if source_set == "all":
        return BOC_CORE_SEEDS + BOC_EXPAND_SEEDS + EVAL_GAP_FILL_SEEDS
    raise ValueError(f"Unsupported source-set: {source_set}")


def dry_run(seeds: list[SourceSeed]) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    session = build_session()
    robots = RobotsCache(session)
    existing_records = load_metadata()
    existing_ids = {r.get("id") for r in existing_records}
    with CANDIDATES_PATH.open("w", encoding="utf-8") as f:
        for seed in seeds:
            target = seed.document_url or seed.url
            allowed, status = robots.allowed(target)
            record = seed_to_candidate(seed, allowed, status, seed.id in existing_ids)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    allowed_count = sum(1 for line in CANDIDATES_PATH.read_text(encoding="utf-8").splitlines() if '"robots_allowed": true' in line)
    print(f"[crawl] dry-run wrote {len(seeds)} candidates -> {CANDIDATES_PATH}")
    print(f"[crawl] robots allowed: {allowed_count}/{len(seeds)}")
    return 0


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
    })
    return session


async def crawl_html_with_crawl4ai(url: str) -> Optional[str]:
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    except Exception:
        return None

    browser_config = BrowserConfig(verbose=False)
    run_config = CrawlerRunConfig(
        word_count_threshold=5,
        excluded_tags=["script", "style", "nav", "footer", "form"],
        exclude_external_links=True,
        remove_overlay_elements=True,
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if not result.success:
            return None
        markdown = result.markdown
        if hasattr(markdown, "fit_markdown") and markdown.fit_markdown:
            return str(markdown.fit_markdown)
        if hasattr(markdown, "raw_markdown") and markdown.raw_markdown:
            return str(markdown.raw_markdown)
        return str(markdown or "").strip() or None


def fetch(session: requests.Session, limiter: DomainLimiter, url: str) -> tuple[int, str, bytes]:
    limiter.wait(url)
    resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True, stream=True)
    content_type = resp.headers.get("Content-Type", "")
    content = b""
    for chunk in resp.iter_content(chunk_size=1024 * 64):
        if not chunk:
            continue
        content += chunk
        if len(content) > MAX_BYTES:
            raise ValueError(f"download exceeded max bytes: {MAX_BYTES}")
    if resp.status_code in (403, 429):
        raise PermissionError(f"HTTP {resp.status_code}")
    resp.raise_for_status()
    return resp.status_code, content_type, content


def record_from_seed(seed: SourceSeed, raw_file: str, md_file: str, content_hash: str, body_chars: int, extraction_status: str) -> dict:
    record = {
        "id": seed.id,
        "raw_file": raw_file,
        "title": seed.title,
        "issuer": seed.issuer,
        "authority_level": seed.authority_level,
        "region": seed.region,
        "topic": seed.topic,
        "source_url": seed.url,
        "document_url": seed.document_url,
        "source_type": seed.source_type,
        "language": seed.language,
        "demo_relevance": seed.demo_relevance or seed.reason,
        "trust_tier": seed.trust_tier,
        "country": seed.country,
        "subdivision": seed.subdivision,
        "agency": seed.agency,
        "crawl_frequency": seed.crawl_frequency,
        "publish_date": seed.publish_date,
        "effective_date": seed.effective_date,
        "collected_at": utc_now(),
        "raw_file_path": str((RAW_DIR / raw_file).relative_to(ROOT)),
        "extraction_status": extraction_status,
        "markdown_file": md_file,
        "body_chars": body_chars,
        "content_hash": content_hash,
    }
    return record


def write_markdown(record: dict, body: str) -> None:
    md_path = ROOT / record["markdown_file"]
    frontmatter = ["---"]
    for key in [
        "id", "title", "issuer", "authority_level", "region", "topic", "source_url",
        "document_url", "source_type", "language", "trust_tier", "country",
        "subdivision", "agency", "crawl_frequency", "publish_date", "effective_date",
        "demo_relevance", "collected_at",
        "raw_file_path", "extraction_status", "content_hash",
    ]:
        if key in record:
            rendered = yaml_scalar(record[key])
            if isinstance(record[key], list) or "\n" in rendered:
                frontmatter.append(f"{key}:")
                frontmatter.append(rendered)
            else:
                frontmatter.append(f"{key}: {rendered}")
    frontmatter.append("---")
    md_path.write_text("\n".join(frontmatter) + f"\n\n# {record['title']}\n\n{body}\n", encoding="utf-8")


def log_error(seed: SourceSeed, error: str, stage: str) -> None:
    ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "id": seed.id,
            "url": seed.document_url or seed.url,
            "stage": stage,
            "error": error,
            "logged_at": utc_now(),
        }, ensure_ascii=False) + "\n")


def crawl_seed(session: requests.Session, robots: RobotsCache, limiter: DomainLimiter, seed: SourceSeed) -> Optional[dict]:
    target_url = seed.document_url or seed.url
    allowed, robots_status = robots.allowed(target_url)
    if not allowed:
        log_error(seed, f"blocked_by_robots:{robots_status}", "robots")
        print(f"[crawl] SKIP robots blocked {seed.id} {target_url}")
        return None

    try:
        status_code, content_type, content = fetch(session, limiter, target_url)
    except Exception as exc:
        log_error(seed, f"{exc.__class__.__name__}: {exc}", "fetch")
        print(f"[crawl] FAIL fetch {seed.id}: {exc}")
        return None

    source_type = file_type_for(target_url, content_type)
    seed.source_type = source_type
    raw_file = f"crawl_{seed.id}{raw_extension(source_type, target_url)}"
    raw_path = RAW_DIR / raw_file
    md_file = f"data/{seed.id}.md"
    content_hash = stable_content_hash(content)

    if source_type == "PDF":
        body, extraction_status = pdf_bytes_to_text(content, raw_path)
    else:
        raw_path.write_bytes(content)
        markdown = asyncio.run(crawl_html_with_crawl4ai(target_url))
        body = clean_text(markdown) if markdown else html_bytes_to_text(content)
        body = trim_body_to_title(body, seed.title)
        body = trim_body_to_anchor(body, seed.content_anchor)
        extraction_status = "ok" if body else "empty"

    if not body:
        body = (
            "Text extraction did not produce readable body content. "
            "Use the source_url or document_url in the metadata to re-fetch the document."
        )

    if len(body) < 500 and not seed.allow_short_body:
        log_error(seed, f"body_too_short:{len(body)}", "quality")
        print(f"[crawl] SKIP low-quality {seed.id}: chars={len(body)}")
        return None

    record = record_from_seed(
        seed=seed,
        raw_file=raw_file,
        md_file=md_file,
        content_hash=content_hash,
        body_chars=len(body),
        extraction_status=extraction_status,
    )
    record["http_status"] = status_code
    record["content_type"] = content_type
    write_markdown(record, body)
    print(f"[crawl] OK {seed.id} {source_type} chars={len(body)}")
    return record


def commit_crawl(seeds: list[SourceSeed], limit: Optional[int], commit_ingest: bool, persist_dir: str) -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_metadata()
    existing_by_id = {record.get("id"): record for record in existing}
    session = build_session()
    robots = RobotsCache(session)
    limiter = DomainLimiter()
    selected = seeds[: limit] if limit else seeds
    added_or_updated: list[dict] = []

    for seed in selected:
        old = existing_by_id.get(seed.id)
        record = crawl_seed(session, robots, limiter, seed)
        if not record:
            continue
        if old and old.get("content_hash") == record.get("content_hash"):
            print(f"[crawl] unchanged {seed.id}; updating parsed metadata only")
            record["collected_at"] = old.get("collected_at") or record["collected_at"]
            added_or_updated.append(record)
        elif old and int(record.get("body_chars") or 0) < max(500, int(old.get("body_chars") or 0) // 2):
            print(
                f"[crawl] low-quality update {seed.id}; keeping existing metadata "
                f"old_chars={old.get('body_chars')} new_chars={record.get('body_chars')}"
            )
            added_or_updated.append(old)
        else:
            added_or_updated.append(record)

    if not added_or_updated:
        print("[crawl] no records crawled successfully")
        return 1

    updated_by_id = {record.get("id"): record for record in existing}
    for record in added_or_updated:
        updated_by_id[record["id"]] = record
    ordered: list[dict] = []
    seen: set[str] = set()
    for record in existing:
        record_id = record.get("id")
        if record_id in updated_by_id:
            ordered.append(updated_by_id[record_id])
            seen.add(record_id)
    for seed in selected:
        if seed.id in updated_by_id and seed.id not in seen:
            ordered.append(updated_by_id[seed.id])
            seen.add(seed.id)
    write_metadata(ordered)
    print(f"[crawl] metadata updated -> {METADATA_PATH} records={len(ordered)}")

    if commit_ingest:
        return run_ingestion(persist_dir)
    return 0


def run_ingestion(persist_dir: str) -> int:
    persist_enabled = bool(os.environ.get("DASHSCOPE_API_KEY") and os.environ.get("LANGSMITH_API_KEY"))
    cmd = [
        sys.executable,
        str(ROOT / "files" / "ingestion.py"),
        "--input",
        str(DATA_DIR),
        "--output",
        str(CHUNKS_PATH),
        "--sample",
        "0",
    ]
    if persist_enabled:
        cmd.extend(["--persist", "--persist-dir", persist_dir])
    else:
        print(
            "[crawl] DASHSCOPE_API_KEY/LANGSMITH_API_KEY not set; "
            "rebuilding chunks.jsonl only and skipping Chroma persistence."
        )
    print("[crawl] running ingestion:", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=str(ROOT), text=True)
    return completed.returncode


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="First-pass official/BOC crawler for CrossBridge RAG.")
    parser.add_argument(
        "--source-set",
        default="boc_core",
        choices=["boc_core", "boc_expand", "eval_gap_fill", "all"],
    )
    parser.add_argument("--dry-run", action="store_true", help="Only write data/crawl_candidates.jsonl.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum seeds to crawl.")
    parser.add_argument("--commit-ingest", action="store_true", help="Run files/ingestion.py --persist after crawl.")
    parser.add_argument("--persist-dir", default=str(DATA_DIR / "chroma"))
    args = parser.parse_args(argv)

    seeds = load_seeds(args.source_set)
    if args.dry_run:
        return dry_run(seeds)
    return commit_crawl(seeds, args.limit, args.commit_ingest, args.persist_dir)


if __name__ == "__main__":
    raise SystemExit(main())

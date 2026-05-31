from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, get_args

import httpx
from pydantic import ValidationError

from .models import LoanProduct, isoformat_utc
from .schemas import (
    BusinessScenario,
    ClarifierDecision,
    DraftProfile,
    DraftProfileUpdate,
    FinancingPurpose,
)

REQUIRED_FIELDS = (
    "business_scenario",
    "annual_turnover_hkd",
    "financing_purpose",
    "requested_amount_hkd",
)
FIELD_LABELS = {
    "business_scenario": "跨境业务场景",
    "annual_turnover_hkd": "年营业额",
    "financing_purpose": "融资用途",
    "requested_amount_hkd": "计划融资金额",
    "order_scale_hkd": "订单规模",
    "target_market": "目标市场",
    "business_age_years": "经营年限",
}
QUESTION_BY_FIELD = {
    "business_scenario": "您主要是哪类跨境业务：海外采购、跨境电商、出口贸易还是海外投资？",
    "annual_turnover_hkd": "贵公司去年的年营业额大约是多少港币？",
    "financing_purpose": "这笔融资主要用于支付供应商、备货、履行出口订单、日常周转还是海外投资？",
    "requested_amount_hkd": "您计划申请的融资金额大约是多少港币？",
}

ACTION_PATTERNS = [
    r"帮我.{0,8}(找|选|推荐).{0,5}(贷款|融资|loan|financing)",
    r"(help me|please).{0,8}(find|choose|recommend).{0,8}(loan|financing)",
    r"(适合|推荐|匹配).{0,8}(贷款|融资|loan|financing)",
    r"(申请|需要|想要|want|need|apply).{0,8}(贷款|融资|loan|financing)",
    r"(贷款|融资|loan|financing).{0,8}(产品|方案|option|product|recommend)",
]
INFORMATIONAL_PATTERNS = [
    r"(是什么|解释|定义|要求|条件|文件|材料|流程|政策|合规|风险|利率怎么算|what is|explain|requirement|document|policy|compliance)",
]


NUMERIC_FIELDS = ("annual_turnover_hkd", "requested_amount_hkd", "order_scale_hkd", "business_age_years")


def missing_required_fields(profile: DraftProfile) -> list[str]:
    return [field for field in REQUIRED_FIELDS if getattr(profile, field) is None]


def try_direct_numeric_fill(target_field: str | None, message: str) -> DraftProfileUpdate | None:
    """
    确定性兜底：当前正在问一个数值字段、且用户这句话「基本上就是一个金额」时，
    直接把解析出的数值塞进 target_field，跳过 LLM —— 裸数字 1000000 / 700万 / 7m 秒填、零误判。
    若解析不出（如中文数字「一千万」无阿拉伯数字），返回 None 交给带 target 的 LLM。
    """
    if target_field not in NUMERIC_FIELDS:
        return None
    amount = _parse_hkd_amount(message)
    if amount is None or amount <= 0:
        return None
    # 句子里若除了数字还含明显「别的字段」线索，就别抢，交给 LLM 判断
    lower = message.lower()
    if target_field == "annual_turnover_hkd" and re.search(r"(融资|融資|贷款|貸款|申请|申請|额度|額度)", lower):
        return None
    if target_field == "requested_amount_hkd" and re.search(r"(营业额|營業額|turnover|revenue)", lower):
        return None
    return DraftProfileUpdate.model_validate({target_field: amount})


_CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "兩": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000, "萬": 10000,
             "亿": 100_000_000, "億": 100_000_000}


def _parse_chinese_amount(text: str) -> int | None:
    """解析中文数字金额（一千万 / 七百万 / 两百万 / 一千五百万 / 十万 等），LLM 不可靠时兜底。"""
    run = re.search(r"[零〇一二两兩三四五六七八九十百千万萬亿億]+", text)
    if not run:
        return None
    s = run.group(0)
    total = 0      # 已结算的「万/亿」段累加
    section = 0    # 当前万以下段
    number = 0     # 当前一位数字
    for ch in s:
        if ch in _CN_DIGITS:
            number = _CN_DIGITS[ch]
        else:
            unit = _CN_UNITS[ch]
            if unit >= 10000:  # 万 / 亿：结算当前段
                section = (section + number) * unit
                total += section
                section = 0
            else:              # 十 / 百 / 千
                section += (number or 1) * unit
            number = 0
    result = total + section + number
    return result if result > 0 else None


def _parse_hkd_amount(text: str) -> int | None:
    normalized = text.replace(",", "").replace("，", "").strip().lower()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(亿|萬|万|千|m|million|k)?", normalized)
    if not match:
        # 没有阿拉伯数字 —— 尝试中文数字（一千万 / 七百万 …）
        return _parse_chinese_amount(text)
    value = float(match.group(1))
    unit = match.group(2)
    multiplier = {
        "亿": 100_000_000,
        "萬": 10_000,
        "万": 10_000,
        "千": 1_000,
        "m": 1_000_000,
        "million": 1_000_000,
        "k": 1_000,
    }.get(unit, 1)
    return int(value * multiplier)


def _find_amount_near(text: str, anchors: list[str]) -> int | None:
    for anchor in anchors:
        match = re.search(
            rf"{anchor}.{{0,16}}?(\d+(?:\.\d+)?)\s*(亿|萬|万|千|m|million|k)?",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return _parse_hkd_amount(match.group(1) + (match.group(2) or ""))
    return None


def extract_prefill(message: str) -> DraftProfileUpdate:
    text = message.strip()
    lower = text.lower()
    updates: dict[str, Any] = {}

    if re.search(r"(供应商|採購|采购|supplier|procurement)", lower):
        updates["business_scenario"] = "overseas_procurement"
    elif re.search(r"(跨境电商|跨境電商|e-?commerce)", lower):
        updates["business_scenario"] = "cross_border_ecommerce"
    elif re.search(r"(出口|export)", lower):
        updates["business_scenario"] = "export_trade"
    elif re.search(r"(海外投资|海外投資|overseas investment)", lower):
        updates["business_scenario"] = "overseas_investment"

    turnover = _find_amount_near(lower, ["年营业额", "年營業額", "营业额", "營業額", "turnover", "revenue"])
    if turnover:
        updates["annual_turnover_hkd"] = turnover

    requested = _find_amount_near(
        lower,
        [
            "融资金额",
            "融資金額",
            "申请",
            "申請",
            "融资",
            "融資",
            "贷款",
            "貸款",
            "支付",
            "付",
            "amount",
            "finance",
            "loan",
            "pay",
        ],
    )
    if requested and requested != turnover:
        updates["requested_amount_hkd"] = requested

    if re.search(r"(供应商|採購|采购|supplier|procurement)", lower):
        updates["financing_purpose"] = "procurement_payment"
    elif re.search(r"(备货|備貨|stock|inventory)", lower):
        updates["financing_purpose"] = "stocking"
    elif re.search(r"(履约|履約|订单|訂單|order fulfillment)", lower):
        updates["financing_purpose"] = "order_fulfillment"
    elif re.search(r"(周转|週轉|working capital)", lower):
        updates["financing_purpose"] = "working_capital"
    elif re.search(r"(投资|投資|investment)", lower):
        updates["financing_purpose"] = "investment"

    markets = {
        "越南": "越南",
        "vietnam": "越南",
        "vn": "越南",
        "东南亚": "东南亚",
        "東南亞": "东南亚",
        "southeast asia": "东南亚",
        "sea": "东南亚",
    }
    for keyword, label in markets.items():
        if re.search(rf"\b{re.escape(keyword)}\b", lower) if keyword.isascii() else keyword in lower:
            updates["target_market"] = label
            break

    return DraftProfileUpdate.model_validate(updates)


def route_intent(message: str) -> dict[str, Any]:
    text = message.strip()
    has_action = any(re.search(pattern, text, re.IGNORECASE) for pattern in ACTION_PATTERNS)
    has_information = any(
        re.search(pattern, text, re.IGNORECASE) for pattern in INFORMATIONAL_PATTERNS
    )
    if has_action:
        intent = "loan_matching_action"
        confidence = 0.95
    elif has_information:
        intent = "informational_qa"
        confidence = 0.9
    else:
        intent = "ambiguous"
        confidence = 0.5
    return {
        "intent": intent,
        "confidence": confidence,
        "show_cta": intent == "loan_matching_action",
        "prefill": extract_prefill(text).model_dump(exclude_none=True),
    }


def merge_profile(profile: DraftProfile, updates: DraftProfileUpdate) -> DraftProfile:
    return DraftProfile.model_validate(
        {**profile.model_dump(), **updates.model_dump(exclude_none=True)}
    )


def fallback_question(profile: DraftProfile) -> str | None:
    missing = missing_required_fields(profile)
    return QUESTION_BY_FIELD.get(missing[0]) if missing else None


_VALID_SCENARIOS = frozenset(get_args(BusinessScenario))
_VALID_PURPOSES = frozenset(get_args(FinancingPurpose))
_INT_FIELDS = (
    "annual_turnover_hkd",
    "requested_amount_hkd",
    "order_scale_hkd",
    "business_age_years",
)


def _coerce_positive_int(value: Any) -> int | None:
    """LLM 有时把金额回成字符串/带逗号/带单位 —— 尽力转成正整数，失败就丢。"""
    if isinstance(value, bool):  # bool 是 int 的子类，单独挡掉
        return None
    if isinstance(value, (int, float)):
        number = int(value)
    elif isinstance(value, str):
        parsed = _parse_hkd_amount(value)
        if parsed is None:
            return None
        number = parsed
    else:
        return None
    return number if number > 0 else None


def sanitize_extracted_updates(raw: Any) -> DraftProfileUpdate:
    """
    逐字段宽容校验：只保留合法字段，丢掉非法枚举 / 多余 key / 坏类型，
    而不是因为一个坏字段就整条 decision 作废（原来的 extra="forbid" 行为）。
    """
    if not isinstance(raw, dict):
        return DraftProfileUpdate()
    clean: dict[str, Any] = {}
    if raw.get("business_scenario") in _VALID_SCENARIOS:
        clean["business_scenario"] = raw["business_scenario"]
    if raw.get("financing_purpose") in _VALID_PURPOSES:
        clean["financing_purpose"] = raw["financing_purpose"]
    for field in _INT_FIELDS:
        coerced = _coerce_positive_int(raw.get(field))
        if coerced is not None:
            clean[field] = coerced
    market = raw.get("target_market")
    if isinstance(market, str) and market.strip():
        clean["target_market"] = market.strip()[:80]
    try:
        return DraftProfileUpdate.model_validate(clean)
    except ValidationError:
        return DraftProfileUpdate()


def parse_clarifier_payload(payload: str | dict[str, Any]) -> ClarifierDecision:
    if isinstance(payload, str):
        cleaned = payload.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        payload = {}
    question = payload.get("question_to_user")
    if not isinstance(question, str):
        question = None
    elif len(question) > 300:
        question = question[:300]
    missing_slot = payload.get("missing_slot")
    if not isinstance(missing_slot, str):
        missing_slot = None
    return ClarifierDecision(
        extracted_updates=sanitize_extracted_updates(payload.get("extracted_updates")),
        ready_to_match=bool(payload.get("ready_to_match", False)),
        missing_slot=missing_slot,
        question_to_user=question,
    )


@dataclass
class ClarifierResult:
    decision: ClarifierDecision | None
    mode: str
    error: str | None = None


class LlmClarifier:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 20,
    ) -> None:
        self.base_url = (
            base_url
            or os.environ.get("CROSSBRIDGE_CLARIFIER_BASE_URL")
            or os.environ.get("QWEN_BASE_URL")
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ).rstrip("/")
        self.api_key = (
            api_key
            or os.environ.get("CROSSBRIDGE_CLARIFIER_API_KEY")
            or os.environ.get("DASHSCOPE_API_KEY")
        )
        self.model = (
            model
            or os.environ.get("CROSSBRIDGE_CLARIFIER_MODEL")
            or os.environ.get("QWEN_MODEL")
            or "qwen-plus"
        )
        self.timeout_seconds = timeout_seconds

    def clarify(
        self, profile: DraftProfile, message: str, target_field: str | None = None
    ) -> ClarifierResult:
        if not self.api_key:
            return ClarifierResult(None, "manual_fallback", "clarifier API key is not configured")
        prompt = {
            "known_profile": profile.model_dump(exclude_none=True),
            "latest_user_message": message,
            # 关键：告诉 LLM「当前正在问哪个字段」，否则用户打裸数字会被乱塞
            "current_target_field": target_field,
            "required_fields": list(REQUIRED_FIELDS),
            "allowed_scenarios": [
                "overseas_procurement",
                "cross_border_ecommerce",
                "export_trade",
                "overseas_investment",
            ],
            "allowed_purposes": [
                "procurement_payment",
                "stocking",
                "order_fulfillment",
                "working_capital",
                "investment",
            ],
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "temperature": 0,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Extract SME financing profile updates. Return JSON only with "
                                    "extracted_updates, ready_to_match, missing_slot, question_to_user. "
                                    "Never invent missing values. Ask at most one concise Chinese question. "
                                    "IMPORTANT: the user is currently answering the question for "
                                    "`current_target_field`. If the message is just a value (a number, "
                                    "an amount like '一千万'/'700万'/'2 million', or a single phrase), put it "
                                    "into `current_target_field`. Only assign a different field when the user "
                                    "explicitly names it. annual_turnover_hkd and requested_amount_hkd are "
                                    "different things — never swap them."
                                ),
                            },
                            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                        ],
                    },
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return ClarifierResult(parse_clarifier_payload(content), "llm")
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            return ClarifierResult(None, "manual_fallback", str(exc))


def product_snapshot(product: LoanProduct) -> dict[str, Any]:
    disclaimer = (
        "DEMO ONLY · 非银行正式产品 · 实际资格需由银行审批"
        if product.demo_only
        else "BOCHK 官方公开页面候选 · 不代表银行审批 · 实际资格与条款需由客户经理确认"
    )
    return {
        "product_id": product.id,
        "product_name": product.product_name,
        "product_description": product.product_description,
        "loan_limit_text": product.loan_limit_text,
        "interest_rate_text": product.interest_rate_text,
        "tenor_text": product.tenor_text,
        "repayment_method_text": product.repayment_method_text,
        "fee_text": product.fee_text,
        "public_guidance": json.loads(product.public_guidance_json),
        "required_documents": json.loads(product.required_documents_json),
        "application_thresholds": json.loads(product.application_thresholds_json),
        "localization": json.loads(product.localization_json),
        "source_url": product.source_url,
        "source_title": product.source_title,
        "source_checked_at": isoformat_utc(product.source_checked_at),
        "source_content_hash": product.source_content_hash,
        "source_refs": json.loads(product.source_refs_json),
        "review_status": product.review_status,
        "review_notes": json.loads(product.review_notes_json),
        "demo_only": product.demo_only,
        "disclaimer": disclaimer,
    }


def match_products(profile: DraftProfile, products: list[LoanProduct]) -> list[dict[str, Any]]:
    missing = missing_required_fields(profile)
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    results = []
    for product in products:
        scenarios = json.loads(product.scenarios_json) or [product.business_scenario]
        purposes = json.loads(product.purposes_json)
        if profile.business_scenario not in scenarios:
            continue
        if profile.financing_purpose not in purposes:
            continue
        if (
            product.min_requested_amount_hkd is not None
            and profile.requested_amount_hkd < product.min_requested_amount_hkd
        ):
            continue
        if (
            product.max_requested_amount_hkd is not None
            and profile.requested_amount_hkd > product.max_requested_amount_hkd
        ):
            continue
        if (
            product.min_annual_turnover_hkd is not None
            and profile.annual_turnover_hkd < product.min_annual_turnover_hkd
        ):
            continue

        reason_codes = ["scenario_supported", "purpose_supported"]
        needs_rm_confirmation = []
        if (
            product.min_requested_amount_hkd is not None
            or product.max_requested_amount_hkd is not None
        ):
            reason_codes.append("amount_within_published_term")
        else:
            reason_codes.append("amount_requires_rm_confirmation")
            needs_rm_confirmation.append("loan_limit")
        if product.min_annual_turnover_hkd is not None:
            reason_codes.append("turnover_meets_published_threshold")
        else:
            reason_codes.append("turnover_requires_rm_confirmation")
            needs_rm_confirmation.append("eligibility")
        if not product.interest_rate_text or "需客户经理确认" in product.interest_rate_text or "relationship-manager" in product.interest_rate_text:
            needs_rm_confirmation.append("interest_rate")
        if not product.demo_only:
            reason_codes.append("official_source_verified")
            if product.review_status != "human_reviewed":
                needs_rm_confirmation.append("catalog_human_review")
        if not product.tenor_text or "需客户经理确认" in product.tenor_text or "relationship-manager" in product.tenor_text:
            needs_rm_confirmation.append("tenor")
        if (
            not product.repayment_method_text
            or "需客户经理确认" in product.repayment_method_text
            or "relationship-manager" in product.repayment_method_text
        ):
            needs_rm_confirmation.append("repayment_method")
        needs_rm_confirmation.extend(
            field
            for field in ("order_scale_hkd", "target_market", "business_age_years")
            if getattr(profile, field) is None
        )
        needs_rm_confirmation = list(dict.fromkeys(needs_rm_confirmation))
        results.append(
            {
                "score": 100,
                "reasons": reason_codes,
                "needs_rm_confirmation": needs_rm_confirmation,
                "product": product_snapshot(product),
            }
        )
    return sorted(results, key=lambda item: (-item["score"], item["product"]["product_id"]))

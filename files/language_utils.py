"""Deterministic response-language selection for CrossBridge conversations."""

from __future__ import annotations

import re
from typing import Literal

ResponseLanguage = Literal["zh", "en"]
AnswerLanguage = Literal["zh", "en", "bilingual"]

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-_][A-Za-z0-9]+)*")
_HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_BILINGUAL_REQUEST_RE = re.compile(
    r"中英(?:文)?(?:双语|对照)|双语(?:回答|作答|回复|输出)?|"
    r"\bbilingual\b|(?:in|using)\s+both\s+(?:chinese\s+and\s+english|english\s+and\s+chinese)",
    re.IGNORECASE,
)
_ENGLISH_REQUEST_RE = re.compile(
    r"(?:请)?用英文(?:回答|作答|回复|输出)?|英文(?:回答|作答|回复|输出)|"
    r"(?:reply|respond|answer|write)\s+in\s+english|(?:in|using)\s+english",
    re.IGNORECASE,
)
_CHINESE_REQUEST_RE = re.compile(
    r"(?:请)?用中文(?:回答|作答|回复|输出)?|中文(?:回答|作答|回复|输出)|"
    r"(?:reply|respond|answer|write)\s+in\s+chinese|(?:in|using)\s+chinese",
    re.IGNORECASE,
)


def normalize_language(value: str | None, default: ResponseLanguage = "zh") -> ResponseLanguage:
    return "en" if str(value or "").lower() == "en" else default


def normalize_answer_language(
    value: str | None, default: AnswerLanguage = "zh"
) -> AnswerLanguage:
    normalized = str(value or "").lower()
    if normalized == "bilingual":
        return "bilingual"
    if normalized == "en":
        return "en"
    return default


def detect_explicit_language_request(text: str) -> AnswerLanguage | None:
    """Return an explicitly requested answer language before dominant-language detection."""
    value = str(text or "")
    if _BILINGUAL_REQUEST_RE.search(value):
        return "bilingual"
    if _ENGLISH_REQUEST_RE.search(value):
        return "en"
    if _CHINESE_REQUEST_RE.search(value):
        return "zh"
    return None


def detect_response_language(text: str) -> ResponseLanguage | None:
    """Return the dominant natural language, ignoring codes and identifiers."""
    cleaned = _URL_RE.sub(" ", str(text or ""))
    han_count = len(_HAN_RE.findall(cleaned))

    latin_count = 0
    for token in _TOKEN_RE.findall(cleaned):
        # Product codes, acronyms, and SWIFT fragments are not language evidence.
        if token.isupper() or len(token) <= 1:
            continue
        latin_count += len(token)

    if not han_count and not latin_count:
        return None
    if han_count and not latin_count:
        return "zh"
    if latin_count and not han_count:
        return "en"
    return "zh" if han_count >= latin_count else "en"


def resolve_response_language(
    text: str,
    *,
    previous: str | None = None,
    fallback: str | None = None,
) -> ResponseLanguage:
    return (
        detect_response_language(text)
        or normalize_language(previous, default=normalize_language(fallback))
    )


def resolve_answer_language(
    text: str,
    *,
    previous: str | None = None,
    fallback: str | None = None,
) -> AnswerLanguage:
    """Resolve policy-Q&A answer language without widening Function 1 state."""
    return (
        detect_explicit_language_request(text)
        or detect_response_language(text)
        or normalize_answer_language(
            previous, default=normalize_answer_language(fallback)
        )
    )

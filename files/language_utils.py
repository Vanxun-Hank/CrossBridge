"""Deterministic response-language selection for CrossBridge conversations."""

from __future__ import annotations

import re
from typing import Literal

ResponseLanguage = Literal["zh", "en"]

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-_][A-Za-z0-9]+)*")
_HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def normalize_language(value: str | None, default: ResponseLanguage = "zh") -> ResponseLanguage:
    return "en" if str(value or "").lower() == "en" else default


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

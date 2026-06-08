#!/usr/bin/env python3
"""Focused eval for deterministic Chinese/English response-language following."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "files"))

from fastapi.testclient import TestClient

from files.language_utils import (
    detect_explicit_language_request,
    detect_response_language,
    resolve_answer_language,
    resolve_response_language,
)
from rag_engine import SYSTEM_PROMPTS, build_prompt
from server.business.app import create_app
from server.business.matching import ClarifierResult


class FakeUnavailableClarifier:
    def clarify(self, profile, message: str, target_field: str | None = None) -> ClarifierResult:
        return ClarifierResult(None, "manual_fallback", "simulated LLM outage")


class Eval:
    def __init__(self) -> None:
        self.passed = 0
        self.total = 0

    def check(self, name: str, condition: bool) -> None:
        self.total += 1
        if condition:
            self.passed += 1
        else:
            print(f"FAIL: {name}")


def main() -> int:
    ev = Eval()
    ev.check("detect Chinese", detect_response_language("我想了解跨境付款要求") == "zh")
    ev.check("detect English", detect_response_language("What documents do I need?") == "en")
    ev.check("ignore product code", detect_response_language("BOCHK") is None)
    ev.check("ignore SWIFT", detect_response_language("BKCHHKHHXXX") is None)
    ev.check(
        "Chinese dominates acronym",
        detect_response_language("BOCHK 的进口融资需要什么材料？") == "zh",
    )
    ev.check(
        "English dominates Chinese proper noun",
        detect_response_language("What documents are needed for 中银香港 financing?") == "en",
    )
    ev.check(
        "ambiguous input inherits previous language",
        resolve_response_language("BOCHK", previous="en", fallback="zh") == "en",
    )
    ev.check(
        "first ambiguous input falls back to settings",
        resolve_response_language("12345", fallback="en") == "en",
    )
    ev.check(
        "explicit bilingual request wins over Chinese query",
        detect_explicit_language_request("请用中英双语说明跨境付款要求") == "bilingual",
    )
    ev.check(
        "explicit English request wins over Chinese query",
        resolve_answer_language("请用英文回答进口融资需要什么材料？") == "en",
    )
    ev.check(
        "explicit Chinese request wins over English query",
        resolve_answer_language("Please reply in Chinese: what documents are required?") == "zh",
    )
    ev.check(
        "policy answer language supports bilingual",
        resolve_answer_language("请中英对照说明 BOCHK 汇款要求") == "bilingual",
    )

    retrieved = [
        (
            {
                "source_name": "BOCHK",
                "region": "香港",
                "effective_date": "2026-01-01",
                "title": "Trade Finance",
                "content": "Official material",
            },
            1.0,
        )
    ]
    english_prompt = build_prompt("What documents are required?", retrieved, response_language="en")
    chinese_prompt = build_prompt("需要什么材料？", retrieved, response_language="zh")
    bilingual_prompt = build_prompt("请中英双语说明。", retrieved, response_language="bilingual")
    ev.check("English RAG prompt wrapper", "[Reference materials]" in english_prompt)
    ev.check("English RAG prompt source marker", "[Source1] (citable)" in english_prompt)
    ev.check("Chinese RAG prompt wrapper", "【参考资料】" in chinese_prompt)
    ev.check("Chinese RAG prompt source marker", "[资料1] (可引用)" in chinese_prompt)
    ev.check("Bilingual RAG prompt wrapper", "【参考资料 / Reference materials】" in bilingual_prompt)
    ev.check("Bilingual RAG prompt instruction", "中文和英文中英对照作答" in bilingual_prompt)
    ev.check("English system prompt is explicit", "Answer entirely in English" in SYSTEM_PROMPTS["en"])
    ev.check("Chinese system prompt is explicit", "必须全程使用中文回答" in SYSTEM_PROMPTS["zh"])
    ev.check("Bilingual system prompt is explicit", "BOTH Chinese and English" in SYSTEM_PROMPTS["bilingual"])

    with tempfile.TemporaryDirectory() as temp_dir:
        db_url = f"sqlite:///{Path(temp_dir) / 'language_eval.db'}"
        app = create_app(
            database_url=db_url,
            clarifier=FakeUnavailableClarifier(),
            catalog_mode="demo",
        )
        with TestClient(app) as client:
            session = client.post(
                "/crossbridge/v1/loan-matching/sessions",
                json={"sme_id": "language_eval", "ui_language": "en"},
            ).json()
            ev.check("F1 initial question follows English settings", session["response_language"] == "en")
            ev.check("F1 initial question is English", session["current_question"].startswith("Which"))

            session = client.post(
                f"/crossbridge/v1/loan-matching/sessions/{session['id']}/clarify",
                json={"message": "BOCHK", "ui_language": "zh"},
            ).json()
            ev.check("F1 ambiguous code inherits English", session["response_language"] == "en")
            ev.check("F1 ambiguous code keeps English question", session["current_question"].startswith("Which"))

            session = client.post(
                f"/crossbridge/v1/loan-matching/sessions/{session['id']}/clarify",
                json={"message": "我主要做出口贸易", "ui_language": "en"},
            ).json()
            ev.check("F1 clear Chinese switches language", session["response_language"] == "zh")
            ev.check("F1 question switches to Chinese", session["current_question"].startswith("您主要"))

            resumed = client.post(
                "/crossbridge/v1/loan-matching/sessions",
                json={"sme_id": "language_eval", "ui_language": "en"},
            ).json()
            ev.check("F1 resume uses current settings fallback", resumed["response_language"] == "en")
            ev.check("F1 resumed question follows current settings", resumed["current_question"].startswith("Which"))

    print({"passed": ev.passed, "total": ev.total})
    return 0 if ev.passed == ev.total else 1


if __name__ == "__main__":
    raise SystemExit(main())

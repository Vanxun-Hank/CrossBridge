from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BusinessScenario = Literal[
    "overseas_procurement",
    "cross_border_ecommerce",
    "export_trade",
    "overseas_investment",
]
FinancingPurpose = Literal[
    "procurement_payment",
    "stocking",
    "order_fulfillment",
    "working_capital",
    "investment",
]
UiLanguage = Literal["zh", "en"]


class DraftProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_scenario: BusinessScenario | None = None
    annual_turnover_hkd: int | None = None
    financing_purpose: FinancingPurpose | None = None
    requested_amount_hkd: int | None = None
    order_scale_hkd: int | None = None
    target_market: str | None = Field(default=None, max_length=80)
    business_age_years: int | None = None

    @field_validator(
        "annual_turnover_hkd",
        "requested_amount_hkd",
        "order_scale_hkd",
        "business_age_years",
    )
    @classmethod
    def positive_numbers_only(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("must be greater than zero")
        return value


class DraftProfileUpdate(DraftProfile):
    pass


class RouteIntentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class CreateSessionRequest(BaseModel):
    sme_id: str = Field(default="demo_sme_001", pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    prefill: DraftProfileUpdate = Field(default_factory=DraftProfileUpdate)
    ui_language: UiLanguage = "zh"


class UpdateDraftRequest(BaseModel):
    updates: DraftProfileUpdate


class SaveDraftRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    selected_product_ids: list[str] = Field(default_factory=list)


class ClarifyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    ui_language: UiLanguage | None = None


class ClarifierDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extracted_updates: DraftProfileUpdate = Field(default_factory=DraftProfileUpdate)
    ready_to_match: bool
    missing_slot: str | None = None
    question_to_user: str | None = Field(default=None, max_length=300)

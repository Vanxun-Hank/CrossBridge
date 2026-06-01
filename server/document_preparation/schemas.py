from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ScenarioCode = Literal["import_payment", "export_fulfillment"]


class CreatePackageRequest(BaseModel):
    sme_id: str = Field(default="demo_sme_001", pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    scenario_code: ScenarioCode
    selected_product_id: str | None = Field(default=None, max_length=64)
    origin_matching_session_id: str | None = Field(default=None, max_length=36)


class UpdateProductRequest(BaseModel):
    selected_product_id: str | None = Field(default=None, max_length=64)


class UpdateChecklistRequest(BaseModel):
    item_code: str = Field(..., min_length=1, max_length=80)
    checked: bool


class UpdateTemplateRequest(BaseModel):
    content: dict[str, Any] = Field(default_factory=dict)


class UpdateOfficialFormDraftRequest(BaseModel):
    # Raw PDF.js annotation values keyed by AcroForm field name. The server filters
    # these against the registry whitelist before persisting; unknown keys are dropped.
    values: dict[str, Any] = Field(default_factory=dict)

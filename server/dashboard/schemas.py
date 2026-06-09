from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PolicyBookmarkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sme_id: str = Field(default="demo_sme_001", pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    title: str = Field(min_length=1, max_length=240)
    source_url: str = Field(min_length=1, max_length=2000)
    source_title: str | None = Field(default=None, max_length=240)
    snippet: str | None = Field(default=None, max_length=2000)
    document_type: str | None = Field(default=None, max_length=80)
    trust_tier: str | None = Field(default=None, max_length=80)
    origin_chat_id: str | None = Field(default=None, max_length=80)


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sme_id: str = Field(default="demo_sme_001", pattern=r"^[a-zA-Z0-9_-]{1,64}$")

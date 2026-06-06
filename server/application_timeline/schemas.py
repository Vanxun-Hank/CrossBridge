from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

NodeState = Literal[
    "pending", "in_progress", "completed", "rejected", "supplement_required"
]
# The admin may explicitly set only these states (pending is never set by hand).
AdminSettableState = Literal[
    "in_progress", "completed", "rejected", "supplement_required"
]


class CreateApplicationRequest(BaseModel):
    sme_id: str = Field(default="demo_sme_001", pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    # The Function 2 package being submitted (drives idempotency + readiness check).
    origin_package_id: str = Field(..., min_length=1, max_length=64)
    # Product/scenario snapshot — supplied by the client, which already has them loaded.
    product_id: str | None = Field(default=None, max_length=64)
    product_label_zh: str = Field(default="", max_length=400)
    product_label_en: str = Field(default="", max_length=400)
    scenario_code: str = Field(default="", max_length=64)


class AdminNodeUpdateRequest(BaseModel):
    """Partial update of one timeline node by the bank operator.

    All fields optional: send ``state`` to advance/flag the node, and/or the note
    fields to record customer-visible or internal context. ``reminder_at`` accepts an
    ISO-8601 string or null (to clear).
    """

    state: AdminSettableState | None = None
    customer_note_zh: str | None = Field(default=None, max_length=2000)
    customer_note_en: str | None = Field(default=None, max_length=2000)
    internal_note: str | None = Field(default=None, max_length=2000)
    reminder_at: str | None = Field(default=None, max_length=64)

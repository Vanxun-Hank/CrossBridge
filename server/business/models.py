from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


class Base(DeclarativeBase):
    pass


class SmeProfile(Base):
    __tablename__ = "sme_profiles"

    sme_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MatchingSession(Base):
    __tablename__ = "matching_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    draft_profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    clarification_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_language: Mapped[str] = mapped_column(String(2), nullable=False, default="zh")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LoanProduct(Base):
    __tablename__ = "loan_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(160), nullable=False)
    business_scenario: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scenarios_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    purposes_json: Mapped[str] = mapped_column(Text, nullable=False)
    min_requested_amount_hkd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_requested_amount_hkd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_annual_turnover_hkd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    loan_limit_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    interest_rate_text: Mapped[str | None] = mapped_column(String(240), nullable=True)
    tenor_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    repayment_method_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fee_text: Mapped[str | None] = mapped_column(String(240), nullable=True)
    public_guidance_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    required_documents_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    application_thresholds_json: Mapped[str] = mapped_column(Text, nullable=False)
    localization_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    source_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_title: Mapped[str] = mapped_column(String(240), nullable=False, default="")
    source_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_content_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    source_refs_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="demo_only"
    )
    review_notes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    demo_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("matching_sessions.id"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("loan_products.id"), nullable=False
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons_json: Mapped[str] = mapped_column(Text, nullable=False)
    product_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SavedDraft(Base):
    """An explicitly-saved loan-matching draft: a profile snapshot + the products
    the user picked. Unlike SmeProfile (one row per sme_id), a user can keep many."""

    __tablename__ = "saved_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    selected_product_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    matched_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    origin_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("matching_sessions.id"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

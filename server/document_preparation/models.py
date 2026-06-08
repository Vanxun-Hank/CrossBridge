from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Independent declarative base.

    Intentionally NOT shared with Function 1's Base — each service owns its own
    metadata so the two Alembic environments never touch each other's tables.
    """


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocumentPackage(Base):
    __tablename__ = "document_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scenario_code: Mapped[str] = mapped_column(String(64), nullable=False)
    catalog_version: Mapped[str] = mapped_column(String(128), nullable=False, default="unknown")
    selected_product_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    origin_matching_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # One document package per Function 1 saved draft (true one-to-one). Null = legacy
    # per-scenario package created from a live candidate card (no saved draft).
    saved_draft_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DocumentChecklistState(Base):
    __tablename__ = "document_checklist_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    package_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_packages.id"), nullable=False, index=True
    )
    item_code: Mapped[str] = mapped_column(String(80), nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DocumentTemplateDraft(Base):
    __tablename__ = "document_template_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    package_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_packages.id"), nullable=False, index=True
    )
    template_code: Mapped[str] = mapped_column(String(80), nullable=False)
    content_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DocumentAuditEvent(Base):
    __tablename__ = "document_audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    package_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DocumentOfficialFormDraft(Base):
    """User-entered values for an official BOCHK AcroForm, scoped to a source SHA.

    Keyed by (package_id, form_id, source_sha256): if BOCHK reissues a form and the
    cached source SHA changes, old drafts no longer match and are not auto-migrated.
    ``values_json`` holds only registry-whitelisted PDF.js annotation field values.
    """

    __tablename__ = "document_official_form_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    package_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_packages.id"), nullable=False, index=True
    )
    form_id: Mapped[str] = mapped_column(String(80), nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    values_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DocumentTradeTermsAcceptance(Base):
    """One row per (sme_id, terms_sha256): the SME accepted that exact terms version.

    Gating the trade-finance PDFs requires acceptance of the *current* terms SHA from
    the registry; when BOCHK updates the terms, the SME must re-accept the new version.
    """

    __tablename__ = "document_trade_terms_acceptances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    terms_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    terms_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

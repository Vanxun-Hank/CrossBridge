from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Independent declarative base.

    Intentionally NOT shared with Function 1's or Function 2's Base — each service
    owns its own metadata so the Alembic environments never touch each other's tables.
    """


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimelineApplication(Base):
    __tablename__ = "timeline_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # The Function 2 package this application was submitted from. UNIQUE so a second
    # submit of the same package returns the original application (idempotency).
    origin_package_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    # Product label snapshot taken at submit time — keeps F3 decoupled from F2's catalog
    # (the package can later be reset/deleted without affecting the application record).
    product_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    product_label_zh: Mapped[str] = mapped_column(Text, nullable=False, default="")
    product_label_en: Mapped[str] = mapped_column(Text, nullable=False, default="")
    scenario_code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    current_node_code: Mapped[str] = mapped_column(String(40), nullable=False)
    # in_progress | rejected | completed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="in_progress")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class TimelineNode(Base):
    __tablename__ = "timeline_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("timeline_applications.id"), nullable=False, index=True
    )
    node_code: Mapped[str] = mapped_column(String(40), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    # pending | in_progress | completed | rejected | supplement_required
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    customer_note_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_note_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Bank-private note: NEVER included in the SME-facing serialization.
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class TimelineAuditEvent(Base):
    __tablename__ = "timeline_audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    application_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Independent metadata for Function 7.

    Function 7 aggregates other services through HTTP, but owns only dashboard-native
    rows such as policy bookmarks and export audit events.
    """


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PolicyBookmark(Base):
    __tablename__ = "policy_bookmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_title: Mapped[str] = mapped_column(String(240), nullable=False, default="")
    snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    document_type: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    trust_tier: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    origin_chat_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class DashboardExportEvent(Base):
    __tablename__ = "dashboard_export_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sme_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    export_type: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

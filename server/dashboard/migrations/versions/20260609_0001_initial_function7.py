"""initial function7 dashboard

Revision ID: 20260609_0001
Revises: None
Create Date: 2026-06-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260609_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_bookmarks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sme_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_title", sa.String(length=240), nullable=False, server_default=""),
        sa.Column("snippet", sa.Text(), nullable=False, server_default=""),
        sa.Column("document_type", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("trust_tier", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("origin_chat_id", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_policy_bookmarks_sme_id"), "policy_bookmarks", ["sme_id"], unique=False
    )

    op.create_table(
        "dashboard_export_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sme_id", sa.String(length=64), nullable=False),
        sa.Column("export_type", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dashboard_export_events_sme_id"),
        "dashboard_export_events",
        ["sme_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_dashboard_export_events_sme_id"), table_name="dashboard_export_events")
    op.drop_table("dashboard_export_events")
    op.drop_index(op.f("ix_policy_bookmarks_sme_id"), table_name="policy_bookmarks")
    op.drop_table("policy_bookmarks")

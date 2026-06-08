"""Add Function 1 saved_drafts (multiple named drafts per SME).

Revision ID: 20260602_0008
Revises: 20260601_0007
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260602_0008"
down_revision = "20260601_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_drafts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("profile_json", sa.Text(), nullable=False),
        sa.Column(
            "selected_product_ids_json", sa.Text(), nullable=False, server_default="[]"
        ),
        sa.Column("matched_snapshot_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("origin_session_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_saved_drafts_sme_id", "saved_drafts", ["sme_id"])


def downgrade() -> None:
    op.drop_index("ix_saved_drafts_sme_id", table_name="saved_drafts")
    op.drop_table("saved_drafts")

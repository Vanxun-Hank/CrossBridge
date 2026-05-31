"""Add official-source loan-product provenance and nullable public terms.

Revision ID: 20260530_0003
Revises: 20260530_0002
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260530_0003"
down_revision = "20260530_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.add_column(
            sa.Column("scenarios_json", sa.Text(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("product_description", sa.Text(), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("source_url", sa.Text(), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("source_title", sa.String(length=240), nullable=False, server_default="")
        )
        batch_op.add_column(sa.Column("source_checked_at", sa.DateTime(timezone=True)))
        batch_op.add_column(
            sa.Column("source_content_hash", sa.String(length=64), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("review_status", sa.String(length=64), nullable=False, server_default="demo_only")
        )
        batch_op.add_column(
            sa.Column("review_notes_json", sa.Text(), nullable=False, server_default="[]")
        )
        batch_op.alter_column(
            "min_requested_amount_hkd",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.alter_column(
            "max_requested_amount_hkd",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.alter_column(
            "min_annual_turnover_hkd",
            existing_type=sa.Integer(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.alter_column(
            "min_annual_turnover_hkd",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.alter_column(
            "max_requested_amount_hkd",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.alter_column(
            "min_requested_amount_hkd",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.drop_column("review_notes_json")
        batch_op.drop_column("review_status")
        batch_op.drop_column("source_content_hash")
        batch_op.drop_column("source_checked_at")
        batch_op.drop_column("source_title")
        batch_op.drop_column("source_url")
        batch_op.drop_column("product_description")
        batch_op.drop_column("scenarios_json")

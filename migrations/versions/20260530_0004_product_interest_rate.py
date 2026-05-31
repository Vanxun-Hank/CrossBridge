"""Add public interest-rate display text to loan products.

Revision ID: 20260530_0004
Revises: 20260530_0003
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260530_0004"
down_revision = "20260530_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "loan_products",
        sa.Column("interest_rate_text", sa.String(length=240), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("loan_products", "interest_rate_text")

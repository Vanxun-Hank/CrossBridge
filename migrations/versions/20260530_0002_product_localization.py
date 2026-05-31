"""Add localized Function 1 mock product text.

Revision ID: 20260530_0002
Revises: 20260530_0001
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260530_0002"
down_revision = "20260530_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "loan_products",
        sa.Column("localization_json", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("loan_products", "localization_json")


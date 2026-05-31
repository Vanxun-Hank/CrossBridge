"""Persist the preferred response language for Function 1 sessions.

Revision ID: 20260601_0007
Revises: 20260531_0006
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260601_0007"
down_revision = "20260531_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("matching_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("response_language", sa.String(length=2), nullable=False, server_default="zh")
        )


def downgrade() -> None:
    with op.batch_alter_table("matching_sessions") as batch_op:
        batch_op.drop_column("response_language")

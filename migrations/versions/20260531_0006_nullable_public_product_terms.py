"""Keep unpublished public product terms as null.

Revision ID: 20260531_0006
Revises: 20260531_0005
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260531_0006"
down_revision = "20260531_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.alter_column("loan_limit_text", existing_type=sa.String(length=200), nullable=True)
        batch_op.alter_column("interest_rate_text", existing_type=sa.String(length=240), nullable=True)
        batch_op.alter_column("tenor_text", existing_type=sa.String(length=200), nullable=True)
        batch_op.alter_column("repayment_method_text", existing_type=sa.String(length=200), nullable=True)
        batch_op.alter_column("fee_text", existing_type=sa.String(length=240), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.alter_column("fee_text", existing_type=sa.String(length=240), nullable=False, server_default="")
        batch_op.alter_column("repayment_method_text", existing_type=sa.String(length=200), nullable=False, server_default="")
        batch_op.alter_column("tenor_text", existing_type=sa.String(length=200), nullable=False, server_default="")
        batch_op.alter_column("interest_rate_text", existing_type=sa.String(length=240), nullable=False, server_default="")
        batch_op.alter_column("loan_limit_text", existing_type=sa.String(length=200), nullable=False, server_default="")

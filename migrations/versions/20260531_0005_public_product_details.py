"""Add public product guidance, document hints, fees and source references.

Revision ID: 20260531_0005
Revises: 20260530_0004
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260531_0005"
down_revision = "20260530_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.add_column(
            sa.Column("fee_text", sa.String(length=240), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("public_guidance_json", sa.Text(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("required_documents_json", sa.Text(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("source_refs_json", sa.Text(), nullable=False, server_default="[]")
        )


def downgrade() -> None:
    with op.batch_alter_table("loan_products") as batch_op:
        batch_op.drop_column("source_refs_json")
        batch_op.drop_column("required_documents_json")
        batch_op.drop_column("public_guidance_json")
        batch_op.drop_column("fee_text")

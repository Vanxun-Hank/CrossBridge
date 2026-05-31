"""Add Function 2 document-preparation tables.

Revision ID: 20260531_f2_0001
Revises:
Create Date: 2026-05-31
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260531_f2_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_packages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("scenario_code", sa.String(length=64), nullable=False),
        sa.Column("selected_product_id", sa.String(length=64), nullable=True),
        sa.Column("origin_matching_session_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "document_checklist_states",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("package_id", sa.String(length=36), sa.ForeignKey("document_packages.id"), nullable=False, index=True),
        sa.Column("item_code", sa.String(length=80), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "document_template_drafts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("package_id", sa.String(length=36), sa.ForeignKey("document_packages.id"), nullable=False, index=True),
        sa.Column("template_code", sa.String(length=80), nullable=False),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "document_audit_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("package_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("document_audit_events")
    op.drop_table("document_template_drafts")
    op.drop_table("document_checklist_states")
    op.drop_table("document_packages")

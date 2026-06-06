"""Add Function 3 application-timeline tables.

Revision ID: 20260605_f3_0001
Revises:
Create Date: 2026-06-05
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260605_f3_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "timeline_applications",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False, index=True),
        # UNIQUE: a second submit of the same F2 package returns the original application.
        sa.Column(
            "origin_package_id",
            sa.String(length=64),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("product_id", sa.String(length=64), nullable=True),
        sa.Column("product_label_zh", sa.Text(), nullable=False),
        sa.Column("product_label_en", sa.Text(), nullable=False),
        sa.Column("scenario_code", sa.String(length=64), nullable=False),
        sa.Column("current_node_code", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "timeline_nodes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "application_id",
            sa.String(length=36),
            sa.ForeignKey("timeline_applications.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("node_code", sa.String(length=40), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("customer_note_zh", sa.Text(), nullable=True),
        sa.Column("customer_note_en", sa.Text(), nullable=True),
        sa.Column("internal_note", sa.Text(), nullable=True),
        sa.Column("reminder_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "timeline_audit_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("application_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("timeline_audit_events")
    op.drop_table("timeline_nodes")
    op.drop_table("timeline_applications")

"""Add Function 1 loan-matching tables.

Revision ID: 20260530_0001
Revises:
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260530_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sme_profiles",
        sa.Column("sme_id", sa.String(length=64), primary_key=True),
        sa.Column("profile_json", sa.Text(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "matching_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("draft_profile_json", sa.Text(), nullable=False),
        sa.Column("clarification_count", sa.Integer(), nullable=False),
        sa.Column("current_question", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_matching_sessions_sme_id", "matching_sessions", ["sme_id"])
    op.create_table(
        "loan_products",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("product_name", sa.String(length=160), nullable=False),
        sa.Column("business_scenario", sa.String(length=64), nullable=False),
        sa.Column("purposes_json", sa.Text(), nullable=False),
        sa.Column("min_requested_amount_hkd", sa.Integer(), nullable=False),
        sa.Column("max_requested_amount_hkd", sa.Integer(), nullable=False),
        sa.Column("min_annual_turnover_hkd", sa.Integer(), nullable=False),
        sa.Column("loan_limit_text", sa.String(length=200), nullable=False),
        sa.Column("tenor_text", sa.String(length=200), nullable=False),
        sa.Column("repayment_method_text", sa.String(length=200), nullable=False),
        sa.Column("application_thresholds_json", sa.Text(), nullable=False),
        sa.Column("demo_only", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_loan_products_business_scenario", "loan_products", ["business_scenario"])
    op.create_table(
        "match_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("reasons_json", sa.Text(), nullable=False),
        sa.Column("product_snapshot_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["matching_sessions.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["loan_products.id"]),
    )
    op.create_index("ix_match_results_session_id", "match_results", ["session_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["matching_sessions.id"]),
    )
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_session_id", "audit_events", ["session_id"])
    op.create_index("ix_audit_events_sme_id", "audit_events", ["sme_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("match_results")
    op.drop_table("loan_products")
    op.drop_table("matching_sessions")
    op.drop_table("sme_profiles")


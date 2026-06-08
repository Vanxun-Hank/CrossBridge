"""Add Function 2 official-form drafts and trade-terms acceptance tables.

Revision ID: 20260601_f2_0003
Revises: 20260531_f2_0002
Create Date: 2026-06-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260601_f2_0003"
down_revision = "20260531_f2_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_official_form_drafts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "package_id",
            sa.String(length=36),
            sa.ForeignKey("document_packages.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("form_id", sa.String(length=80), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("values_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "uq_document_official_form_drafts_pkg_form_sha",
        "document_official_form_drafts",
        ["package_id", "form_id", "source_sha256"],
        unique=True,
    )

    op.create_table(
        "document_trade_terms_acceptances",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sme_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("terms_sha256", sa.String(length=64), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("terms_url", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
    )
    op.create_index(
        "uq_document_trade_terms_acceptances_sme_sha",
        "document_trade_terms_acceptances",
        ["sme_id", "terms_sha256"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_document_trade_terms_acceptances_sme_sha",
        table_name="document_trade_terms_acceptances",
    )
    op.drop_table("document_trade_terms_acceptances")
    op.drop_index(
        "uq_document_official_form_drafts_pkg_form_sha",
        table_name="document_official_form_drafts",
    )
    op.drop_table("document_official_form_drafts")

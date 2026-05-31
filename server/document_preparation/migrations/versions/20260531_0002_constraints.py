"""Add Function 2 package uniqueness and snapshot versioning.

Revision ID: 20260531_f2_0002
Revises: 20260531_f2_0001
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa


revision = "20260531_f2_0002"
down_revision = "20260531_f2_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "document_packages",
        sa.Column("catalog_version", sa.String(length=128), nullable=False, server_default="unknown"),
    )
    op.create_index(
        "uq_document_packages_sme_scenario",
        "document_packages",
        ["sme_id", "scenario_code"],
        unique=True,
    )
    op.create_index(
        "uq_document_checklist_states_package_item",
        "document_checklist_states",
        ["package_id", "item_code"],
        unique=True,
    )
    op.create_index(
        "uq_document_template_drafts_package_template",
        "document_template_drafts",
        ["package_id", "template_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_document_template_drafts_package_template", table_name="document_template_drafts")
    op.drop_index("uq_document_checklist_states_package_item", table_name="document_checklist_states")
    op.drop_index("uq_document_packages_sme_scenario", table_name="document_packages")
    op.drop_column("document_packages", "catalog_version")

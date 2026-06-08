"""Link document packages one-to-one to Function 1 saved drafts.

Adds document_packages.saved_draft_id and drops the per-(sme_id, scenario_code)
uniqueness so a user can keep one document draft per loan saved draft.

Revision ID: 20260602_f2_0004
Revises: 20260601_f2_0003
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260602_f2_0004"
down_revision = "20260601_f2_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("document_packages") as batch_op:
        batch_op.add_column(sa.Column("saved_draft_id", sa.String(length=36), nullable=True))
    op.drop_index("uq_document_packages_sme_scenario", table_name="document_packages")
    op.create_index(
        "ix_document_packages_saved_draft", "document_packages", ["saved_draft_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_document_packages_saved_draft", table_name="document_packages")
    op.create_index(
        "uq_document_packages_sme_scenario",
        "document_packages",
        ["sme_id", "scenario_code"],
        unique=True,
    )
    with op.batch_alter_table("document_packages") as batch_op:
        batch_op.drop_column("saved_draft_id")

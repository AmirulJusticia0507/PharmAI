"""add BPOM source identity

Revision ID: d91e4a706b52
Revises: b67c2a103d4e
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d91e4a706b52"
down_revision: Union[str, Sequence[str], None] = "b67c2a103d4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drugs", sa.Column("source_product_id", sa.String(length=100), nullable=True))
    op.add_column("drugs", sa.Column("source_application_id", sa.String(length=50), nullable=True))
    op.create_unique_constraint(
        "uq_drugs_bpom_source",
        "drugs",
        ["source_product_id", "source_application_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_drugs_bpom_source", "drugs", type_="unique")
    op.drop_column("drugs", "source_application_id")
    op.drop_column("drugs", "source_product_id")

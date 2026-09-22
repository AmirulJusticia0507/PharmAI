"""add drug regulatory fields

Revision ID: 8f3149d8c210
Revises: 002e006f26ca
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f3149d8c210"
down_revision: Union[str, Sequence[str], None] = "002e006f26ca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drugs", sa.Column("active_ingredients", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("drugs", sa.Column("registration_number", sa.String(length=100), nullable=True))
    op.add_column("drugs", sa.Column("registration_status", sa.String(length=30), server_default="unverified", nullable=False))
    op.add_column("drugs", sa.Column("registration_expires_at", sa.Date(), nullable=True))
    op.add_column("drugs", sa.Column("regulatory_source_url", sa.String(length=1000), nullable=True))
    op.add_column("drugs", sa.Column("regulatory_checked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("drugs", sa.Column("regulatory_notes", sa.Text(), nullable=True))
    op.create_index("ix_drugs_registration_number", "drugs", ["registration_number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_drugs_registration_number", table_name="drugs")
    op.drop_column("drugs", "regulatory_notes")
    op.drop_column("drugs", "regulatory_checked_at")
    op.drop_column("drugs", "regulatory_source_url")
    op.drop_column("drugs", "registration_expires_at")
    op.drop_column("drugs", "registration_status")
    op.drop_column("drugs", "registration_number")
    op.drop_column("drugs", "active_ingredients")

"""add usage guidance fields (indication, benefit, dosage, usage_time, frequency)

Revision ID: a3f1c9d24b7e
Revises: d91e4a706b52
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3f1c9d24b7e"
down_revision: Union[str, Sequence[str], None] = "d91e4a706b52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drugs", sa.Column("indication", sa.Text(), nullable=True))
    op.add_column("drugs", sa.Column("benefit", sa.Text(), nullable=True))
    op.add_column("drugs", sa.Column("dosage", sa.Text(), nullable=True))
    op.add_column("drugs", sa.Column("usage_time", sa.JSON(), nullable=True))
    op.add_column("drugs", sa.Column("frequency", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("drugs", "frequency")
    op.drop_column("drugs", "usage_time")
    op.drop_column("drugs", "dosage")
    op.drop_column("drugs", "benefit")
    op.drop_column("drugs", "indication")

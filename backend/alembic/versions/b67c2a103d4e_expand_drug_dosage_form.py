"""expand drug dosage form

Revision ID: b67c2a103d4e
Revises: 8f3149d8c210
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b67c2a103d4e"
down_revision: Union[str, Sequence[str], None] = "8f3149d8c210"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "drugs",
        "dosage_form",
        existing_type=sa.String(length=100),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "drugs",
        "dosage_form",
        existing_type=sa.String(length=500),
        type_=sa.String(length=100),
        existing_nullable=True,
    )

"""Expand image_url for generated image data URLs.

Revision ID: c41b6e2d7f90
Revises: f6b8e7c42a10
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c41b6e2d7f90"
down_revision: str | Sequence[str] | None = "f6b8e7c42a10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "drugs",
        "image_url",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "drugs",
        "image_url",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )

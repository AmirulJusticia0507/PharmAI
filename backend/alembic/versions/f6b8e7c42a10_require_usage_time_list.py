"""require usage_time to be a list

Revision ID: f6b8e7c42a10
Revises: a3f1c9d24b7e
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6b8e7c42a10"
down_revision: Union[str, Sequence[str], None] = "a3f1c9d24b7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE drugs SET usage_time = '[]'::json WHERE usage_time IS NULL")
    op.alter_column(
        "drugs",
        "usage_time",
        existing_type=sa.JSON(),
        server_default=sa.text("'[]'::json"),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "drugs",
        "usage_time",
        existing_type=sa.JSON(),
        server_default=None,
        nullable=True,
    )

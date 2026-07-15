"""add timestamp defaults to dividend tables

Revision ID: 20260714_0002
Revises: 20260714_0001
Create Date: 2026-07-14 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0002"
down_revision: Union[str, None] = "20260714_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table_name in ("dividends", "corporate_actions"):
        op.alter_column(table_name, "created_at", server_default=sa.func.now(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        op.alter_column(table_name, "updated_at", server_default=sa.func.now(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)


def downgrade() -> None:
    for table_name in ("dividends", "corporate_actions"):
        op.alter_column(table_name, "updated_at", server_default=None, existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        op.alter_column(table_name, "created_at", server_default=None, existing_type=sa.DateTime(timezone=True), existing_nullable=False)

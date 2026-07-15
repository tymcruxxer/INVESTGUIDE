"""create market snapshots table

Revision ID: 20260715_0002
Revises: 20260715_0001
Create Date: 2026-07-15 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0002"
down_revision: Union[str, None] = "20260715_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("exchange", sa.String(length=20), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(18, 6), nullable=True),
        sa.Column("open_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("high_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("low_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("close_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("volume", sa.Numeric(24, 2), nullable=True),
        sa.Column("market_cap", sa.Numeric(24, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_market_snapshots_asset_id_assets"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_market_snapshots")),
        sa.UniqueConstraint("asset_id", "snapshot_date", "source_type", name="uq_market_snapshots_asset_date_source"),
    )
    op.create_index("ix_market_snapshots_asset_id", "market_snapshots", ["asset_id"])
    op.create_index("ix_market_snapshots_is_development_data", "market_snapshots", ["is_development_data"])
    op.create_index("ix_market_snapshots_snapshot_date", "market_snapshots", ["snapshot_date"])


def downgrade() -> None:
    op.drop_index("ix_market_snapshots_snapshot_date", table_name="market_snapshots")
    op.drop_index("ix_market_snapshots_is_development_data", table_name="market_snapshots")
    op.drop_index("ix_market_snapshots_asset_id", table_name="market_snapshots")
    op.drop_table("market_snapshots")

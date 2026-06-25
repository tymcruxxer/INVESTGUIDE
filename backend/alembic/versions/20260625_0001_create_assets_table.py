"""create assets table

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260625_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the assets table and lookup indexes."""
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("exchange", sa.String(length=20), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("official_website", sa.String(length=500), nullable=True),
        sa.Column("market_cap", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("listing_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("exchange IN ('ZSE', 'VFEX')", name="ck_assets_asset_exchange"),
        sa.CheckConstraint(
            "asset_type IN ('equity', 'REIT', 'bond', 'money_market', 'alternative')",
            name="ck_assets_asset_type",
        ),
        sa.CheckConstraint("currency IN ('ZWG', 'USD')", name="ck_assets_asset_currency"),
        sa.CheckConstraint(
            "status IN ('active', 'suspended', 'delisted')",
            name="ck_assets_asset_status",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_assets"),
        sa.UniqueConstraint("ticker", name="uq_assets_ticker"),
    )
    op.create_index("ix_assets_ticker", "assets", ["ticker"], unique=False)
    op.create_index("ix_assets_exchange", "assets", ["exchange"], unique=False)
    op.create_index("ix_assets_sector", "assets", ["sector"], unique=False)
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"], unique=False)


def downgrade() -> None:
    """Drop the assets table and lookup indexes."""
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_index("ix_assets_sector", table_name="assets")
    op.drop_index("ix_assets_exchange", table_name="assets")
    op.drop_index("ix_assets_ticker", table_name="assets")
    op.drop_table("assets")
"""create dividends and corporate actions tables

Revision ID: 20260714_0001
Revises: 20260713_0002
Create Date: 2026-07-14 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0001"
down_revision: Union[str, None] = "20260713_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dividends",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=True),
        sa.Column("announcement_date", sa.Date(), nullable=True),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("ex_dividend_date", sa.Date(), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("dividend_type", sa.Enum("Interim", "Final", "Special", "Other", name="dividend_type", native_enum=False, length=20), server_default="Other", nullable=False),
        sa.Column("dividend_per_share", sa.Numeric(18, 6), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("shares_outstanding", sa.Numeric(24, 2), nullable=True),
        sa.Column("total_dividend_amount", sa.Numeric(24, 2), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name="fk_dividends_asset_id_assets", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_dividends_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_dividends"),
        sa.UniqueConstraint("company_id", "asset_id", "fiscal_year", "dividend_type", "announcement_date", name="uq_dividends_company_asset_year_type_announcement"),
    )
    op.create_index("ix_dividends_asset_id", "dividends", ["asset_id"], unique=False)
    op.create_index("ix_dividends_company_id", "dividends", ["company_id"], unique=False)
    op.create_index("ix_dividends_fiscal_year", "dividends", ["fiscal_year"], unique=False)
    op.create_index("ix_dividends_is_development_data", "dividends", ["is_development_data"], unique=False)

    op.create_table(
        "corporate_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=True),
        sa.Column("action_type", sa.Enum("dividend", "split", "rights_issue", "consolidation", "other", name="corporate_action_type", native_enum=False, length=50), server_default="other", nullable=False),
        sa.Column("announcement_date", sa.Date(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name="fk_corporate_actions_asset_id_assets", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_corporate_actions_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_corporate_actions"),
        sa.UniqueConstraint("company_id", "asset_id", "action_type", "announcement_date", name="uq_corporate_actions_company_asset_type_announcement"),
    )
    op.create_index("ix_corporate_actions_action_type", "corporate_actions", ["action_type"], unique=False)
    op.create_index("ix_corporate_actions_asset_id", "corporate_actions", ["asset_id"], unique=False)
    op.create_index("ix_corporate_actions_company_id", "corporate_actions", ["company_id"], unique=False)
    op.create_index("ix_corporate_actions_is_development_data", "corporate_actions", ["is_development_data"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_corporate_actions_is_development_data", table_name="corporate_actions")
    op.drop_index("ix_corporate_actions_company_id", table_name="corporate_actions")
    op.drop_index("ix_corporate_actions_asset_id", table_name="corporate_actions")
    op.drop_index("ix_corporate_actions_action_type", table_name="corporate_actions")
    op.drop_table("corporate_actions")
    op.drop_index("ix_dividends_is_development_data", table_name="dividends")
    op.drop_index("ix_dividends_fiscal_year", table_name="dividends")
    op.drop_index("ix_dividends_company_id", table_name="dividends")
    op.drop_index("ix_dividends_asset_id", table_name="dividends")
    op.drop_table("dividends")


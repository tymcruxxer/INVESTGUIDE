"""Create macro indicators table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260715_0004"
down_revision = "20260715_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "macro_indicators",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("indicator_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Numeric(18, 6), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("reporting_period", sa.Date(), nullable=False),
        sa.Column("country", sa.String(length=100), server_default="Zimbabwe", nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("commodity", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=True),
        sa.Column("dataset_version", sa.String(length=100), nullable=True),
        sa.Column("external_key", sa.String(length=128), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "indicator_type IN ('inflation', 'interest_rate', 'exchange_rate', 'gdp', 'commodity_price')",
            name="ck_macro_indicators_indicator_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "indicator_type",
            "name",
            "reporting_period",
            "country",
            "currency",
            "source_type",
            name="uq_macro_indicator_identity",
        ),
    )
    op.create_index("ix_macro_indicators_type", "macro_indicators", ["indicator_type"])
    op.create_index("ix_macro_indicators_period", "macro_indicators", ["reporting_period"])
    op.create_index("ix_macro_indicators_country", "macro_indicators", ["country"])
    op.create_index("ix_macro_indicators_currency", "macro_indicators", ["currency"])
    op.create_index("ix_macro_indicators_is_development_data", "macro_indicators", ["is_development_data"])


def downgrade() -> None:
    op.drop_index("ix_macro_indicators_is_development_data", table_name="macro_indicators")
    op.drop_index("ix_macro_indicators_currency", table_name="macro_indicators")
    op.drop_index("ix_macro_indicators_country", table_name="macro_indicators")
    op.drop_index("ix_macro_indicators_period", table_name="macro_indicators")
    op.drop_index("ix_macro_indicators_type", table_name="macro_indicators")
    op.drop_table("macro_indicators")

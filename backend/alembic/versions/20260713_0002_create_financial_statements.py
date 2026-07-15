"""create financial statement tables

Revision ID: 20260713_0002
Revises: 20260703_0001
Create Date: 2026-07-13
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260713_0002"
down_revision: str | None = "20260703_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _statement_common_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("period", sa.Enum("annual", "interim", name="statement_period", native_enum=False), server_default="annual", nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "income_statements",
        *_statement_common_columns(),
        sa.Column("revenue", sa.Numeric(18, 2), nullable=True),
        sa.Column("cost_of_sales", sa.Numeric(18, 2), nullable=True),
        sa.Column("gross_profit", sa.Numeric(18, 2), nullable=True),
        sa.Column("operating_profit", sa.Numeric(18, 2), nullable=True),
        sa.Column("profit_before_tax", sa.Numeric(18, 2), nullable=True),
        sa.Column("net_profit", sa.Numeric(18, 2), nullable=True),
        sa.Column("interest_expense", sa.Numeric(18, 2), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_income_statements_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_income_statements"),
        sa.UniqueConstraint("company_id", "fiscal_year", "period", name="uq_income_statements_company_year_period"),
    )
    op.create_index("ix_income_statements_company_id", "income_statements", ["company_id"], unique=False)
    op.create_index("ix_income_statements_fiscal_year", "income_statements", ["fiscal_year"], unique=False)

    op.create_table(
        "balance_sheets",
        *_statement_common_columns(),
        sa.Column("total_assets", sa.Numeric(18, 2), nullable=True),
        sa.Column("current_assets", sa.Numeric(18, 2), nullable=True),
        sa.Column("inventory", sa.Numeric(18, 2), nullable=True),
        sa.Column("cash_and_equivalents", sa.Numeric(18, 2), nullable=True),
        sa.Column("total_liabilities", sa.Numeric(18, 2), nullable=True),
        sa.Column("current_liabilities", sa.Numeric(18, 2), nullable=True),
        sa.Column("total_debt", sa.Numeric(18, 2), nullable=True),
        sa.Column("total_equity", sa.Numeric(18, 2), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_balance_sheets_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_balance_sheets"),
        sa.UniqueConstraint("company_id", "fiscal_year", "period", name="uq_balance_sheets_company_year_period"),
    )
    op.create_index("ix_balance_sheets_company_id", "balance_sheets", ["company_id"], unique=False)
    op.create_index("ix_balance_sheets_fiscal_year", "balance_sheets", ["fiscal_year"], unique=False)

    op.create_table(
        "cash_flow_statements",
        *_statement_common_columns(),
        sa.Column("operating_cash_flow", sa.Numeric(18, 2), nullable=True),
        sa.Column("investing_cash_flow", sa.Numeric(18, 2), nullable=True),
        sa.Column("financing_cash_flow", sa.Numeric(18, 2), nullable=True),
        sa.Column("net_cash_flow", sa.Numeric(18, 2), nullable=True),
        sa.Column("capital_expenditure", sa.Numeric(18, 2), nullable=True),
        sa.Column("free_cash_flow", sa.Numeric(18, 2), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_cash_flow_statements_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_cash_flow_statements"),
        sa.UniqueConstraint("company_id", "fiscal_year", "period", name="uq_cash_flow_statements_company_year_period"),
    )
    op.create_index("ix_cash_flow_statements_company_id", "cash_flow_statements", ["company_id"], unique=False)
    op.create_index("ix_cash_flow_statements_fiscal_year", "cash_flow_statements", ["fiscal_year"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cash_flow_statements_fiscal_year", table_name="cash_flow_statements")
    op.drop_index("ix_cash_flow_statements_company_id", table_name="cash_flow_statements")
    op.drop_table("cash_flow_statements")
    op.drop_index("ix_balance_sheets_fiscal_year", table_name="balance_sheets")
    op.drop_index("ix_balance_sheets_company_id", table_name="balance_sheets")
    op.drop_table("balance_sheets")
    op.drop_index("ix_income_statements_fiscal_year", table_name="income_statements")
    op.drop_index("ix_income_statements_company_id", table_name="income_statements")
    op.drop_table("income_statements")

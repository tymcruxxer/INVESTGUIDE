"""Financial statement SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy constraints."""
    return [member.value for member in enum_class]


class StatementPeriod(StrEnum):
    """Supported statement periods."""

    ANNUAL = "annual"
    INTERIM = "interim"


class FinancialStatementMixin(TimestampMixin):
    """Shared financial statement metadata."""

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[StatementPeriod] = mapped_column(
        Enum(
            StatementPeriod,
            name="statement_period",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=StatementPeriod.ANNUAL,
        server_default=StatementPeriod.ANNUAL.value,
    )
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")


class IncomeStatement(FinancialStatementMixin, Base):
    """Persisted income statement period data."""

    __tablename__ = "income_statements"
    __table_args__ = (
        UniqueConstraint("company_id", "fiscal_year", "period", name="uq_income_statements_company_year_period"),
        Index("ix_income_statements_company_id", "company_id"),
        Index("ix_income_statements_fiscal_year", "fiscal_year"),
    )

    revenue: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    cost_of_sales: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    gross_profit: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    operating_profit: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    profit_before_tax: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    net_profit: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    interest_expense: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    company: Mapped[Company] = relationship("Company", back_populates="income_statements")


class BalanceSheet(FinancialStatementMixin, Base):
    """Persisted balance sheet period data."""

    __tablename__ = "balance_sheets"
    __table_args__ = (
        UniqueConstraint("company_id", "fiscal_year", "period", name="uq_balance_sheets_company_year_period"),
        Index("ix_balance_sheets_company_id", "company_id"),
        Index("ix_balance_sheets_fiscal_year", "fiscal_year"),
    )

    total_assets: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    current_assets: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    inventory: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    cash_and_equivalents: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_liabilities: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    current_liabilities: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_debt: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_equity: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    company: Mapped[Company] = relationship("Company", back_populates="balance_sheets")


class CashFlowStatement(FinancialStatementMixin, Base):
    """Persisted cash flow statement period data."""

    __tablename__ = "cash_flow_statements"
    __table_args__ = (
        UniqueConstraint("company_id", "fiscal_year", "period", name="uq_cash_flow_statements_company_year_period"),
        Index("ix_cash_flow_statements_company_id", "company_id"),
        Index("ix_cash_flow_statements_fiscal_year", "fiscal_year"),
    )

    operating_cash_flow: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    investing_cash_flow: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    financing_cash_flow: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    net_cash_flow: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    capital_expenditure: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    free_cash_flow: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    company: Mapped[Company] = relationship("Company", back_populates="cash_flow_statements")



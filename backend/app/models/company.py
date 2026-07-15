"""Company profile SQLAlchemy model."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.asset import AssetStatus, Currency, Exchange
from app.models.associations import company_news
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.company_profile import CompanyProfile
    from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement
    from app.models.dividend import CorporateAction, Dividend
    from app.models.news import News


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy check constraints."""
    return [member.value for member in enum_class]


class Company(TimestampMixin, Base):
    """Issuer-level knowledge entity sitting above listed assets."""

    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("ticker", name="uq_companies_ticker"),
        Index("ix_companies_ticker", "ticker"),
        Index("ix_companies_exchange", "exchange"),
        Index("ix_companies_sector", "sector"),
        Index("ix_companies_industry", "industry"),
        Index("ix_companies_market", "market"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange: Mapped[Exchange] = mapped_column(
        Enum(
            Exchange,
            name="company_exchange",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
    )
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    market: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[Currency | None] = mapped_column(
        Enum(
            Currency,
            name="company_currency",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=10,
        ),
        nullable=True,
    )
    status: Mapped[AssetStatus] = mapped_column(
        Enum(
            AssetStatus,
            name="company_status",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=AssetStatus.ACTIVE,
        server_default=AssetStatus.ACTIVE.value,
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    assets: Mapped[list[Asset]] = relationship(
        "Asset",
        back_populates="company",
        cascade="save-update",
    )
    news_articles: Mapped[list[News]] = relationship(
        "News",
        secondary=company_news,
        back_populates="companies",
    )
    profile: Mapped[CompanyProfile | None] = relationship(
        "CompanyProfile",
        back_populates="company",
        cascade="all, delete-orphan",
        uselist=False,
    )
    income_statements: Mapped[list[IncomeStatement]] = relationship(
        "IncomeStatement",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    balance_sheets: Mapped[list[BalanceSheet]] = relationship(
        "BalanceSheet",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    cash_flow_statements: Mapped[list[CashFlowStatement]] = relationship(
        "CashFlowStatement",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    dividends: Mapped[list[Dividend]] = relationship(
        "Dividend",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    corporate_actions: Mapped[list[CorporateAction]] = relationship(
        "CorporateAction",
        back_populates="company",
        cascade="all, delete-orphan",
    )



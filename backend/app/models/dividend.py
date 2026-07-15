"""Dividend and corporate-action SQLAlchemy models."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.company import Company


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy constraints."""
    return [member.value for member in enum_class]


class DividendType(StrEnum):
    """Supported dividend classifications."""

    INTERIM = "Interim"
    FINAL = "Final"
    SPECIAL = "Special"
    OTHER = "Other"


class CorporateActionType(StrEnum):
    """Supported corporate-action classifications."""

    DIVIDEND = "dividend"
    SPLIT = "split"
    RIGHTS_ISSUE = "rights_issue"
    CONSOLIDATION = "consolidation"
    OTHER = "other"


class Dividend(TimestampMixin, Base):
    """Persisted dividend record with source provenance."""

    __tablename__ = "dividends"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "asset_id",
            "fiscal_year",
            "dividend_type",
            "announcement_date",
            name="uq_dividends_company_asset_year_type_announcement",
        ),
        Index("ix_dividends_company_id", "company_id"),
        Index("ix_dividends_asset_id", "asset_id"),
        Index("ix_dividends_fiscal_year", "fiscal_year"),
        Index("ix_dividends_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    announcement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ex_dividend_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fiscal_year: Mapped[int | None] = mapped_column(nullable=True)
    dividend_type: Mapped[DividendType] = mapped_column(
        Enum(
            DividendType,
            name="dividend_type",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=DividendType.OTHER,
        server_default=DividendType.OTHER.value,
    )
    dividend_per_share: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    shares_outstanding: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    total_dividend_amount: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    company: Mapped[Company] = relationship("Company", back_populates="dividends")
    asset: Mapped[Asset | None] = relationship("Asset", back_populates="dividends")


class CorporateAction(TimestampMixin, Base):
    """Persisted corporate-action record for future verified notices."""

    __tablename__ = "corporate_actions"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "asset_id",
            "action_type",
            "announcement_date",
            name="uq_corporate_actions_company_asset_type_announcement",
        ),
        Index("ix_corporate_actions_company_id", "company_id"),
        Index("ix_corporate_actions_asset_id", "asset_id"),
        Index("ix_corporate_actions_action_type", "action_type"),
        Index("ix_corporate_actions_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    action_type: Mapped[CorporateActionType] = mapped_column(
        Enum(
            CorporateActionType,
            name="corporate_action_type",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=50,
        ),
        nullable=False,
        default=CorporateActionType.OTHER,
        server_default=CorporateActionType.OTHER.value,
    )
    announcement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fiscal_year: Mapped[int | None] = mapped_column(nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    company: Mapped[Company] = relationship("Company", back_populates="corporate_actions")
    asset: Mapped[Asset | None] = relationship("Asset", back_populates="corporate_actions")

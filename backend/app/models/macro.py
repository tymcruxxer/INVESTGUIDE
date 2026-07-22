"""Macroeconomic indicator SQLAlchemy model."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy constraints."""
    return [member.value for member in enum_class]


class MacroIndicatorType(StrEnum):
    """Supported deterministic macro indicator families."""

    INFLATION = "inflation"
    INTEREST_RATE = "interest_rate"
    EXCHANGE_RATE = "exchange_rate"
    GDP = "gdp"
    COMMODITY_PRICE = "commodity_price"


class MacroIndicator(TimestampMixin, Base):
    """Persisted macro record with verification and source provenance."""

    __tablename__ = "macro_indicators"
    __table_args__ = (
        UniqueConstraint(
            "indicator_type",
            "name",
            "reporting_period",
            "country",
            "currency",
            "source_type",
            name="uq_macro_indicator_identity",
        ),
        Index("ix_macro_indicators_type", "indicator_type"),
        Index("ix_macro_indicators_period", "reporting_period"),
        Index("ix_macro_indicators_country", "country"),
        Index("ix_macro_indicators_currency", "currency"),
        Index("ix_macro_indicators_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_type: Mapped[MacroIndicatorType] = mapped_column(
        Enum(
            MacroIndicatorType,
            name="macro_indicator_type",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=50,
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    reporting_period: Mapped[date] = mapped_column(Date, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Zimbabwe", server_default="Zimbabwe")
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    commodity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

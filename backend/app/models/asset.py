"""Investment asset SQLAlchemy model."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.associations import asset_news
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.news import News


class Exchange(StrEnum):
    """Supported Zimbabwean exchanges."""

    ZSE = "ZSE"
    VFEX = "VFEX"


class AssetType(StrEnum):
    """Supported investment asset categories."""

    EQUITY = "equity"
    REIT = "REIT"
    BOND = "bond"
    MONEY_MARKET = "money_market"
    ALTERNATIVE = "alternative"


class Currency(StrEnum):
    """Supported asset currencies."""

    ZWG = "ZWG"
    USD = "USD"


class AssetStatus(StrEnum):
    """Supported asset lifecycle states."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy check constraints."""
    return [member.value for member in enum_class]


class Asset(TimestampMixin, Base):
    """Listed investment asset tracked by InvestGuide."""

    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("ticker", name="uq_assets_ticker"),
        Index("ix_assets_ticker", "ticker"),
        Index("ix_assets_exchange", "exchange"),
        Index("ix_assets_sector", "sector"),
        Index("ix_assets_asset_type", "asset_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[Exchange] = mapped_column(
        Enum(
            Exchange,
            name="asset_exchange",
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
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(
            AssetType,
            name="asset_type",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=50,
        ),
        nullable=False,
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(
            Currency,
            name="asset_currency",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=10,
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    official_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    listing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[AssetStatus] = mapped_column(
        Enum(
            AssetStatus,
            name="asset_status",
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
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company: Mapped[Company | None] = relationship("Company", back_populates="assets")
    news_articles: Mapped[list[News]] = relationship(
        "News",
        secondary=asset_news,
        back_populates="assets",
    )
    dividends: Mapped[list[Dividend]] = relationship("Dividend", back_populates="asset")
    corporate_actions: Mapped[list[CorporateAction]] = relationship("CorporateAction", back_populates="asset")

# Import after class declaration so SQLAlchemy can resolve the relationship target.
from app.models.news import News  # noqa: E402




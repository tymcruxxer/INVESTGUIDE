"""Market snapshot SQLAlchemy model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class MarketSnapshot(TimestampMixin, Base):
    """Persisted market data point with source provenance."""

    __tablename__ = "market_snapshots"
    __table_args__ = (
        UniqueConstraint("asset_id", "snapshot_date", "source_type", name="uq_market_snapshots_asset_date_source"),
        Index("ix_market_snapshots_asset_id", "asset_id"),
        Index("ix_market_snapshots_snapshot_date", "snapshot_date"),
        Index("ix_market_snapshots_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    open_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    high_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    low_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    close_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    volume: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    asset: Mapped[Asset] = relationship("Asset")

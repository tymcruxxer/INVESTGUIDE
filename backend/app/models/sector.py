"""Sector and industry SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin



class Sector(TimestampMixin, Base):
    """Persisted market sector reference data with provenance metadata."""

    __tablename__ = "sectors"
    __table_args__ = (        Index("ix_sectors_slug", "slug"),
        Index("ix_sectors_name", "name"),
        Index("ix_sectors_country", "country"),
        Index("ix_sectors_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exchange_coverage: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Zimbabwe", server_default="Zimbabwe")
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Development", server_default="Development")
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    industries: Mapped[list[Industry]] = relationship(
        "Industry",
        back_populates="sector",
        cascade="all, delete-orphan",
    )


class Industry(TimestampMixin, Base):
    """Persisted industry reference data linked to a parent sector."""

    __tablename__ = "industries"
    __table_args__ = (        Index("ix_industries_slug", "slug"),
        Index("ix_industries_name", "name"),
        Index("ix_industries_sector_id", "sector_id"),
        Index("ix_industries_is_development_data", "is_development_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Development", server_default="Development")
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    sector: Mapped[Sector] = relationship("Sector", back_populates="industries")




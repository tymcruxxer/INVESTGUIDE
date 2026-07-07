"""Company enrichment profile model."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.asset import AssetStatus, Currency, Exchange
from app.models.company import enum_values
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company


class ResearchStatus(StrEnum):
    """Human research/verification status for company profile facts."""

    DEVELOPMENT = "development"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    UNAVAILABLE = "unavailable"


class CompanyProfile(TimestampMixin, Base):
    """Structured, source-transparent enrichment record for a company."""

    __tablename__ = "company_profiles"
    __table_args__ = (
        UniqueConstraint("company_id", name="uq_company_profiles_company_id"),
        Index("ix_company_profiles_company_id", "company_id"),
        Index("ix_company_profiles_research_status", "research_status"),
        Index("ix_company_profiles_last_verified", "last_verified"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    business_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_business: Mapped[str | None] = mapped_column(String(255), nullable=True)
    products_services: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sub_industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exchange: Mapped[Exchange | None] = mapped_column(
        Enum(
            Exchange,
            name="company_profile_exchange",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=True,
    )
    currency: Mapped[Currency | None] = mapped_column(
        Enum(
            Currency,
            name="company_profile_currency",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=10,
        ),
        nullable=True,
    )
    employees: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[AssetStatus | None] = mapped_column(
        Enum(
            AssetStatus,
            name="company_profile_status",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=True,
    )
    research_status: Mapped[ResearchStatus] = mapped_column(
        Enum(
            ResearchStatus,
            name="company_profile_research_status",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=ResearchStatus.DEVELOPMENT,
        server_default=ResearchStatus.DEVELOPMENT.value,
    )
    last_verified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    company: Mapped[Company] = relationship("Company", back_populates="profile")
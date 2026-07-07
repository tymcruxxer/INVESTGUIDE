"""Pydantic schemas for company enrichment profiles."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.asset import AssetStatus, Currency, Exchange
from app.models.company_profile import ResearchStatus
from app.schemas.company import CompanyRead


class CompanyProfileBase(BaseModel):
    """Shared company profile enrichment fields."""

    business_summary: str | None = None
    primary_business: str | None = Field(default=None, max_length=255)
    products_services: list[str] = Field(default_factory=list)
    industry: str | None = Field(default=None, max_length=100)
    sub_industry: str | None = Field(default=None, max_length=100)
    headquarters: str | None = Field(default=None, max_length=255)
    founded_year: int | None = Field(default=None, ge=1800, le=2200)
    website: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    exchange: Exchange | None = None
    currency: Currency | None = None
    employees: int | None = Field(default=None, ge=0)
    status: AssetStatus | None = None
    research_status: ResearchStatus = ResearchStatus.DEVELOPMENT
    last_verified: datetime | None = None
    source_name: str | None = Field(default=None, max_length=255)
    source_url: str | None = Field(default=None, max_length=1000)

    @field_validator("products_services", mode="before")
    @classmethod
    def normalize_products_services(cls, value: object) -> list[str]:
        """Normalize nullable database JSON values into a stable list."""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return []


class CompanyProfileRead(CompanyProfileBase):
    """Schema returned for persisted or fixture-backed company profiles."""

    id: int | None = None
    company_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileVerificationRead(BaseModel):
    """Source transparency and verification metadata."""

    last_verified: datetime | None = None
    source_name: str | None = None
    source_url: str | None = None
    research_status: ResearchStatus = ResearchStatus.UNAVAILABLE


class CompanyProfileDetailRead(BaseModel):
    """Company profile endpoint payload."""

    company: CompanyRead
    profile: CompanyProfileRead | None = None
    verification: CompanyProfileVerificationRead
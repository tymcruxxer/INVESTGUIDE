"""Pydantic schemas for the company intelligence domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.asset import AssetStatus, Currency, Exchange
from app.schemas.asset import AssetRead
from app.schemas.news import NewsRead


class CompanyBase(BaseModel):
    """Shared company profile fields."""

    name: str = Field(..., min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    ticker: str = Field(..., min_length=1, max_length=20)
    exchange: Exchange
    sector: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    headquarters: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=500)
    description: str | None = None
    founded_year: int | None = Field(default=None, ge=1800, le=2200)
    employee_count: int | None = Field(default=None, ge=0)
    market: str | None = Field(default=None, max_length=100)
    currency: Currency | None = None
    status: AssetStatus = AssetStatus.ACTIVE
    logo_url: str | None = Field(default=None, max_length=500)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        """Normalize ticker symbols for stable lookups."""
        return value.strip().upper()


class CompanyRead(CompanyBase):
    """Schema returned for persisted company profiles."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyDetailRead(BaseModel):
    """Company detail payload with related intelligence surfaces."""

    company: CompanyRead
    related_assets: list[AssetRead] = Field(default_factory=list)
    latest_news: list[NewsRead] = Field(default_factory=list)
    assessment_available: bool = False
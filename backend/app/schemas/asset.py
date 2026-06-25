"""Pydantic schemas for investment assets."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.asset import AssetStatus, AssetType, Currency, Exchange


class AssetBase(BaseModel):
    """Shared asset fields."""

    ticker: str = Field(..., min_length=1, max_length=20)
    company_name: str = Field(..., min_length=1, max_length=255)
    exchange: Exchange
    sector: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    asset_type: AssetType
    currency: Currency
    description: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)
    official_website: str | None = Field(default=None, max_length=500)
    market_cap: Decimal | None = Field(default=None, ge=0)
    listing_date: date | None = None
    status: AssetStatus = AssetStatus.ACTIVE

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        """Store ticker symbols consistently for future lookups."""
        return value.strip().upper()


class AssetCreate(AssetBase):
    """Schema for creating an asset record."""


class AssetUpdate(BaseModel):
    """Schema for updating an asset record."""

    ticker: str | None = Field(default=None, min_length=1, max_length=20)
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    exchange: Exchange | None = None
    sector: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    asset_type: AssetType | None = None
    currency: Currency | None = None
    description: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)
    official_website: str | None = Field(default=None, max_length=500)
    market_cap: Decimal | None = Field(default=None, ge=0)
    listing_date: date | None = None
    status: AssetStatus | None = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str | None) -> str | None:
        """Store ticker symbols consistently for future lookups."""
        if value is None:
            return value
        return value.strip().upper()


class AssetRead(AssetBase):
    """Schema returned for persisted assets."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
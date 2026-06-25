"""Pydantic schemas for investment news."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NewsBase(BaseModel):
    """Shared news article fields."""

    title: str = Field(..., min_length=1, max_length=500)
    summary: str | None = None
    content: str | None = None
    content_hash: str | None = Field(default=None, min_length=64, max_length=64)
    source: str = Field(..., min_length=1, max_length=150)
    author: str | None = Field(default=None, max_length=150)
    published_at: datetime
    url: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)
    language: str = Field(default="en", min_length=2, max_length=10)
    sentiment: Decimal | None = Field(default=None, ge=-1, le=1)
    relevance_score: Decimal | None = Field(default=None, ge=0, le=1)
    credibility_score: Decimal | None = Field(default=None, ge=0, le=1)
    asset_tickers: list[str] = Field(default_factory=list)

    @field_validator("asset_tickers", mode="before")
    @classmethod
    def normalize_asset_tickers(cls, value: object) -> list[str]:
        """Store related asset tickers consistently for filtering and display."""
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            return [str(ticker).strip().upper() for ticker in value if str(ticker).strip()]
        return value


class NewsCreate(NewsBase):
    """Schema for creating a news article record."""


class NewsRead(NewsBase):
    """Schema returned for persisted news articles."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
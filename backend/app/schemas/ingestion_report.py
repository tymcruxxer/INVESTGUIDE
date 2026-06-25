"""Schemas for internal news ingestion reports."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

IngestionMode = Literal["DRY_RUN", "WRITE"]
DuplicateStatus = Literal["NEW", "DUPLICATE", "POSSIBLE_DUPLICATE"]
IngestionArticleStatus = Literal["DRY_RUN", "WRITTEN", "DUPLICATE", "POSSIBLE_DUPLICATE", "FAILED"]


class IngestionArticlePayload(BaseModel):
    """Backend-compatible normalized news article payload."""

    title: str = Field(..., min_length=1, max_length=500)
    source: str = Field(..., min_length=1, max_length=150)
    published_at: datetime
    summary: str | None = None
    content: str | None = None
    url: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)
    author: str | None = Field(default=None, max_length=150)
    language: str = Field(default="en", min_length=2, max_length=10)
    asset_tickers: list[str] = Field(default_factory=list)
    sentiment: Decimal | None = Field(default=None, ge=-1, le=1)
    relevance_score: Decimal | None = Field(default=None, ge=0, le=1)
    credibility_score: Decimal | None = Field(default=None, ge=0, le=1)
    content_hash: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("title", "source", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        """Trim required text fields before validation."""
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("asset_tickers", mode="before")
    @classmethod
    def normalize_asset_tickers(cls, value: object) -> list[str]:
        """Normalize asset tickers into unique uppercase values."""
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            normalized: list[str] = []
            seen: set[str] = set()
            for ticker in value:
                normalized_ticker = str(ticker).strip().upper()
                if normalized_ticker and normalized_ticker not in seen:
                    normalized.append(normalized_ticker)
                    seen.add(normalized_ticker)
            return normalized
        return value


class NewsIngestionRequest(BaseModel):
    """Internal ingestion request for normalized news payloads."""

    articles: list[IngestionArticlePayload] = Field(..., min_length=1)
    mode: IngestionMode | None = None

    @field_validator("mode", mode="before")
    @classmethod
    def normalize_mode(cls, value: object) -> object:
        """Allow request mode overrides to be case-insensitive."""
        if isinstance(value, str):
            return value.strip().upper()
        return value


class IngestionArticleResult(BaseModel):
    """Per-article ingestion result."""

    title: str | None = None
    source: str | None = None
    url: str | None = None
    status: IngestionArticleStatus
    duplicate_status: DuplicateStatus | None = None
    news_id: int | None = None
    asset_tickers: list[str] = Field(default_factory=list)
    assets_linked: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class IngestionReport(BaseModel):
    """Summary returned by the internal ingestion adapter."""

    articles_received: int
    articles_written: int
    duplicates_skipped: int
    failed_articles: int
    assets_linked: int
    execution_time: float
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    mode: IngestionMode
    results: list[IngestionArticleResult] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
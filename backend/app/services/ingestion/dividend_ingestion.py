"""Dividend ingestion contracts for future verified sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.services.ingestion.base import IngestionAdapter, IngestionResult, SourceVerification


@dataclass(frozen=True)
class DividendIngestionPayload:
    """Normalized dividend input compatible with future verified imports."""

    ticker: str
    fiscal_year: int | None
    dividend_type: str
    source: SourceVerification
    announcement_date: date | None = None
    record_date: date | None = None
    ex_dividend_date: date | None = None
    payment_date: date | None = None
    dividend_per_share: float | None = None
    currency: str | None = None
    shares_outstanding: float | None = None
    total_dividend_amount: float | None = None
    source_document_date: date | None = None
    upsert_key: str | None = None
    validation_errors: list[str] = field(default_factory=list)
    raw_payload: dict[str, Any] = field(default_factory=dict)


class DividendIngestionService:
    """Contract for future dividend imports; live connectors are intentionally absent."""

    def __init__(self, adapter: IngestionAdapter[DividendIngestionPayload]) -> None:
        self.adapter = adapter

    def upsert_dividends(self, payloads: list[DividendIngestionPayload]) -> IngestionResult:
        """Persist normalized dividends when a verified adapter exists."""
        raise NotImplementedError("Verified dividend persistence adapters will be implemented in a future sprint.")

"""Market data ingestion contract for future verified market sources."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.base import SourceVerification


@dataclass(frozen=True)
class MarketDataIngestionPayload:
    """Normalized market data upsert payload."""

    ticker: str
    exchange: str
    values: dict[str, float | int | str | None]
    source: SourceVerification


class MarketIngestionService:
    """Contract placeholder for verified market data upserts."""

    def upsert_market_data(self, payload: MarketDataIngestionPayload) -> None:
        """Persist verified market data in a future sprint."""
        raise NotImplementedError("Verified market data ingestion is not implemented yet.")

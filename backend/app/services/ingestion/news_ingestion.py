"""News ingestion contract for future verified news/source adapters."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.base import SourceVerification


@dataclass(frozen=True)
class NewsIngestionPayload:
    """Normalized news article upsert payload."""

    title: str
    source_name: str
    published_at: str
    source: SourceVerification
    url: str | None = None
    summary: str | None = None
    content: str | None = None
    related_tickers: tuple[str, ...] = ()


class NewsIngestionService:
    """Contract placeholder for verified news upserts."""

    def upsert_news(self, payload: NewsIngestionPayload) -> None:
        """Persist verified news in a future sprint."""
        raise NotImplementedError("Verified news ingestion is not implemented yet.")

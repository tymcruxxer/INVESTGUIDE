"""Company ingestion contract for future verified source adapters."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.base import SourceVerification


@dataclass(frozen=True)
class CompanyIngestionPayload:
    """Normalized company upsert payload."""

    ticker: str
    name: str
    exchange: str
    source: SourceVerification
    legal_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    website: str | None = None


class CompanyIngestionService:
    """Contract placeholder for verified company upserts."""

    def upsert_company(self, payload: CompanyIngestionPayload) -> None:
        """Persist a verified company payload in a future sprint."""
        raise NotImplementedError("Verified company ingestion is not implemented yet.")

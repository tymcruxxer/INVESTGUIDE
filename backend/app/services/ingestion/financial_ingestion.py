"""Financial statement ingestion contract for future verified filings."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.base import SourceVerification


@dataclass(frozen=True)
class FinancialStatementIngestionPayload:
    """Normalized financial statement upsert payload."""

    ticker: str
    fiscal_year: int
    period: str
    statement_type: str
    values: dict[str, float | str | None]
    source: SourceVerification


class FinancialIngestionService:
    """Contract placeholder for verified financial statement upserts."""

    def upsert_financial_statement(self, payload: FinancialStatementIngestionPayload) -> None:
        """Persist a verified financial statement payload in a future sprint."""
        raise NotImplementedError("Verified financial statement ingestion is not implemented yet.")

"""Corporate-action ingestion contracts for future verified notices."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.services.ingestion.base import IngestionAdapter, IngestionResult, SourceVerification


@dataclass(frozen=True)
class CorporateActionIngestionPayload:
    """Normalized corporate-action input for future ZSE/VFEX/manual imports."""

    ticker: str
    action_type: str
    source: SourceVerification
    announcement_date: date | None = None
    effective_date: date | None = None
    fiscal_year: int | None = None
    title: str | None = None
    description: str | None = None
    source_document_date: date | None = None
    upsert_key: str | None = None
    validation_errors: list[str] = field(default_factory=list)
    raw_payload: dict[str, Any] = field(default_factory=dict)


class CorporateActionIngestionService:
    """Contract for future corporate-action imports; no live source calls are made."""

    def __init__(self, adapter: IngestionAdapter[CorporateActionIngestionPayload]) -> None:
        self.adapter = adapter

    def upsert_corporate_actions(self, payloads: list[CorporateActionIngestionPayload]) -> IngestionResult:
        """Persist normalized corporate actions when a verified adapter exists."""
        raise NotImplementedError("Verified corporate-action persistence adapters will be implemented in a future sprint.")

"""Compatibility contracts and public ingestion pipeline exports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Protocol, TypeVar

from app.services.ingestion.pipeline import IngestionPipeline, SourceAdapter
from app.services.ingestion.types import (
    EntityType,
    ImportResult,
    IngestionMode,
    LoadedDataset,
    PipelineResult,
    SourceMetadata,
    SourceType,
    ValidationIssue,
    ValidationResult,
    VerificationStatus,
)

T = TypeVar("T")


@dataclass(frozen=True)
class SourceVerification:
    """Legacy source metadata required for verified imported records."""

    source_name: str
    source_type: str
    source_url: str | None = None
    imported_at: datetime | None = None
    verified_at: datetime | None = None
    is_development_data: bool = False


@dataclass(frozen=True)
class IngestionResult:
    """Legacy result for earlier ingestion adapter contracts."""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


class IngestionAdapter(Protocol, Generic[T]):
    """Legacy protocol implemented by future source-specific adapters."""

    source: SourceVerification

    def normalize(self, payload: Any) -> dict[str, Any]:
        """Normalize source payload into existing backend model fields."""

    def validate(self, payload: dict[str, Any]) -> None:
        """Validate normalized payload before persistence."""


__all__ = [
    "EntityType",
    "ImportResult",
    "IngestionAdapter",
    "IngestionMode",
    "IngestionPipeline",
    "IngestionResult",
    "LoadedDataset",
    "PipelineResult",
    "SourceAdapter",
    "SourceMetadata",
    "SourceType",
    "SourceVerification",
    "ValidationIssue",
    "ValidationResult",
    "VerificationStatus",
]

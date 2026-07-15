"""Verified data ingestion framework."""

from app.services.ingestion.base import (
    EntityType,
    ImportResult,
    IngestionMode,
    IngestionPipeline,
    PipelineResult,
    SourceMetadata,
    SourceType,
    VerificationStatus,
)
from app.services.ingestion.corporate_action_ingestion import CorporateActionIngestionPayload, CorporateActionIngestionService
from app.services.ingestion.dividend_ingestion import DividendIngestionPayload, DividendIngestionService
from app.services.ingestion.registry import IngestionRegistry, build_default_registry
from app.services.ingestion.types import IssueCode, IssueSeverity

__all__ = [
    "CorporateActionIngestionPayload",
    "CorporateActionIngestionService",
    "DividendIngestionPayload",
    "DividendIngestionService",
    "EntityType",
    "ImportResult",
    "IngestionMode",
    "IngestionPipeline",
    "IssueCode",
    "IssueSeverity",
    "IngestionRegistry",
    "PipelineResult",
    "SourceMetadata",
    "SourceType",
    "VerificationStatus",
    "build_default_registry",
]


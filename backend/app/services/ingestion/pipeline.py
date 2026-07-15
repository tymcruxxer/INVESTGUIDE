"""Source-agnostic ingestion pipeline orchestration."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session

from app.database.development_data_guard import ensure_development_data_allowed
from app.services.ingestion.audit import IngestionAuditRecorder
from app.services.ingestion.types import (
    BaseNormalizedRecord,
    EntityType,
    ImportResult,
    IngestionMode,
    LoadedDataset,
    PipelineResult,
    ValidationResult,
)


class SourceAdapter(Protocol):
    """Protocol implemented by local and future source adapters."""

    def load(self) -> LoadedDataset:
        """Load raw records."""


class Normalizer(Protocol):
    """Protocol implemented by normalizers."""

    def normalize(self, records: list[dict[str, object]], source: object) -> list[BaseNormalizedRecord]:
        """Normalize source records."""


class Validator(Protocol):
    """Protocol implemented by validators."""

    def validate(self, records: list[BaseNormalizedRecord]) -> ValidationResult:
        """Validate normalized records."""


class Importer(Protocol):
    """Protocol implemented by database importers."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        """Import normalized records."""


class IngestionPipeline:
    """Execute source loading, normalization, validation, importing, and audit."""

    def __init__(
        self,
        entity: EntityType,
        source: SourceAdapter,
        normalizer: Normalizer,
        validator: Validator,
        importer: Importer,
        audit_recorder: IngestionAuditRecorder | None = None,
    ) -> None:
        self.entity = entity
        self.source = source
        self.normalizer = normalizer
        self.validator = validator
        self.importer = importer
        self.audit_recorder = audit_recorder or IngestionAuditRecorder()

    def run(self, db: Session, mode: IngestionMode = IngestionMode.DRY_RUN) -> PipelineResult:
        """Run the ingestion pipeline."""
        loaded = self.source.load()
        if loaded.metadata.is_development_data and mode != IngestionMode.DRY_RUN:
            ensure_development_data_allowed()

        run = self.audit_recorder.start_run(db, self.entity, mode, loaded.metadata)
        normalized = self.normalizer.normalize(loaded.records, loaded.metadata)
        validation = self.validator.validate(normalized)

        if mode == IngestionMode.STRICT and validation.rejected_records:
            result = ImportResult(rejected=len(validation.rejected_records), errors=["Strict mode rejected the batch."])
            self.audit_recorder.finish_run(db, run, validation, result, status="rejected", normalized_count=len(normalized))
            return PipelineResult(
                entity=self.entity,
                mode=mode,
                source=loaded.metadata,
                total_records=len(normalized),
                valid_records=len(validation.valid_records),
                rejected_records=len(validation.rejected_records),
                import_result=result,
                run_id=run.id,
            )

        result = self.importer.import_records(db, validation.valid_records, mode)
        status = "failed" if result.errors and result.inserted == 0 and result.updated == 0 else "completed"
        self.audit_recorder.finish_run(db, run, validation, result, status=status, normalized_count=len(normalized))
        return PipelineResult(
            entity=self.entity,
            mode=mode,
            source=loaded.metadata,
            total_records=len(normalized),
            valid_records=len(validation.valid_records),
            rejected_records=len(validation.rejected_records),
            import_result=result,
            run_id=run.id,
        )


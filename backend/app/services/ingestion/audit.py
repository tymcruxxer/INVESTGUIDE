"""Audit helpers for verified data ingestion runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.ingestion import IngestionRecordIssue, IngestionRun
from app.services.ingestion.types import (
    EntityType,
    ImportResult,
    IngestionMode,
    IssueCode,
    SourceMetadata,
    ValidationIssue,
    ValidationResult,
)


def _safe_summary(value: object) -> str | None:
    """Return a concise non-sensitive issue summary."""
    if value is None:
        return None
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    if not text:
        return None
    return text[:500]


def _issue_code(issue: ValidationIssue) -> str:
    """Resolve stable issue code from explicit code or legacy field/message patterns."""
    explicit_code = getattr(issue, "code", None)
    if explicit_code and explicit_code != IssueCode.VALIDATION_ERROR:
        return explicit_code.value if hasattr(explicit_code, "value") else str(explicit_code)
    field = issue.field.lower()
    message = issue.message.lower()
    if "duplicate external" in message:
        return IssueCode.DUPLICATE_EXTERNAL_KEY.value
    if field in {"ticker", "company_ticker", "asset_ticker"}:
        return IssueCode.INVALID_TICKER.value if "required" not in message else IssueCode.MISSING_REQUIRED_FIELD.value
    if field == "exchange":
        return IssueCode.INVALID_EXCHANGE.value
    if field == "currency":
        return IssueCode.INVALID_CURRENCY.value
    if "date" in field:
        return IssueCode.INVALID_DATE.value
    if field == "balance":
        return IssueCode.BALANCE_SHEET_IMBALANCE.value
    if field == "net_cash_flow":
        return IssueCode.CASH_FLOW_MISMATCH.value
    if field in {"price", "open_price", "high_price", "low_price", "close_price"}:
        return IssueCode.INVALID_PRICE_RANGE.value
    if "verified" in field:
        return IssueCode.VERIFICATION_METADATA_MISSING.value
    if "required" in message:
        return IssueCode.MISSING_REQUIRED_FIELD.value
    return IssueCode.VALIDATION_ERROR.value


def _severity(issue: ValidationIssue, rejected: bool = False) -> str:
    if rejected:
        return "Rejected"
    if issue.severity.lower() == "warning":
        return "Warning"
    if issue.severity.lower() == "info":
        return "Info"
    return "Error"


class IngestionAuditRecorder:
    """Persist source-level ingestion run summaries and record-level issues."""

    def start_run(self, db: Session, entity: EntityType, mode: IngestionMode, source: SourceMetadata) -> IngestionRun:
        """Create an audit row at the beginning of a pipeline run."""
        run = IngestionRun(
            entity=entity.value,
            mode=mode.value,
            status="running",
            source_name=source.source_name,
            source_type=source.source_type.value,
            source_url=source.source_url,
            dataset_version=source.dataset_version,
            checksum=source.checksum,
            verification_status=source.verification_status.value,
            is_development_data=source.is_development_data,
            total_records=source.record_count,
            normalized_records=0,
            valid_records=0,
            rejected_records=0,
            inserted=0,
            updated=0,
            skipped=0,
            warning_count=0,
            error_count=0,
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def finish_run(
        self,
        db: Session,
        run: IngestionRun,
        validation: ValidationResult,
        result: ImportResult,
        status: str = "completed",
        normalized_count: int | None = None,
    ) -> IngestionRun:
        """Mark an audit row complete and persist safe record-level issues."""
        run.status = status
        run.normalized_records = normalized_count if normalized_count is not None else len(validation.valid_records) + len(validation.rejected_records)
        run.valid_records = len(validation.valid_records)
        run.rejected_records = len(validation.rejected_records) + result.rejected
        run.inserted = result.inserted
        run.updated = result.updated
        run.skipped = result.skipped
        run.errors = json.dumps(result.errors) if result.errors else None
        warning_messages = [issue.message for issue in validation.warnings] + result.warnings
        run.warnings = json.dumps(warning_messages) if warning_messages else None
        run.warning_count = len(validation.warnings) + len(result.warnings)
        run.error_count = len(result.errors) + sum(len(rejected.issues) for rejected in validation.rejected_records)
        run.finished_at = datetime.now(timezone.utc)

        for issue in validation.warnings:
            self._add_issue(db, run, issue, rejected=False)
        for rejected_record in validation.rejected_records:
            external_key = rejected_record.record.external_key
            for issue in rejected_record.issues:
                self._add_issue(db, run, issue, rejected=True, external_key=external_key)
        for index, warning in enumerate(result.warnings):
            self._add_import_issue(db, run, index, warning, "Warning", IssueCode.IMPORT_WARNING.value)
        for index, error in enumerate(result.errors):
            self._add_import_issue(db, run, index, error, "Error", IssueCode.DATABASE_WRITE_FAILED.value)

        db.commit()
        db.refresh(run)
        return run

    def fail_run(self, db: Session, run: IngestionRun, errors: list[str]) -> IngestionRun:
        """Mark an audit row failed."""
        run.status = "failed"
        run.errors = json.dumps(errors)
        run.error_count = len(errors)
        run.finished_at = datetime.now(timezone.utc)
        for index, error in enumerate(errors):
            self._add_import_issue(db, run, index, error, "Error", IssueCode.DATABASE_WRITE_FAILED.value)
        db.commit()
        db.refresh(run)
        return run

    def _add_issue(
        self,
        db: Session,
        run: IngestionRun,
        issue: ValidationIssue,
        rejected: bool,
        external_key: str | None = None,
    ) -> None:
        db.add(
            IngestionRecordIssue(
                ingestion_run_id=run.id,
                entity_type=run.entity,
                record_index=issue.record_index,
                external_key=external_key,
                severity=_severity(issue, rejected),
                issue_code=_issue_code(issue),
                field_name=issue.field,
                message=issue.message[:1000],
                raw_value_summary=_safe_summary(issue.raw_value_summary),
            )
        )

    def _add_import_issue(self, db: Session, run: IngestionRun, index: int, message: str, severity: str, code: str) -> None:
        db.add(
            IngestionRecordIssue(
                ingestion_run_id=run.id,
                entity_type=run.entity,
                record_index=index,
                severity=severity,
                issue_code=code,
                message=message[:1000],
            )
        )


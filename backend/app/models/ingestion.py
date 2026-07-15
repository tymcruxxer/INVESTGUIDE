"""Ingestion audit SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


class IngestionRun(TimestampMixin, Base):
    """Audit record for a source-agnostic ingestion pipeline execution."""

    __tablename__ = "ingestion_runs"
    __table_args__ = (
        Index("ix_ingestion_runs_entity", "entity"),
        Index("ix_ingestion_runs_source_name", "source_name"),
        Index("ix_ingestion_runs_status", "status"),
        Index("ix_ingestion_runs_started_at", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    mode: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False)
    is_development_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    normalized_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    valid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    rejected_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    issues: Mapped[list["IngestionRecordIssue"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class IngestionRecordIssue(TimestampMixin, Base):
    """Safe record-level validation/import issue linked to an ingestion run."""

    __tablename__ = "ingestion_record_issues"
    __table_args__ = (
        Index("ix_ingestion_record_issues_run_id", "ingestion_run_id"),
        Index("ix_ingestion_record_issues_entity", "entity_type"),
        Index("ix_ingestion_record_issues_severity", "severity"),
        Index("ix_ingestion_record_issues_issue_code", "issue_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    record_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    issue_code: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_value_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)

    run: Mapped[IngestionRun] = relationship(back_populates="issues")

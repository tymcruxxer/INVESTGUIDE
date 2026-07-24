"""Ingestion Operations Centre models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.source_registry import Source
    from app.models.user import User


class IngestionJobType(StrEnum):
    MARKET_PRICES = "market_prices"
    CORPORATE_ACTIONS = "corporate_actions"
    DIVIDENDS = "dividends"
    ANNUAL_REPORTS = "annual_reports"
    INTERIM_REPORTS = "interim_reports"
    TRADING_UPDATES = "trading_updates"
    NEWS = "news"
    ECONOMIC_INDICATORS = "economic_indicators"
    EXCHANGE_RATES = "exchange_rates"
    COMMODITY_PRICES = "commodity_prices"
    WEATHER = "weather"
    RESEARCH_REPORTS = "research_reports"


class IngestionExecutionMode(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    RETRY = "retry"


class IngestionPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class IngestionJobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    DISABLED = "disabled"
    DELETED = "deleted"


class IngestionExecutionStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class IngestionTriggerType(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    RETRY = "retry"
    SYSTEM = "system"


class IngestionFailureCategory(StrEnum):
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PARSING = "parsing"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class IngestionJob(TimestampMixin, Base):
    """Operator-managed ingestion job definition."""

    __tablename__ = "ingestion_jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "name", name="uq_ingestion_jobs_source_id_name"),
        Index("ix_ingestion_jobs_source_id", "source_id"),
        Index("ix_ingestion_jobs_status", "status"),
        Index("ix_ingestion_jobs_job_type", "job_type"),
        Index("ix_ingestion_jobs_priority", "priority"),
        Index("ix_ingestion_jobs_freshness_status", "freshness_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    job_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    execution_mode: Mapped[str] = mapped_column(String(40), nullable=False, default=IngestionExecutionMode.MANUAL.value, server_default=IngestionExecutionMode.MANUAL.value)
    priority: Mapped[str] = mapped_column(String(40), nullable=False, default=IngestionPriority.NORMAL.value, server_default=IngestionPriority.NORMAL.value)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300, server_default="300")
    concurrency_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    queue_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=IngestionJobStatus.PENDING.value, server_default=IngestionJobStatus.PENDING.value)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    manual_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_successful_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_scheduled_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    freshness_status: Mapped[str] = mapped_column(String(40), nullable=False, default=FreshnessStatus.UNKNOWN.value, server_default=FreshnessStatus.UNKNOWN.value)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    source: Mapped["Source"] = relationship("Source")
    executions: Mapped[list["IngestionExecution"]] = relationship(back_populates="job", cascade="all, delete-orphan", order_by="IngestionExecution.id.desc()")
    deleted_by: Mapped["User | None"] = relationship("User", foreign_keys=[deleted_by_user_id])


class IngestionExecution(TimestampMixin, Base):
    """Immutable execution history row for an ingestion job."""

    __tablename__ = "ingestion_executions"
    __table_args__ = (
        Index("ix_ingestion_executions_job_id", "job_id"),
        Index("ix_ingestion_executions_status", "status"),
        Index("ix_ingestion_executions_started_at", "started_at"),
        Index("ix_ingestion_executions_trigger_type", "trigger_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=IngestionExecutionStatus.QUEUED.value, server_default=IngestionExecutionStatus.QUEUED.value)
    trigger_type: Mapped[str] = mapped_column(String(40), nullable=False)
    operator_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    job: Mapped[IngestionJob] = relationship(back_populates="executions")
    operator: Mapped["User | None"] = relationship("User")
    metric: Mapped["ExecutionMetric"] = relationship(back_populates="execution", cascade="all, delete-orphan", uselist=False)
    failures: Mapped[list["ExecutionFailure"]] = relationship(back_populates="execution", cascade="all, delete-orphan")


class ExecutionMetric(TimestampMixin, Base):
    """Operational metrics for one ingestion execution."""

    __tablename__ = "execution_metrics"
    __table_args__ = (UniqueConstraint("execution_id", name="uq_execution_metrics_execution_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("ingestion_executions.id", ondelete="CASCADE"), nullable=False)
    rows_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    records_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    duplicates_detected: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    throughput_per_second: Mapped[float | None] = mapped_column(Float, nullable=True)

    execution: Mapped[IngestionExecution] = relationship(back_populates="metric")


class ExecutionFailure(TimestampMixin, Base):
    """Failure detail for an ingestion execution."""

    __tablename__ = "execution_failures"
    __table_args__ = (
        Index("ix_execution_failures_execution_id", "execution_id"),
        Index("ix_execution_failures_category", "failure_category"),
        Index("ix_execution_failures_failed_at", "failed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("ingestion_executions.id", ondelete="CASCADE"), nullable=False)
    failure_category: Mapped[str] = mapped_column(String(60), nullable=False, default=IngestionFailureCategory.UNKNOWN.value, server_default=IngestionFailureCategory.UNKNOWN.value)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace_placeholder: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    execution: Mapped[IngestionExecution] = relationship(back_populates="failures")

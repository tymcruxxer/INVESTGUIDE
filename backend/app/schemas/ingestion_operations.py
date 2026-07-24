"""Schemas for the Ingestion Operations Centre."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.ingestion_operations import (
    FreshnessStatus,
    IngestionExecutionMode,
    IngestionExecutionStatus,
    IngestionFailureCategory,
    IngestionJobStatus,
    IngestionJobType,
    IngestionPriority,
    IngestionTriggerType,
)

JobTypeValue = Literal[
    "market_prices",
    "corporate_actions",
    "dividends",
    "annual_reports",
    "interim_reports",
    "trading_updates",
    "news",
    "economic_indicators",
    "exchange_rates",
    "commodity_prices",
    "weather",
    "research_reports",
]
ExecutionModeValue = Literal["manual", "scheduled", "event_driven", "retry"]
PriorityValue = Literal["low", "normal", "high", "critical"]
JobStatusValue = Literal["pending", "queued", "running", "completed", "failed", "cancelled", "paused", "disabled", "deleted"]
ExecutionStatusValue = Literal["pending", "queued", "running", "completed", "failed", "cancelled", "paused"]
FailureCategoryValue = Literal["network", "authentication", "parsing", "validation", "rate_limit", "timeout", "internal", "unknown"]
FreshnessStatusValue = Literal["fresh", "aging", "stale", "expired", "unknown"]


class IngestionJobBase(BaseModel):
    source_id: int
    name: str = Field(min_length=2, max_length=160)
    job_type: JobTypeValue
    description: str | None = None
    configuration: dict[str, Any] = Field(default_factory=dict)
    execution_mode: ExecutionModeValue = IngestionExecutionMode.MANUAL.value
    priority: PriorityValue = IngestionPriority.NORMAL.value
    max_retries: int = Field(default=3, ge=0, le=20)
    timeout_seconds: int = Field(default=300, ge=1, le=86400)
    concurrency_limit: int = Field(default=1, ge=1, le=100)
    queue_name: str | None = Field(default=None, max_length=120)
    status: JobStatusValue = IngestionJobStatus.PENDING.value
    is_enabled: bool = False
    manual_only: bool = True
    freshness_status: FreshnessStatusValue = FreshnessStatus.UNKNOWN.value


class IngestionJobCreate(IngestionJobBase):
    reason: str = Field(min_length=3, max_length=1000)


class IngestionJobUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    job_type: JobTypeValue | None = None
    description: str | None = None
    configuration: dict[str, Any] | None = None
    execution_mode: ExecutionModeValue | None = None
    priority: PriorityValue | None = None
    max_retries: int | None = Field(default=None, ge=0, le=20)
    timeout_seconds: int | None = Field(default=None, ge=1, le=86400)
    concurrency_limit: int | None = Field(default=None, ge=1, le=100)
    queue_name: str | None = Field(default=None, max_length=120)
    status: JobStatusValue | None = None
    is_enabled: bool | None = None
    manual_only: bool | None = None
    freshness_status: FreshnessStatusValue | None = None
    reason: str = Field(min_length=3, max_length=1000)


class IngestionOperationRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class ExecutionMetricRead(BaseModel):
    id: int
    rows_processed: int
    records_inserted: int
    records_updated: int
    duplicates_detected: int
    records_rejected: int
    warning_count: int
    error_count: int
    duration_ms: int | None = None
    throughput_per_second: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ExecutionFailureRead(BaseModel):
    id: int
    failure_category: str
    error_message: str
    stack_trace_placeholder: str | None = None
    retry_eligible: bool
    failed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IngestionExecutionRead(BaseModel):
    id: int
    job_id: int
    job_name: str | None = None
    source_name: str | None = None
    status: str
    trigger_type: str
    operator_user_id: int | None = None
    operator_email: str | None = None
    retry_count: int
    result_summary: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = None
    request_id: str | None = None
    metric: ExecutionMetricRead | None = None
    failures: list[ExecutionFailureRead] = Field(default_factory=list)
    created_at: datetime | None = None


class IngestionJobSummary(BaseModel):
    id: int
    source_id: int
    source_name: str
    name: str
    job_type: str
    status: str
    priority: str
    is_enabled: bool
    execution_mode: str
    manual_only: bool
    last_run_at: datetime | None = None
    last_successful_run_at: datetime | None = None
    next_scheduled_run_at: datetime | None = None
    freshness_status: str
    latest_execution_status: str | None = None
    updated_at: datetime | None = None


class IngestionJobRead(IngestionJobSummary):
    description: str | None = None
    configuration: dict[str, Any]
    max_retries: int
    timeout_seconds: int
    concurrency_limit: int
    queue_name: str | None = None
    recent_executions: list[IngestionExecutionRead] = Field(default_factory=list)
    recent_failures: list[ExecutionFailureRead] = Field(default_factory=list)
    audit: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None


class IngestionJobListPayload(BaseModel):
    jobs: list[IngestionJobSummary]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool
    summary: dict[str, int | float | str]


class IngestionExecutionListPayload(BaseModel):
    executions: list[IngestionExecutionRead]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class IngestionMetadataPayload(BaseModel):
    job_types: list[str]
    execution_modes: list[str]
    priorities: list[str]
    job_statuses: list[str]
    execution_statuses: list[str]
    failure_categories: list[str]
    freshness_statuses: list[str]
    trigger_types: list[str]


INGESTION_OPERATION_METADATA = IngestionMetadataPayload(
    job_types=[item.value for item in IngestionJobType],
    execution_modes=[item.value for item in IngestionExecutionMode],
    priorities=[item.value for item in IngestionPriority],
    job_statuses=[item.value for item in IngestionJobStatus if item != IngestionJobStatus.DELETED],
    execution_statuses=[item.value for item in IngestionExecutionStatus],
    failure_categories=[item.value for item in IngestionFailureCategory],
    freshness_statuses=[item.value for item in FreshnessStatus],
    trigger_types=[item.value for item in IngestionTriggerType],
)

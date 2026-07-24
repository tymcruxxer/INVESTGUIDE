"""Service layer for the Ingestion Operations Centre."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.ingestion_operations import (
    ExecutionFailure,
    ExecutionMetric,
    FreshnessStatus,
    IngestionExecution,
    IngestionExecutionStatus,
    IngestionJob,
    IngestionJobStatus,
    IngestionTriggerType,
)
from app.models.source_registry import Source, SourceStatus
from app.models.user import User
from app.schemas.ingestion_operations import (
    ExecutionFailureRead,
    ExecutionMetricRead,
    IngestionExecutionListPayload,
    IngestionExecutionRead,
    IngestionJobCreate,
    IngestionJobListPayload,
    IngestionJobRead,
    IngestionJobSummary,
    IngestionJobUpdate,
    IngestionOperationRequest,
)
from app.services.audit_service import record_audit_event


class IngestionOperationsError(ValueError):
    """Raised when an ingestion operations request is invalid."""

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


@dataclass(frozen=True)
class JobListResult:
    jobs: list[IngestionJob]
    total: int
    page: int
    limit: int


@dataclass(frozen=True)
class ExecutionListResult:
    executions: list[IngestionExecution]
    total: int
    page: int
    limit: int


def list_jobs(
    db: Session,
    *,
    search: str | None = None,
    source_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    job_type: str | None = None,
    freshness_status: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
) -> JobListResult:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(IngestionJob).where(IngestionJob.status != IngestionJobStatus.DELETED.value).options(selectinload(IngestionJob.source), selectinload(IngestionJob.executions))
    if search:
        needle = f"%{search.strip().lower()}%"
        query = query.join(Source).where(or_(func.lower(IngestionJob.name).like(needle), func.lower(Source.display_name).like(needle), func.lower(Source.name).like(needle)))
    if source_id is not None:
        query = query.where(IngestionJob.source_id == source_id)
    if status:
        query = query.where(IngestionJob.status == status)
    if priority:
        query = query.where(IngestionJob.priority == priority)
    if job_type:
        query = query.where(IngestionJob.job_type == job_type)
    if freshness_status:
        query = query.where(IngestionJob.freshness_status == freshness_status)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = {
        "name": IngestionJob.name,
        "status": IngestionJob.status,
        "priority": IngestionJob.priority,
        "freshness_status": IngestionJob.freshness_status,
        "last_run_at": IngestionJob.last_run_at,
        "updated_at": IngestionJob.updated_at,
        "created_at": IngestionJob.created_at,
    }.get(sort_by, IngestionJob.updated_at)
    order = asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)
    jobs = list(db.scalars(query.order_by(order).offset((page - 1) * limit).limit(limit)).unique().all())
    return JobListResult(jobs=jobs, total=total, page=page, limit=limit)


def get_job_or_raise(db: Session, job_id: int, *, include_deleted: bool = False) -> IngestionJob:
    job = db.scalar(
        select(IngestionJob)
        .where(IngestionJob.id == job_id)
        .options(
            selectinload(IngestionJob.source),
            selectinload(IngestionJob.executions).selectinload(IngestionExecution.metric),
            selectinload(IngestionJob.executions).selectinload(IngestionExecution.failures),
            selectinload(IngestionJob.executions).selectinload(IngestionExecution.operator),
        )
    )
    if job is None or (job.status == IngestionJobStatus.DELETED.value and not include_deleted):
        raise IngestionOperationsError("Ingestion job was not found", "INGESTION_JOB_NOT_FOUND", 404)
    return job


def create_job(db: Session, *, actor: User, payload: IngestionJobCreate, request_id: str | None = None, ip_address: str | None = None) -> IngestionJob:
    source = db.get(Source, payload.source_id)
    if source is None or source.status == SourceStatus.DELETED.value:
        raise IngestionOperationsError("Source was not found", "SOURCE_NOT_FOUND", 404)
    job = IngestionJob(
        source_id=payload.source_id,
        name=payload.name,
        job_type=payload.job_type,
        description=payload.description,
        configuration=payload.configuration,
        execution_mode=payload.execution_mode,
        priority=payload.priority,
        max_retries=payload.max_retries,
        timeout_seconds=payload.timeout_seconds,
        concurrency_limit=payload.concurrency_limit,
        queue_name=payload.queue_name,
        status=payload.status,
        is_enabled=payload.is_enabled,
        manual_only=payload.manual_only,
        freshness_status=payload.freshness_status,
    )
    db.add(job)
    db.flush()
    _audit(db, actor, "admin.ingestion.job.create", job, payload.reason, request_id, ip_address, previous=None, new=_job_snapshot(job))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise IngestionOperationsError("A job with this name already exists for this source", "INGESTION_JOB_ALREADY_EXISTS", 409) from exc
    return get_job_or_raise(db, job.id)


def update_job(db: Session, *, actor: User, job: IngestionJob, payload: IngestionJobUpdate, request_id: str | None = None, ip_address: str | None = None) -> IngestionJob:
    previous = _job_snapshot(job)
    for field in ("name", "job_type", "description", "configuration", "execution_mode", "priority", "max_retries", "timeout_seconds", "concurrency_limit", "queue_name", "status", "is_enabled", "manual_only", "freshness_status"):
        value = getattr(payload, field)
        if value is not None:
            setattr(job, field, value)
    db.flush()
    _audit(db, actor, "admin.ingestion.job.update", job, payload.reason, request_id, ip_address, previous=previous, new=_job_snapshot(job))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise IngestionOperationsError("A job with this name already exists for this source", "INGESTION_JOB_ALREADY_EXISTS", 409) from exc
    return get_job_or_raise(db, job.id)


def request_operation(db: Session, *, actor: User, job: IngestionJob, operation: str, payload: IngestionOperationRequest, request_id: str | None = None, ip_address: str | None = None) -> IngestionJob:
    previous = _job_snapshot(job)
    now = datetime.now(UTC)
    trigger = IngestionTriggerType.RETRY.value if operation == "retry" else IngestionTriggerType.MANUAL.value
    execution_status = IngestionExecutionStatus.QUEUED.value
    result_summary = f"{operation.title()} request recorded. No ingestion worker executed in Sprint 055."
    if operation == "pause":
        job.status = IngestionJobStatus.PAUSED.value
        job.is_enabled = False
        execution_status = IngestionExecutionStatus.PAUSED.value
    elif operation == "resume":
        job.status = IngestionJobStatus.PENDING.value
        job.is_enabled = True
    elif operation == "cancel":
        job.status = IngestionJobStatus.CANCELLED.value
        execution_status = IngestionExecutionStatus.CANCELLED.value
    elif operation in {"run", "retry"}:
        job.status = IngestionJobStatus.QUEUED.value
        job.last_run_at = now
    else:
        raise IngestionOperationsError("Unsupported operation", "UNSUPPORTED_OPERATION", 400)

    execution = IngestionExecution(
        job_id=job.id,
        status=execution_status,
        trigger_type=trigger,
        operator_user_id=actor.id,
        retry_count=1 if operation == "retry" else 0,
        result_summary=result_summary,
        started_at=now if operation in {"run", "retry"} else None,
        finished_at=now if operation in {"pause", "cancel"} else None,
        duration_ms=0 if operation in {"pause", "cancel"} else None,
        request_id=request_id,
    )
    db.add(execution)
    db.flush()
    db.add(ExecutionMetric(execution_id=execution.id, duration_ms=execution.duration_ms, throughput_per_second=0.0 if execution.duration_ms == 0 else None))
    _audit(db, actor, f"admin.ingestion.job.{operation}", job, payload.reason, request_id, ip_address, previous=previous, new=_job_snapshot(job))
    db.commit()
    return get_job_or_raise(db, job.id)


def list_executions(
    db: Session,
    *,
    job_id: int | None = None,
    status: str | None = None,
    trigger_type: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> ExecutionListResult:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(IngestionExecution).options(selectinload(IngestionExecution.job).selectinload(IngestionJob.source), selectinload(IngestionExecution.operator), selectinload(IngestionExecution.metric), selectinload(IngestionExecution.failures))
    if job_id is not None:
        query = query.where(IngestionExecution.job_id == job_id)
    if status:
        query = query.where(IngestionExecution.status == status)
    if trigger_type:
        query = query.where(IngestionExecution.trigger_type == trigger_type)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    executions = list(db.scalars(query.order_by(desc(IngestionExecution.created_at)).offset((page - 1) * limit).limit(limit)).unique().all())
    return ExecutionListResult(executions=executions, total=total, page=page, limit=limit)


def get_execution_or_raise(db: Session, execution_id: int) -> IngestionExecution:
    execution = db.scalar(
        select(IngestionExecution)
        .where(IngestionExecution.id == execution_id)
        .options(selectinload(IngestionExecution.job).selectinload(IngestionJob.source), selectinload(IngestionExecution.operator), selectinload(IngestionExecution.metric), selectinload(IngestionExecution.failures))
    )
    if execution is None:
        raise IngestionOperationsError("Execution was not found", "INGESTION_EXECUTION_NOT_FOUND", 404)
    return execution


def job_list_payload(db: Session, result: JobListResult) -> IngestionJobListPayload:
    return IngestionJobListPayload(
        jobs=[job_to_summary(job) for job in result.jobs],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
        summary=summary_widgets(db),
    )


def execution_list_payload(result: ExecutionListResult) -> IngestionExecutionListPayload:
    return IngestionExecutionListPayload(
        executions=[execution_to_read(execution) for execution in result.executions],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
    )


def summary_widgets(db: Session) -> dict[str, int | float | str]:
    jobs = list(db.scalars(select(IngestionJob).where(IngestionJob.status != IngestionJobStatus.DELETED.value)).all())
    executions_today = db.scalar(select(func.count()).select_from(IngestionExecution)) or 0
    durations = [value for value in db.scalars(select(IngestionExecution.duration_ms).where(IngestionExecution.duration_ms.is_not(None))).all() if value is not None]
    return {
        "registered_jobs": len(jobs),
        "running_jobs": sum(1 for job in jobs if job.status == IngestionJobStatus.RUNNING.value),
        "failed_jobs": sum(1 for job in jobs if job.status == IngestionJobStatus.FAILED.value),
        "paused_jobs": sum(1 for job in jobs if job.status == IngestionJobStatus.PAUSED.value),
        "fresh_sources": sum(1 for job in jobs if job.freshness_status == FreshnessStatus.FRESH.value),
        "stale_sources": sum(1 for job in jobs if job.freshness_status in {FreshnessStatus.STALE.value, FreshnessStatus.EXPIRED.value}),
        "average_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
        "todays_executions": executions_today,
    }


def job_to_summary(job: IngestionJob) -> IngestionJobSummary:
    latest = job.executions[0] if job.executions else None
    return IngestionJobSummary(
        id=job.id,
        source_id=job.source_id,
        source_name=job.source.display_name if job.source else "Unknown source",
        name=job.name,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        is_enabled=job.is_enabled,
        execution_mode=job.execution_mode,
        manual_only=job.manual_only,
        last_run_at=job.last_run_at,
        last_successful_run_at=job.last_successful_run_at,
        next_scheduled_run_at=job.next_scheduled_run_at,
        freshness_status=job.freshness_status,
        latest_execution_status=latest.status if latest else None,
        updated_at=job.updated_at,
    )


def job_to_read(db: Session, job: IngestionJob) -> IngestionJobRead:
    summary = job_to_summary(job).model_dump()
    recent_failures = [failure for execution in job.executions[:10] for failure in execution.failures]
    audits = [
        {
            "id": event.id,
            "action": event.action,
            "reason": event.reason,
            "result": event.result,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        for event in db.scalars(select(AuditLog).where(AuditLog.target_type == "ingestion_job", AuditLog.target_id == str(job.id)).order_by(AuditLog.created_at.desc()).limit(10)).all()
    ]
    return IngestionJobRead(
        **summary,
        description=job.description,
        configuration=job.configuration,
        max_retries=job.max_retries,
        timeout_seconds=job.timeout_seconds,
        concurrency_limit=job.concurrency_limit,
        queue_name=job.queue_name,
        recent_executions=[execution_to_read(execution) for execution in job.executions[:10]],
        recent_failures=[ExecutionFailureRead.model_validate(failure) for failure in recent_failures[:10]],
        audit=audits,
        created_at=job.created_at,
    )


def execution_to_read(execution: IngestionExecution) -> IngestionExecutionRead:
    return IngestionExecutionRead(
        id=execution.id,
        job_id=execution.job_id,
        job_name=execution.job.name if execution.job else None,
        source_name=execution.job.source.display_name if execution.job and execution.job.source else None,
        status=execution.status,
        trigger_type=execution.trigger_type,
        operator_user_id=execution.operator_user_id,
        operator_email=execution.operator.email if execution.operator else None,
        retry_count=execution.retry_count,
        result_summary=execution.result_summary,
        started_at=execution.started_at,
        finished_at=execution.finished_at,
        duration_ms=execution.duration_ms,
        request_id=execution.request_id,
        metric=ExecutionMetricRead.model_validate(execution.metric) if execution.metric else None,
        failures=[ExecutionFailureRead.model_validate(failure) for failure in execution.failures],
        created_at=execution.created_at,
    )


def _job_snapshot(job: IngestionJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "source_id": job.source_id,
        "name": job.name,
        "job_type": job.job_type,
        "execution_mode": job.execution_mode,
        "priority": job.priority,
        "status": job.status,
        "is_enabled": job.is_enabled,
        "manual_only": job.manual_only,
        "freshness_status": job.freshness_status,
        "max_retries": job.max_retries,
        "timeout_seconds": job.timeout_seconds,
        "concurrency_limit": job.concurrency_limit,
        "queue_name": job.queue_name,
    }


def _audit(db: Session, actor: User, action: str, job: IngestionJob, reason: str | None, request_id: str | None, ip_address: str | None, previous: dict[str, Any] | None, new: dict[str, Any] | None) -> None:
    record_audit_event(
        db,
        actor=actor,
        action=action,
        target_type="ingestion_job",
        target_id=str(job.id),
        result="success",
        reason=reason,
        request_id=request_id,
        ip_address=ip_address,
        metadata={"previous": previous, "new": new},
        commit=False,
    )

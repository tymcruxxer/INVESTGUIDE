"""Development-only seed data for the Ingestion Operations Centre."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.ingestion_operations import ExecutionFailure, ExecutionMetric, FreshnessStatus, IngestionExecution, IngestionExecutionStatus, IngestionJob, IngestionJobStatus
from app.models.rbac import Role, UserRole
from app.models.source_registry import Source
from app.models.user import User
from app.schemas.ingestion_operations import IngestionJobCreate
from app.services.ingestion_operations_service import create_job
from app.services.rbac_service import OWNER_ROLE

logger = get_logger(__name__)

JOB_CATALOGUE: tuple[dict[str, object], ...] = (
    {"source": "zimbabwe_stock_exchange", "name": "ZSE market prices monitor", "job_type": "market_prices", "priority": "high", "status": "pending", "freshness": "fresh"},
    {"source": "zimbabwe_stock_exchange", "name": "ZSE corporate actions review", "job_type": "corporate_actions", "priority": "high", "status": "paused", "freshness": "aging"},
    {"source": "victoria_falls_stock_exchange", "name": "VFEX announcements review", "job_type": "trading_updates", "priority": "normal", "status": "pending", "freshness": "fresh"},
    {"source": "reserve_bank_of_zimbabwe", "name": "RBZ exchange rates monitor", "job_type": "exchange_rates", "priority": "critical", "status": "failed", "freshness": "stale"},
    {"source": "zimstat", "name": "ZIMSTAT inflation release review", "job_type": "economic_indicators", "priority": "high", "status": "pending", "freshness": "stale"},
    {"source": "ih_securities", "name": "IH Securities research reports", "job_type": "research_reports", "priority": "normal", "status": "pending", "freshness": "aging"},
    {"source": "newsday_business", "name": "NewsDay business news review", "job_type": "news", "priority": "low", "status": "pending", "freshness": "fresh"},
)


@dataclass(frozen=True)
class IngestionOperationsSeedResult:
    inserted_jobs: int
    skipped_jobs: int
    inserted_executions: int
    inserted_failures: int


def seed_ingestion_operations(db: Session) -> IngestionOperationsSeedResult:
    """Seed operator-visible ingestion jobs and simulated execution history."""
    ensure_development_data_allowed()
    actor = _owner_user(db)
    inserted_jobs = 0
    skipped_jobs = 0
    inserted_executions = 0
    inserted_failures = 0
    try:
        for item in JOB_CATALOGUE:
            source = db.scalar(select(Source).where(Source.name == str(item["source"])))
            if source is None:
                skipped_jobs += 1
                continue
            existing = db.scalar(select(IngestionJob).where(IngestionJob.source_id == source.id, IngestionJob.name == str(item["name"])))
            if existing is not None:
                skipped_jobs += 1
                continue
            job = create_job(
                db,
                actor=actor,
                payload=IngestionJobCreate(
                    source_id=source.id,
                    name=str(item["name"]),
                    job_type=str(item["job_type"]),
                    description="Development operations-centre job. It does not execute live ingestion.",
                    configuration={"mode": "development_preview", "executes_live_ingestion": False},
                    execution_mode="manual",
                    priority=str(item["priority"]),
                    status=str(item["status"]),
                    is_enabled=str(item["status"]) not in {"paused", "failed"},
                    manual_only=True,
                    freshness_status=str(item["freshness"]),
                    reason="Development ingestion operations seed",
                ),
            )
            inserted_jobs += 1
            execution, failed = _seed_execution_for_job(db, job, actor)
            inserted_executions += 1 if execution else 0
            inserted_failures += 1 if failed else 0
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Ingestion operations seed failed; transaction rolled back")
        raise
    logger.info("Ingestion operations seed completed: %s jobs inserted, %s jobs skipped", inserted_jobs, skipped_jobs)
    return IngestionOperationsSeedResult(inserted_jobs=inserted_jobs, skipped_jobs=skipped_jobs, inserted_executions=inserted_executions, inserted_failures=inserted_failures)


def _seed_execution_for_job(db: Session, job: IngestionJob, actor: User) -> tuple[IngestionExecution | None, bool]:
    now = datetime.now(UTC)
    if job.status == IngestionJobStatus.FAILED.value:
        execution = IngestionExecution(job_id=job.id, status=IngestionExecutionStatus.FAILED.value, trigger_type="manual", operator_user_id=actor.id, retry_count=1, result_summary="Simulated development failure; no live connector was executed.", started_at=now - timedelta(minutes=12), finished_at=now - timedelta(minutes=10), duration_ms=120000)
        db.add(execution)
        db.flush()
        db.add(ExecutionMetric(execution_id=execution.id, rows_processed=0, records_rejected=1, error_count=1, duration_ms=120000, throughput_per_second=0.0))
        db.add(ExecutionFailure(execution_id=execution.id, failure_category="authentication", error_message="Development placeholder: credentials are not configured.", stack_trace_placeholder="Stack trace intentionally omitted in development seed.", retry_eligible=True, failed_at=now - timedelta(minutes=10)))
        job.last_run_at = execution.started_at
        return execution, True
    status = IngestionExecutionStatus.PAUSED.value if job.status == IngestionJobStatus.PAUSED.value else IngestionExecutionStatus.COMPLETED.value
    duration = 45000 if status == IngestionExecutionStatus.COMPLETED.value else 0
    execution = IngestionExecution(job_id=job.id, status=status, trigger_type="manual", operator_user_id=actor.id, retry_count=0, result_summary="Simulated development execution record. No live ingestion was executed.", started_at=now - timedelta(hours=2), finished_at=now - timedelta(hours=2) + timedelta(milliseconds=duration), duration_ms=duration)
    db.add(execution)
    db.flush()
    db.add(ExecutionMetric(execution_id=execution.id, rows_processed=120 if duration else 0, records_inserted=20 if duration else 0, records_updated=8 if duration else 0, duplicates_detected=3 if duration else 0, records_rejected=1 if duration else 0, warning_count=2 if duration else 0, error_count=0, duration_ms=duration, throughput_per_second=2.67 if duration else 0.0))
    job.last_run_at = execution.started_at
    if status == IngestionExecutionStatus.COMPLETED.value:
        job.last_successful_run_at = execution.finished_at
        job.status = IngestionJobStatus.COMPLETED.value
        if job.freshness_status == FreshnessStatus.UNKNOWN.value:
            job.freshness_status = FreshnessStatus.FRESH.value
    return execution, False


def _owner_user(db: Session) -> User:
    owner = db.scalar(select(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(Role.slug == OWNER_ROLE, UserRole.is_active.is_(True)))
    if owner is None:
        raise RuntimeError("RBAC Owner must be bootstrapped before seeding ingestion operations")
    return owner

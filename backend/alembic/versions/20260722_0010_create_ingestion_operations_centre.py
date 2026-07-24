"""create ingestion operations centre tables

Revision ID: 20260722_0010
Revises: 20260722_0009
Create Date: 2026-07-22 15:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0010"
down_revision: str | None = "20260722_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("execution_mode", sa.String(length=40), server_default="manual", nullable=False),
        sa.Column("priority", sa.String(length=40), server_default="normal", nullable=False),
        sa.Column("max_retries", sa.Integer(), server_default="3", nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), server_default="300", nullable=False),
        sa.Column("concurrency_limit", sa.Integer(), server_default="1", nullable=False),
        sa.Column("queue_name", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="pending", nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("manual_only", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_successful_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_scheduled_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("freshness_status", sa.String(length=40), server_default="unknown", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "name", name="uq_ingestion_jobs_source_id_name"),
    )
    op.create_index("ix_ingestion_jobs_freshness_status", "ingestion_jobs", ["freshness_status"])
    op.create_index("ix_ingestion_jobs_job_type", "ingestion_jobs", ["job_type"])
    op.create_index("ix_ingestion_jobs_priority", "ingestion_jobs", ["priority"])
    op.create_index("ix_ingestion_jobs_source_id", "ingestion_jobs", ["source_id"])
    op.create_index("ix_ingestion_jobs_status", "ingestion_jobs", ["status"])

    op.create_table(
        "ingestion_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="queued", nullable=False),
        sa.Column("trigger_type", sa.String(length=40), nullable=False),
        sa.Column("operator_user_id", sa.Integer(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["ingestion_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operator_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_executions_job_id", "ingestion_executions", ["job_id"])
    op.create_index("ix_ingestion_executions_started_at", "ingestion_executions", ["started_at"])
    op.create_index("ix_ingestion_executions_status", "ingestion_executions", ["status"])
    op.create_index("ix_ingestion_executions_trigger_type", "ingestion_executions", ["trigger_type"])

    op.create_table(
        "execution_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("rows_processed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_inserted", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duplicates_detected", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_rejected", sa.Integer(), server_default="0", nullable=False),
        sa.Column("warning_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("throughput_per_second", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["ingestion_executions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("execution_id", name="uq_execution_metrics_execution_id"),
    )

    op.create_table(
        "execution_failures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("failure_category", sa.String(length=60), server_default="unknown", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("stack_trace_placeholder", sa.Text(), nullable=True),
        sa.Column("retry_eligible", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["ingestion_executions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_execution_failures_category", "execution_failures", ["failure_category"])
    op.create_index("ix_execution_failures_execution_id", "execution_failures", ["execution_id"])
    op.create_index("ix_execution_failures_failed_at", "execution_failures", ["failed_at"])


def downgrade() -> None:
    op.drop_index("ix_execution_failures_failed_at", table_name="execution_failures")
    op.drop_index("ix_execution_failures_execution_id", table_name="execution_failures")
    op.drop_index("ix_execution_failures_category", table_name="execution_failures")
    op.drop_table("execution_failures")
    op.drop_table("execution_metrics")
    op.drop_index("ix_ingestion_executions_trigger_type", table_name="ingestion_executions")
    op.drop_index("ix_ingestion_executions_status", table_name="ingestion_executions")
    op.drop_index("ix_ingestion_executions_started_at", table_name="ingestion_executions")
    op.drop_index("ix_ingestion_executions_job_id", table_name="ingestion_executions")
    op.drop_table("ingestion_executions")
    op.drop_index("ix_ingestion_jobs_status", table_name="ingestion_jobs")
    op.drop_index("ix_ingestion_jobs_source_id", table_name="ingestion_jobs")
    op.drop_index("ix_ingestion_jobs_priority", table_name="ingestion_jobs")
    op.drop_index("ix_ingestion_jobs_job_type", table_name="ingestion_jobs")
    op.drop_index("ix_ingestion_jobs_freshness_status", table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")

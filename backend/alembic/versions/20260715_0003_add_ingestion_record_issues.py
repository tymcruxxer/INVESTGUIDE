"""Add ingestion record issues and operational run counters."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260715_0003"
down_revision = "20260715_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_runs", sa.Column("normalized_records", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ingestion_runs", sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ingestion_runs", sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ingestion_runs", sa.Column("triggered_by", sa.String(length=100), nullable=True))

    op.create_table(
        "ingestion_record_issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ingestion_run_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("record_index", sa.Integer(), nullable=True),
        sa.Column("external_key", sa.String(length=128), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("issue_code", sa.String(length=100), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("raw_value_summary", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_record_issues_run_id", "ingestion_record_issues", ["ingestion_run_id"])
    op.create_index("ix_ingestion_record_issues_entity", "ingestion_record_issues", ["entity_type"])
    op.create_index("ix_ingestion_record_issues_severity", "ingestion_record_issues", ["severity"])
    op.create_index("ix_ingestion_record_issues_issue_code", "ingestion_record_issues", ["issue_code"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_record_issues_issue_code", table_name="ingestion_record_issues")
    op.drop_index("ix_ingestion_record_issues_severity", table_name="ingestion_record_issues")
    op.drop_index("ix_ingestion_record_issues_entity", table_name="ingestion_record_issues")
    op.drop_index("ix_ingestion_record_issues_run_id", table_name="ingestion_record_issues")
    op.drop_table("ingestion_record_issues")
    op.drop_column("ingestion_runs", "triggered_by")
    op.drop_column("ingestion_runs", "error_count")
    op.drop_column("ingestion_runs", "warning_count")
    op.drop_column("ingestion_runs", "normalized_records")

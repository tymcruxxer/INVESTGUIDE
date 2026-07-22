"""add financial statement provenance metadata

Revision ID: 20260721_0006
Revises: 20260715_0005
Create Date: 2026-07-21 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260721_0006"
down_revision = "20260715_0005"
branch_labels = None
depends_on = None


TABLES = ("income_statements", "balance_sheets", "cash_flow_statements")


def upgrade() -> None:
    """Add nullable provenance metadata to existing statement tables."""
    for table in TABLES:
        op.add_column(table, sa.Column("source_type", sa.String(length=100), nullable=True))
        op.add_column(table, sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))
        op.add_column(table, sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
        op.add_column(table, sa.Column("verification_status", sa.String(length=50), nullable=True))
        op.add_column(table, sa.Column("dataset_version", sa.String(length=100), nullable=True))
        op.add_column(table, sa.Column("external_key", sa.String(length=128), nullable=True))
        op.create_index(f"ix_{table}_is_development_data", table, ["is_development_data"])
        op.create_index(f"ix_{table}_verification_status", table, ["verification_status"])


def downgrade() -> None:
    """Remove financial statement provenance metadata."""
    for table in reversed(TABLES):
        op.drop_index(f"ix_{table}_verification_status", table_name=table)
        op.drop_index(f"ix_{table}_is_development_data", table_name=table)
        op.drop_column(table, "external_key")
        op.drop_column(table, "dataset_version")
        op.drop_column(table, "verification_status")
        op.drop_column(table, "verified_at")
        op.drop_column(table, "imported_at")
        op.drop_column(table, "source_type")

"""create data source registry tables

Revision ID: 20260722_0009
Revises: 20260721_0008
Create Date: 2026-07-22 12:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0009"
down_revision: str | None = "20260721_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("tier", sa.String(length=40), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("classification", sa.String(length=120), nullable=True),
        sa.Column("supported_capabilities", sa.JSON(), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("authentication_type", sa.String(length=80), server_default="none", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="disabled", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_sources_name"),
    )
    op.create_index("ix_sources_category", "sources", ["category"])
    op.create_index("ix_sources_connector_type", "sources", ["connector_type"])
    op.create_index("ix_sources_status", "sources", ["status"])
    op.create_index("ix_sources_tier", "sources", ["tier"])

    op.create_table(
        "source_configurations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("base_url", sa.String(length=1000), nullable=True),
        sa.Column("headers", sa.JSON(), nullable=False),
        sa.Column("parser", sa.JSON(), nullable=False),
        sa.Column("connector_config", sa.JSON(), nullable=False),
        sa.Column("refresh_policy", sa.String(length=40), server_default="manual", nullable=False),
        sa.Column("custom_cron", sa.String(length=120), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), server_default="30", nullable=False),
        sa.Column("retry_count", sa.Integer(), server_default="3", nullable=False),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("backoff_policy", sa.String(length=120), nullable=True),
        sa.Column("freshness_window_minutes", sa.Integer(), nullable=True),
        sa.Column("confidence_weight", sa.Float(), server_default="0.7", nullable=False),
        sa.Column("trust_level", sa.String(length=120), server_default="standard", nullable=False),
        sa.Column("verification_required", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("parser_version", sa.String(length=80), server_default="1", nullable=False),
        sa.Column("connector_version", sa.String(length=80), server_default="1", nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_by_user_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["last_modified_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", name="uq_source_configurations_source_id"),
    )

    op.create_table(
        "source_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("secret_type", sa.String(length=80), nullable=False),
        sa.Column("secret_reference", sa.String(length=255), nullable=True),
        sa.Column("encrypted_value", sa.Text(), nullable=True),
        sa.Column("is_configured", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("last_rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "key", name="uq_source_credentials_source_key"),
    )
    op.create_index("ix_source_credentials_source_id", "source_credentials", ["source_id"])

    op.create_table(
        "source_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("change_type", sa.String(length=80), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_versions_created_at", "source_versions", ["created_at"])
    op.create_index("ix_source_versions_source_id", "source_versions", ["source_id"])


def downgrade() -> None:
    op.drop_index("ix_source_versions_source_id", table_name="source_versions")
    op.drop_index("ix_source_versions_created_at", table_name="source_versions")
    op.drop_table("source_versions")
    op.drop_index("ix_source_credentials_source_id", table_name="source_credentials")
    op.drop_table("source_credentials")
    op.drop_table("source_configurations")
    op.drop_index("ix_sources_tier", table_name="sources")
    op.drop_index("ix_sources_status", table_name="sources")
    op.drop_index("ix_sources_connector_type", table_name="sources")
    op.drop_index("ix_sources_category", table_name="sources")
    op.drop_table("sources")


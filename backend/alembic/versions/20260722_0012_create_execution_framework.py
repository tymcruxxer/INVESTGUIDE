"""create execution framework

Revision ID: 20260722_0012
Revises: 20260722_0011
Create Date: 2026-07-22 00:12:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260722_0012"
down_revision = "20260722_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=80), server_default="1.0.0", nullable=False),
        sa.Column("runtime_class", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("supported_connector_types", sa.JSON(), nullable=False),
        sa.Column("lifecycle_states", sa.JSON(), nullable=False),
        sa.Column("result_statuses", sa.JSON(), nullable=False),
        sa.Column("runtime_metadata", sa.JSON(), nullable=False),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("classification", sa.String(length=120), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["archived_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_runtime_definitions_name"),
    )
    op.create_index("ix_runtime_definitions_runtime_class", "runtime_definitions", ["runtime_class"])
    op.create_index("ix_runtime_definitions_status", "runtime_definitions", ["status"])

    op.create_table(
        "runtime_capabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("runtime_id", sa.Integer(), nullable=False),
        sa.Column("capability", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["runtime_id"], ["runtime_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("runtime_id", "capability", name="uq_runtime_capabilities_runtime_capability"),
    )
    op.create_index("ix_runtime_capabilities_capability", "runtime_capabilities", ["capability"])

    op.create_table(
        "runtime_compatibilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("runtime_id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.Integer(), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("compatibility_status", sa.String(length=40), server_default="compatible", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["runtime_id"], ["runtime_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("runtime_id", "connector_id", name="uq_runtime_compatibilities_runtime_connector"),
    )
    op.create_index("ix_runtime_compatibilities_connector_id", "runtime_compatibilities", ["connector_id"])
    op.create_index("ix_runtime_compatibilities_status", "runtime_compatibilities", ["compatibility_status"])

    op.create_table(
        "runtime_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("runtime_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("change_type", sa.String(length=80), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["runtime_id"], ["runtime_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_runtime_versions_created_at", "runtime_versions", ["created_at"])
    op.create_index("ix_runtime_versions_runtime_id", "runtime_versions", ["runtime_id"])

    op.create_table(
        "runtime_validations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("runtime_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("connector_id", sa.Integer(), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("checked_fields", sa.JSON(), nullable=False),
        sa.Column("execution_context", sa.JSON(), nullable=False),
        sa.Column("result_contract", sa.JSON(), nullable=False),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["runtime_id"], ["runtime_definitions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_runtime_validations_request_id", "runtime_validations", ["request_id"])
    op.create_index("ix_runtime_validations_runtime_id", "runtime_validations", ["runtime_id"])
    op.create_index("ix_runtime_validations_status", "runtime_validations", ["status"])


def downgrade() -> None:
    op.drop_index("ix_runtime_validations_status", table_name="runtime_validations")
    op.drop_index("ix_runtime_validations_runtime_id", table_name="runtime_validations")
    op.drop_index("ix_runtime_validations_request_id", table_name="runtime_validations")
    op.drop_table("runtime_validations")
    op.drop_index("ix_runtime_versions_runtime_id", table_name="runtime_versions")
    op.drop_index("ix_runtime_versions_created_at", table_name="runtime_versions")
    op.drop_table("runtime_versions")
    op.drop_index("ix_runtime_compatibilities_status", table_name="runtime_compatibilities")
    op.drop_index("ix_runtime_compatibilities_connector_id", table_name="runtime_compatibilities")
    op.drop_table("runtime_compatibilities")
    op.drop_index("ix_runtime_capabilities_capability", table_name="runtime_capabilities")
    op.drop_table("runtime_capabilities")
    op.drop_index("ix_runtime_definitions_status", table_name="runtime_definitions")
    op.drop_index("ix_runtime_definitions_runtime_class", table_name="runtime_definitions")
    op.drop_table("runtime_definitions")

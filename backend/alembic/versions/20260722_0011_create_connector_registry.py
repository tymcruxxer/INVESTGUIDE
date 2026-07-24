"""create connector registry

Revision ID: 20260722_0011
Revises: 20260722_0010
Create Date: 2026-07-22 00:11:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260722_0011"
down_revision = "20260722_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "connectors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=80), server_default="1.0.0", nullable=False),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("classification", sa.String(length=120), nullable=True),
        sa.Column("connector_type", sa.String(length=80), nullable=False),
        sa.Column("lifecycle", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("authentication_strategy", sa.String(length=80), server_default="none", nullable=False),
        sa.Column("configuration_schema", sa.JSON(), nullable=False),
        sa.Column("required_fields", sa.JSON(), nullable=False),
        sa.Column("supported_source_categories", sa.JSON(), nullable=False),
        sa.Column("compatibility_notes", sa.Text(), nullable=True),
        sa.Column("deprecation_status", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["archived_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_connectors_name"),
    )
    op.create_index("ix_connectors_classification", "connectors", ["classification"])
    op.create_index("ix_connectors_connector_type", "connectors", ["connector_type"])
    op.create_index("ix_connectors_lifecycle", "connectors", ["lifecycle"])

    op.create_table(
        "connector_capabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.Integer(), nullable=False),
        sa.Column("capability", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connector_id", "capability", name="uq_connector_capabilities_connector_capability"),
    )
    op.create_index("ix_connector_capabilities_capability", "connector_capabilities", ["capability"])

    op.create_table(
        "connector_configuration_schemas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.Integer(), nullable=False),
        sa.Column("schema", sa.JSON(), nullable=False),
        sa.Column("required_fields", sa.JSON(), nullable=False),
        sa.Column("endpoint_templates", sa.JSON(), nullable=False),
        sa.Column("headers_schema", sa.JSON(), nullable=False),
        sa.Column("pagination_strategy", sa.String(length=120), nullable=True),
        sa.Column("parser_identifier", sa.String(length=255), nullable=True),
        sa.Column("rate_limit_policy", sa.JSON(), nullable=False),
        sa.Column("default_timeout_seconds", sa.Integer(), server_default="30", nullable=False),
        sa.Column("default_retry_count", sa.Integer(), server_default="3", nullable=False),
        sa.Column("request_method", sa.String(length=20), server_default="GET", nullable=False),
        sa.Column("compression", sa.String(length=80), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connector_id", name="uq_connector_configuration_schemas_connector_id"),
    )

    op.create_table(
        "connector_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("change_type", sa.String(length=80), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("compatibility_notes", sa.Text(), nullable=True),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_connector_versions_connector_id", "connector_versions", ["connector_id"])
    op.create_index("ix_connector_versions_created_at", "connector_versions", ["created_at"])

    op.create_table(
        "connector_validations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("checked_fields", sa.JSON(), nullable=False),
        sa.Column("requested_config", sa.JSON(), nullable=False),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connector_id"], ["connectors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_connector_validations_connector_id", "connector_validations", ["connector_id"])
    op.create_index("ix_connector_validations_status", "connector_validations", ["status"])

    op.add_column("sources", sa.Column("connector_id", sa.Integer(), nullable=True))
    op.create_index("ix_sources_connector_id", "sources", ["connector_id"])
    op.create_foreign_key("fk_sources_connector_id_connectors", "sources", "connectors", ["connector_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_sources_connector_id_connectors", "sources", type_="foreignkey")
    op.drop_index("ix_sources_connector_id", table_name="sources")
    op.drop_column("sources", "connector_id")
    op.drop_index("ix_connector_validations_status", table_name="connector_validations")
    op.drop_index("ix_connector_validations_connector_id", table_name="connector_validations")
    op.drop_table("connector_validations")
    op.drop_index("ix_connector_versions_created_at", table_name="connector_versions")
    op.drop_index("ix_connector_versions_connector_id", table_name="connector_versions")
    op.drop_table("connector_versions")
    op.drop_table("connector_configuration_schemas")
    op.drop_index("ix_connector_capabilities_capability", table_name="connector_capabilities")
    op.drop_table("connector_capabilities")
    op.drop_index("ix_connectors_lifecycle", table_name="connectors")
    op.drop_index("ix_connectors_connector_type", table_name="connectors")
    op.drop_index("ix_connectors_classification", table_name="connectors")
    op.drop_table("connectors")

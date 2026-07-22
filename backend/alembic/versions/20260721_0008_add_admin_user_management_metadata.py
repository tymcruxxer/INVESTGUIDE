"""add admin user management metadata

Revision ID: 20260721_0008
Revises: 20260721_0007
Create Date: 2026-07-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0008"
down_revision: Union[str, None] = "20260721_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("suspension_reason", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("suspended_by_user_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("restored_by_user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(op.f("fk_users_suspended_by_user_id_users"), "users", "users", ["suspended_by_user_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(op.f("fk_users_restored_by_user_id_users"), "users", "users", ["restored_by_user_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_is_verified", "users", ["is_verified"])

    op.add_column("user_roles", sa.Column("assignment_reason", sa.Text(), nullable=True))
    op.create_index("ix_user_roles_is_active", "user_roles", ["is_active"])

    op.create_table(
        "user_role_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("previous_roles", sa.Text(), nullable=True),
        sa.Column("new_roles", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_user_role_history_actor_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name=op.f("fk_user_role_history_role_id_roles"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_role_history_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_role_history")),
    )
    op.create_index("ix_user_role_history_user_id", "user_role_history", ["user_id"])
    op.create_index("ix_user_role_history_role_id", "user_role_history", ["role_id"])
    op.create_index("ix_user_role_history_action", "user_role_history", ["action"])

    op.create_table(
        "privilege_change_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("target_user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("previous_state", sa.Text(), nullable=True),
        sa.Column("new_state", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("result", sa.String(length=40), nullable=False, server_default="success"),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_privilege_change_history_actor_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], name=op.f("fk_privilege_change_history_target_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_privilege_change_history")),
    )
    op.create_index("ix_privilege_change_history_actor_user_id", "privilege_change_history", ["actor_user_id"])
    op.create_index("ix_privilege_change_history_target_user_id", "privilege_change_history", ["target_user_id"])
    op.create_index("ix_privilege_change_history_action", "privilege_change_history", ["action"])


def downgrade() -> None:
    op.drop_index("ix_privilege_change_history_action", table_name="privilege_change_history")
    op.drop_index("ix_privilege_change_history_target_user_id", table_name="privilege_change_history")
    op.drop_index("ix_privilege_change_history_actor_user_id", table_name="privilege_change_history")
    op.drop_table("privilege_change_history")
    op.drop_index("ix_user_role_history_action", table_name="user_role_history")
    op.drop_index("ix_user_role_history_role_id", table_name="user_role_history")
    op.drop_index("ix_user_role_history_user_id", table_name="user_role_history")
    op.drop_table("user_role_history")
    op.drop_index("ix_user_roles_is_active", table_name="user_roles")
    op.drop_column("user_roles", "assignment_reason")
    op.drop_index("ix_users_is_verified", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_constraint(op.f("fk_users_restored_by_user_id_users"), "users", type_="foreignkey")
    op.drop_constraint(op.f("fk_users_suspended_by_user_id_users"), "users", type_="foreignkey")
    op.drop_column("users", "restored_by_user_id")
    op.drop_column("users", "restored_at")
    op.drop_column("users", "suspended_by_user_id")
    op.drop_column("users", "suspension_reason")
    op.drop_column("users", "suspended_at")
    op.drop_column("users", "last_login_at")

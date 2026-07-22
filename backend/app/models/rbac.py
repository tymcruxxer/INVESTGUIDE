"""RBAC models for InvestGuide administration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Role(TimestampMixin, Base):
    """Named authorization role assigned to users."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", name="uq_roles_name"),
        UniqueConstraint("slug", name="uq_roles_slug"),
        Index("ix_roles_slug", "slug"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_owner_role: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    permissions: Mapped[list[RolePermission]] = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    users: Mapped[list[UserRole]] = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(TimestampMixin, Base):
    """Granular permission used by server-side authorization."""

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_permissions_code"),
        Index("ix_permissions_code", "code"),
        Index("ix_permissions_category", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_permission: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    roles: Mapped[list[RolePermission]] = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(TimestampMixin, Base):
    """Many-to-many link between roles and permissions."""

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"),
        Index("ix_role_permissions_role_id", "role_id"),
        Index("ix_role_permissions_permission_id", "permission_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role: Mapped[Role] = relationship("Role", back_populates="permissions")
    permission: Mapped[Permission] = relationship("Permission", back_populates="roles")


class UserRole(TimestampMixin, Base):
    """Role assignment for a user."""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
        Index("ix_user_roles_user_id", "user_id"),
        Index("ix_user_roles_role_id", "role_id"),
        Index("ix_user_roles_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignment_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], back_populates="roles")
    assigned_by: Mapped[User | None] = relationship("User", foreign_keys=[assigned_by_user_id])
    role: Mapped[Role] = relationship("Role", back_populates="users")


class UserRoleHistory(TimestampMixin, Base):
    """Immutable role assignment/removal history."""

    __tablename__ = "user_role_history"
    __table_args__ = (
        Index("ix_user_role_history_user_id", "user_id"),
        Index("ix_user_role_history_role_id", "role_id"),
        Index("ix_user_role_history_action", "action"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    previous_roles: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_roles: Mapped[str | None] = mapped_column(Text, nullable=True)


class PrivilegeChangeHistory(TimestampMixin, Base):
    """Audit-friendly history for role and account status changes."""

    __tablename__ = "privilege_change_history"
    __table_args__ = (
        Index("ix_privilege_change_history_actor_user_id", "actor_user_id"),
        Index("ix_privilege_change_history_target_user_id", "target_user_id"),
        Index("ix_privilege_change_history_action", "action"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    previous_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(String(40), nullable=False, default="success")
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

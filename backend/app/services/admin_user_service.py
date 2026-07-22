"""Admin user, role, and permission management service."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.rbac import Permission, PrivilegeChangeHistory, Role, RolePermission, UserRole, UserRoleHistory
from app.models.sensitive_action import SensitiveActionRequest, SensitiveActionStatus
from app.models.user import User
from app.services.audit_service import record_audit_event
from app.services.rbac_service import ADMINISTRATOR_ROLE, OWNER_ROLE, get_user_roles, is_owner

UserStatus = Literal["active", "suspended"]


class AdminUserManagementError(ValueError):
    """Raised when admin user-management rules reject an action."""

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


@dataclass(frozen=True)
class UserListResult:
    """Paginated user listing."""

    users: list[User]
    total: int
    page: int
    limit: int


def _role_names(db: Session, user: User) -> list[str]:
    return [role.slug for role in get_user_roles(db, user)]


def _json_roles(roles: list[str]) -> str:
    return json.dumps(sorted(roles))


def list_users(
    db: Session,
    *,
    search: str | None = None,
    status: str | None = None,
    verified: bool | None = None,
    role: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20,
) -> UserListResult:
    """Return paginated users for the admin directory."""
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(User).options(selectinload(User.roles).selectinload(UserRole.role))

    if search:
        needle = f"%{search.strip().lower()}%"
        query = query.where(or_(func.lower(User.email).like(needle), func.lower(User.username).like(needle)))
    if status == "active":
        query = query.where(User.is_active.is_(True))
    elif status == "suspended":
        query = query.where(User.is_active.is_(False))
    if verified is not None:
        query = query.where(User.is_verified.is_(verified))
    if role:
        role_slug = role.strip().lower()
        query = query.join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(
            UserRole.is_active.is_(True), Role.slug == role_slug
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = {
        "email": User.email,
        "created_at": User.created_at,
        "last_login_at": User.last_login_at,
        "status": User.is_active,
    }.get(sort_by, User.created_at)
    order = asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)
    users = list(db.scalars(query.order_by(order).offset((page - 1) * limit).limit(limit)).unique().all())
    return UserListResult(users=users, total=total, page=page, limit=limit)


def get_user_or_raise(db: Session, user_id: int) -> User:
    """Return a user or raise a management error."""
    user = db.get(User, user_id)
    if user is None:
        raise AdminUserManagementError("User was not found", "USER_NOT_FOUND", 404)
    return user


def list_roles(db: Session) -> list[Role]:
    """Return roles with permissions and assignments loaded."""
    return list(
        db.scalars(
            select(Role)
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission), selectinload(Role.users))
            .order_by(Role.id.asc())
        ).all()
    )


def get_role_or_raise(db: Session, role_id: int) -> Role:
    """Return a role or raise a management error."""
    role = db.get(Role, role_id)
    if role is None:
        raise AdminUserManagementError("Role was not found", "ROLE_NOT_FOUND", 404)
    return role


def assign_role(db: Session, *, actor: User, target: User, role_id: int, reason: str, request_id: str | None = None) -> User:
    """Assign a role to a user with audit and Owner protections."""
    reason = reason.strip()
    if not reason:
        raise AdminUserManagementError("A reason is required", "REASON_REQUIRED")
    role = get_role_or_raise(db, role_id)
    if role.slug == OWNER_ROLE or role.is_owner_role:
        raise AdminUserManagementError("Owner role assignment requires the dedicated ownership-transfer workflow", "OWNER_ROLE_PROTECTED", 409)

    previous_roles = _role_names(db, target)
    existing = db.scalar(select(UserRole).where(UserRole.user_id == target.id, UserRole.role_id == role.id))
    if existing and existing.is_active:
        raise AdminUserManagementError("User already has this role", "DUPLICATE_ROLE_ASSIGNMENT", 409)
    if existing:
        existing.is_active = True
        existing.assigned_by_user_id = actor.id
        existing.assignment_reason = reason
    else:
        db.add(UserRole(user_id=target.id, role_id=role.id, assigned_by_user_id=actor.id, assignment_reason=reason))
    db.flush()
    new_roles = _role_names(db, target)
    _record_privilege_change(db, actor, target, "role.assign", previous_roles, new_roles, reason, request_id)
    record_audit_event(db, actor=actor, action="admin.user.role.assign", target_type="user", target_id=str(target.id), result="success", reason=reason, request_id=request_id, metadata={"previous_roles": previous_roles, "new_roles": new_roles}, commit=False)
    _record_sensitive_action(db, actor, "role.assign", "user", str(target.id), reason)
    db.commit()
    db.refresh(target)
    return target


def remove_role(db: Session, *, actor: User, target: User, role_id: int, reason: str, request_id: str | None = None) -> User:
    """Remove an active role assignment with audit and Owner protections."""
    reason = reason.strip()
    if not reason:
        raise AdminUserManagementError("A reason is required", "REASON_REQUIRED")
    role = get_role_or_raise(db, role_id)
    if actor.id == target.id:
        raise AdminUserManagementError("Administrators cannot change their own role assignments", "SELF_ROLE_CHANGE_BLOCKED", 409)
    if role.slug == OWNER_ROLE or role.is_owner_role:
        raise AdminUserManagementError("Owner role cannot be removed through normal workflows", "OWNER_ROLE_PROTECTED", 409)
    assignment = db.scalar(select(UserRole).where(UserRole.user_id == target.id, UserRole.role_id == role.id, UserRole.is_active.is_(True)))
    if assignment is None:
        raise AdminUserManagementError("User does not have this active role", "ROLE_ASSIGNMENT_NOT_FOUND", 404)

    previous_roles = _role_names(db, target)
    assignment.is_active = False
    db.flush()
    new_roles = _role_names(db, target)
    _record_privilege_change(db, actor, target, "role.remove", previous_roles, new_roles, reason, request_id)
    record_audit_event(db, actor=actor, action="admin.user.role.remove", target_type="user", target_id=str(target.id), result="success", reason=reason, request_id=request_id, metadata={"previous_roles": previous_roles, "new_roles": new_roles}, commit=False)
    _record_sensitive_action(db, actor, "role.remove", "user", str(target.id), reason)
    db.commit()
    db.refresh(target)
    return target


def update_user_status(db: Session, *, actor: User, target: User, status: UserStatus, reason: str, request_id: str | None = None) -> User:
    """Suspend or restore a user account."""
    reason = reason.strip()
    if not reason:
        raise AdminUserManagementError("A reason is required", "REASON_REQUIRED")
    if actor.id == target.id:
        raise AdminUserManagementError("Administrators cannot suspend or restore their own account", "SELF_STATUS_CHANGE_BLOCKED", 409)
    if status == "suspended" and is_owner(db, target):
        raise AdminUserManagementError("Owner cannot be suspended", "OWNER_PROTECTED", 409)
    if status == "suspended" and _is_last_active_admin(db, target):
        raise AdminUserManagementError("Cannot suspend the last active administrator", "LAST_ADMIN_PROTECTED", 409)

    previous_state = {"is_active": target.is_active, "suspended_at": _iso(target.suspended_at), "reason": target.suspension_reason}
    if status == "suspended":
        target.is_active = False
        target.suspended_at = datetime.now(UTC)
        target.suspension_reason = reason
        target.suspended_by_user_id = actor.id
        action = "status.suspend"
    else:
        target.is_active = True
        target.restored_at = datetime.now(UTC)
        target.restored_by_user_id = actor.id
        action = "status.restore"
    new_state = {"is_active": target.is_active, "suspended_at": _iso(target.suspended_at), "reason": target.suspension_reason}
    _record_privilege_change(db, actor, target, action, [json.dumps(previous_state)], [json.dumps(new_state)], reason, request_id)
    record_audit_event(db, actor=actor, action=f"admin.user.{action}", target_type="user", target_id=str(target.id), result="success", reason=reason, request_id=request_id, metadata={"previous_state": previous_state, "new_state": new_state}, commit=False)
    _record_sensitive_action(db, actor, action, "user", str(target.id), reason)
    db.commit()
    db.refresh(target)
    return target


def recent_user_audit(db: Session, user: User, limit: int = 10) -> list[AuditLog]:
    """Return recent audit events for a user as actor or target."""
    return list(
        db.scalars(
            select(AuditLog)
            .where(or_(AuditLog.actor_user_id == user.id, AuditLog.target_id == str(user.id)))
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        ).all()
    )


def _record_privilege_change(db: Session, actor: User, target: User, action: str, previous_roles: list[str], new_roles: list[str], reason: str, request_id: str | None) -> None:
    db.add(
        PrivilegeChangeHistory(
            actor_user_id=actor.id,
            target_user_id=target.id,
            action=action,
            previous_state=_json_roles(previous_roles),
            new_state=_json_roles(new_roles),
            reason=reason,
            result="success",
            request_id=request_id,
        )
    )
    role_lookup = {role.slug: role for role in list_roles(db)}
    changed = set(previous_roles).symmetric_difference(set(new_roles))
    for slug in changed:
        role = role_lookup.get(slug)
        if role:
            db.add(UserRoleHistory(user_id=target.id, role_id=role.id, actor_user_id=actor.id, action=action, reason=reason, previous_roles=_json_roles(previous_roles), new_roles=_json_roles(new_roles)))


def _record_sensitive_action(db: Session, actor: User, action: str, target_type: str, target_id: str, reason: str) -> None:
    db.add(SensitiveActionRequest(user_id=actor.id, action=action, target_type=target_type, target_id=target_id, status=SensitiveActionStatus.CONFIRMED.value, required_method="confirmation", confirmed_at=datetime.now(UTC), reason=reason))


def _is_last_active_admin(db: Session, target: User) -> bool:
    if not any(role.slug == ADMINISTRATOR_ROLE for role in get_user_roles(db, target)):
        return False
    active_admin_count = db.scalar(
        select(func.count())
        .select_from(UserRole)
        .join(Role, Role.id == UserRole.role_id)
        .join(User, User.id == UserRole.user_id)
        .where(Role.slug == ADMINISTRATOR_ROLE, UserRole.is_active.is_(True), User.is_active.is_(True))
    ) or 0
    return active_admin_count <= 1


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


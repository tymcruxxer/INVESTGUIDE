"""RBAC service for roles, permissions, and admin authorization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models.rbac import Permission, Role, RolePermission, UserRole
from app.models.user import User
from app.services.auth_service import get_current_user, hash_password

OWNER_ROLE = "owner"
ADMINISTRATOR_ROLE = "administrator"
USER_ROLE = "user"
OPERATIONS_ADMIN_ROLE = "operations-admin"
FINANCE_ADMIN_ROLE = "finance-admin"
SUPPORT_ADMIN_ROLE = "support-admin"
MODERATOR_ROLE = "moderator"

DEFAULT_ROLES: tuple[dict[str, object], ...] = (
    {"name": "Owner", "slug": OWNER_ROLE, "description": "Permanent platform owner with audited permission bypass.", "is_system_role": True, "is_owner_role": True},
    {"name": "Administrator", "slug": ADMINISTRATOR_ROLE, "description": "General administrator role for future admin modules.", "is_system_role": True, "is_owner_role": False},
    {"name": "Operations Admin", "slug": OPERATIONS_ADMIN_ROLE, "description": "Admin role for ingestion operations and source monitoring.", "is_system_role": True, "is_owner_role": False},
    {"name": "Finance Admin", "slug": FINANCE_ADMIN_ROLE, "description": "Admin role for financial intelligence review and analytics visibility.", "is_system_role": True, "is_owner_role": False},
    {"name": "Support Admin", "slug": SUPPORT_ADMIN_ROLE, "description": "Admin role for user support, account status, and audit inspection.", "is_system_role": True, "is_owner_role": False},
    {"name": "Moderator", "slug": MODERATOR_ROLE, "description": "Read-only moderation role for user and audit inspection.", "is_system_role": True, "is_owner_role": False},
    {"name": "User", "slug": USER_ROLE, "description": "Default authenticated user role.", "is_system_role": True, "is_owner_role": False},
)
DEFAULT_PERMISSIONS: tuple[dict[str, str], ...] = (
    {"code": "users.read", "name": "Read users", "category": "users", "description": "View user records."},
    {"code": "users.update", "name": "Update users", "category": "users", "description": "Update user records."},
    {"code": "users.delete", "name": "Delete users", "category": "users", "description": "Delete non-owner user records."},
    {"code": "roles.read", "name": "Read roles", "category": "roles", "description": "View roles and permissions."},
    {"code": "roles.update", "name": "Update roles", "category": "roles", "description": "Update non-owner roles."},
    {"code": "sources.read", "name": "Read sources", "category": "sources", "description": "View data source configuration."},
    {"code": "sources.update", "name": "Update sources", "category": "sources", "description": "Update data source configuration."},
    {"code": "connectors.read", "name": "Read connectors", "category": "connectors", "description": "View reusable connector definitions."},
    {"code": "connectors.update", "name": "Update connectors", "category": "connectors", "description": "Create, update, validate, and archive connector definitions."},`r`n    {"code": "runtime.read", "name": "Read runtime", "category": "runtime", "description": "View execution runtime definitions."},`r`n    {"code": "runtime.update", "name": "Update runtime", "category": "runtime", "description": "Create, update, validate, and archive runtime definitions."},
    {"code": "ingestion.read", "name": "Read ingestion", "category": "ingestion", "description": "View ingestion operations."},
    {"code": "ingestion.manage", "name": "Manage ingestion", "category": "ingestion", "description": "Operate ingestion workflows."},
    {"code": "analytics.read", "name": "Read analytics", "category": "analytics", "description": "View analytics outputs and diagnostics."},
    {"code": "system.read", "name": "Read system", "category": "system", "description": "View system settings and status."},
    {"code": "system.configure", "name": "Configure system", "category": "system", "description": "Configure system settings."},
    {"code": "audit.read", "name": "Read audit", "category": "audit", "description": "View audit logs."},
    {"code": "audit.export", "name": "Export audit", "category": "audit", "description": "Export audit records."},
)
ROLE_PERMISSION_MAP: dict[str, tuple[str, ...] | str] = {
    ADMINISTRATOR_ROLE: "*",
    OPERATIONS_ADMIN_ROLE: (
        "sources.read",
        "sources.update",
        "connectors.read",
        "connectors.update",`r`n        "runtime.read",`r`n        "runtime.update",`r`n        "ingestion.read",
        "ingestion.manage",
        "system.read",
        "audit.read",
    ),
    FINANCE_ADMIN_ROLE: (
        "analytics.read",
        "system.read",
        "audit.read",
    ),
    SUPPORT_ADMIN_ROLE: (
        "users.read",
        "users.update",
        "roles.read",
        "audit.read",
        "system.read",
    ),
    MODERATOR_ROLE: (
        "users.read",
        "roles.read",
        "audit.read",
        "system.read",
    ),
    USER_ROLE: (),
}

ADMIN_NAVIGATION: tuple[dict[str, str], ...] = (
    {"label": "Dashboard", "href": "/admin/dashboard", "permission": "system.read"},
    {"label": "Users", "href": "/admin/users", "permission": "users.read"},
    {"label": "Roles", "href": "/admin/roles", "permission": "roles.read"},
    {"label": "Connectors", "href": "/admin/connectors", "permission": "connectors.read"},`r`n    {"label": "Runtime", "href": "/admin/runtime", "permission": "runtime.read"},
    {"label": "Settings", "href": "/admin/settings", "permission": "system.configure"},
)


@dataclass(frozen=True)
class BootstrapResult:
    """Summary of RBAC bootstrap work."""

    roles_inserted: int
    permissions_inserted: int
    role_permissions_inserted: int
    owner_created: bool
    owner_assigned: bool


class PermissionDeniedError(PermissionError):
    """Raised when a user lacks a required permission."""


class OwnerProtectionError(PermissionError):
    """Raised when a normal workflow tries to alter the protected Owner."""


def normalize_permission(code: str) -> str:
    """Normalize permission codes for lookup."""
    return code.strip().lower()


def get_user_roles(db: Session, user: User) -> list[Role]:
    """Return active roles for a user."""
    return list(
        db.scalars(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id, UserRole.is_active.is_(True), Role.is_active.is_(True))
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
            .order_by(Role.id.asc())
        ).all()
    )


def is_owner(db: Session, user: User) -> bool:
    """Return whether the user has the protected Owner role."""
    return any(role.is_owner_role for role in get_user_roles(db, user))


def get_user_permission_codes(db: Session, user: User) -> set[str]:
    """Return effective permissions for a user.

    Owner bypasses normal permission checks while still being auditable, so the
    effective permission set includes all bootstrapped permissions.
    """
    roles = get_user_roles(db, user)
    if any(role.is_owner_role for role in roles):
        return {permission.code for permission in db.scalars(select(Permission)).all()}

    permissions: set[str] = set()
    for role in roles:
        for link in role.permissions:
            permissions.add(link.permission.code)
    return permissions


def user_has_permission(db: Session, user: User, permission_code: str) -> bool:
    """Return whether a user has a permission or Owner bypass."""
    code = normalize_permission(permission_code)
    return code in get_user_permission_codes(db, user)


def require_permission(permission_code: str):
    """FastAPI dependency factory enforcing a permission server-side."""

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_permission(db, current_user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' is required",
            )
        return current_user

    return dependency


def get_admin_context(db: Session, user: User) -> dict[str, object]:
    """Build admin-safe context for the authenticated user."""
    roles = get_user_roles(db, user)
    permissions = sorted(get_user_permission_codes(db, user))
    primary_role = next((role for role in roles if role.is_owner_role), roles[0] if roles else None)
    return {
        "user": user,
        "roles": roles,
        "permissions": permissions,
        "is_owner": any(role.is_owner_role for role in roles),
        "primary_role": primary_role,
    }


def assign_role_to_user(db: Session, user: User, role_slug: str, assigned_by: User | None = None, reason: str | None = None) -> bool:
    """Assign a role to a user if not already active."""
    role = db.scalar(select(Role).where(Role.slug == role_slug))
    if role is None:
        raise ValueError(f"Role '{role_slug}' does not exist")
    existing = db.scalar(select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id))
    if existing is not None:
        if not existing.is_active:
            existing.is_active = True
            return True
        return False
    db.add(UserRole(user_id=user.id, role_id=role.id, assigned_by_user_id=assigned_by.id if assigned_by else None, assignment_reason=reason))
    return True


def ensure_user_is_not_protected_owner(db: Session, user: User, action: str) -> None:
    """Block normal delete, suspend, and demotion flows for the Owner."""
    protected_actions = {"delete", "suspend", "demote"}
    if action.strip().lower() in protected_actions and is_owner(db, user):
        raise OwnerProtectionError(
            "Owner cannot be deleted, suspended, or demoted through normal workflows. "
            "Use the dedicated ownership-transfer workflow when it is implemented."
        )

def ensure_owner_protection(db: Session) -> None:
    """Ensure exactly one active Owner assignment exists."""
    owner_role = db.scalar(select(Role).where(Role.slug == OWNER_ROLE))
    if owner_role is None:
        raise RuntimeError("Owner role has not been bootstrapped")
    owner_count = db.scalar(
        select(func.count()).select_from(UserRole).where(UserRole.role_id == owner_role.id, UserRole.is_active.is_(True))
    ) or 0
    if owner_count != 1:
        raise RuntimeError("Exactly one active Owner assignment is required")


def bootstrap_rbac(
    db: Session,
    owner_email: str = "owner@investguide.local",
    owner_password: str = "ChangeMe123!",
) -> BootstrapResult:
    """Bootstrap system roles, permissions, role links, and a development Owner."""
    roles_inserted = 0
    permissions_inserted = 0
    role_permissions_inserted = 0

    roles_by_slug: dict[str, Role] = {}
    for role_data in DEFAULT_ROLES:
        role = db.scalar(select(Role).where(Role.slug == role_data["slug"]))
        if role is None:
            role = Role(**role_data)
            db.add(role)
            db.flush()
            roles_inserted += 1
        roles_by_slug[str(role_data["slug"])] = role

    permissions_by_code: dict[str, Permission] = {}
    for permission_data in DEFAULT_PERMISSIONS:
        permission = db.scalar(select(Permission).where(Permission.code == permission_data["code"]))
        if permission is None:
            permission = Permission(**permission_data)
            db.add(permission)
            db.flush()
            permissions_inserted += 1
        permissions_by_code[str(permission_data["code"])] = permission

    for role_slug, permission_codes in ROLE_PERMISSION_MAP.items():
        role = roles_by_slug[role_slug]
        resolved_codes = tuple(permissions_by_code.keys()) if permission_codes == "*" else permission_codes
        for permission_code in resolved_codes:
            permission = permissions_by_code[str(permission_code)]
            existing = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
            if existing is None:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))
                role_permissions_inserted += 1
    owner = db.scalar(select(User).where(User.email == owner_email.strip().lower()))
    owner_created = False
    if owner is None:
        owner = User(email=owner_email.strip().lower(), username="owner", hashed_password=hash_password(owner_password), is_active=True, is_verified=True)
        db.add(owner)
        db.flush()
        owner_created = True

    owner_assigned = assign_role_to_user(db, owner, OWNER_ROLE, reason="Development Owner bootstrap")
    assign_role_to_user(db, owner, ADMINISTRATOR_ROLE, reason="Development Owner bootstrap")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    ensure_owner_protection(db)
    return BootstrapResult(
        roles_inserted=roles_inserted,
        permissions_inserted=permissions_inserted,
        role_permissions_inserted=role_permissions_inserted,
        owner_created=owner_created,
        owner_assigned=owner_assigned,
    )


def filter_navigation_for_user(db: Session, user: User, items: Iterable[dict[str, str]] = ADMIN_NAVIGATION) -> list[dict[str, str]]:
    """Return admin navigation entries visible to the user."""
    permission_codes = get_user_permission_codes(db, user)
    return [dict(item) for item in items if item["permission"] in permission_codes]










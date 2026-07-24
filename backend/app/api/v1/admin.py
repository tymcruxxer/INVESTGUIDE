"""Secure administration endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.audit import AuditLog
from app.models.rbac import Permission, Role, RolePermission
from app.models.user import User
from app.schemas.admin import (
    AdminMe,
    AdminNavigationItem,
    AdminPermissionsPayload,
    AdminUserDetail,
    AdminUserListPayload,
    AdminUserSummary,
    PermissionRead,
    RoleAssignmentRequest,
    RoleRead,
    UserStatusRequest,
)
from app.schemas.auth import UserRead
from app.schemas.source_registry import SourceCreate, SourceStatusUpdate, SourceUpdate
from app.services import admin_user_service, source_registry_service
from app.services.admin_user_service import AdminUserManagementError
from app.services.audit_service import record_audit_event
from app.services.source_registry_service import SourceRegistryError
from app.services.rbac_service import filter_navigation_for_user, get_admin_context, get_user_permission_codes, get_user_roles, require_permission

router = APIRouter(prefix="/admin", tags=["admin"])


def _request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _permission(permission: Permission) -> PermissionRead:
    return PermissionRead.model_validate(permission)


def _role(role: Role) -> RoleRead:
    active_user_count = len([assignment for assignment in role.users if assignment.is_active]) if role.users else 0
    permissions = [_permission(link.permission) for link in role.permissions if link.permission]
    return RoleRead(
        id=role.id,
        name=role.name,
        slug=role.slug,
        description=role.description,
        is_system_role=role.is_system_role,
        is_owner_role=role.is_owner_role,
        is_active=role.is_active,
        assigned_user_count=active_user_count,
        permissions=permissions,
    )


def _safe_user_summary(db: Session, user: User) -> AdminUserSummary:
    roles = [role.slug for role in get_user_roles(db, user)]
    return AdminUserSummary(
        id=user.id,
        email=user.email,
        username=user.username,
        display_name=user.username or user.email.split("@", 1)[0],
        roles=roles,
        is_active=user.is_active,
        is_verified=user.is_verified,
        status="active" if user.is_active else "suspended",
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        suspended_at=user.suspended_at,
    )


def _audit_item(event: AuditLog) -> dict[str, Any]:
    return {
        "id": event.id,
        "action": event.action,
        "target_type": event.target_type,
        "target_id": event.target_id,
        "result": event.result,
        "reason": event.reason,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _safe_user_detail(db: Session, user: User) -> AdminUserDetail:
    summary = _safe_user_summary(db, user).model_dump()
    audits = admin_user_service.recent_user_audit(db, user)
    return AdminUserDetail(
        **summary,
        permissions=sorted(get_user_permission_codes(db, user)),
        activity_summary={
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "recent_logins": 1 if user.last_login_at else 0,
            "recent_admin_actions": len(audits),
        },
        audit_summary=[_audit_item(event) for event in audits],
        suspension_reason=user.suspension_reason,
        restored_at=user.restored_at,
    )


def _serialize_admin_context(db: Session, user: User) -> dict[str, Any]:
    context = get_admin_context(db, user)
    return AdminMe(
        user=UserRead.model_validate(context["user"]),
        roles=[_role(role) for role in context["roles"]],
        permissions=list(context["permissions"]),
        is_owner=bool(context["is_owner"]),
        primary_role=_role(context["primary_role"]) if context["primary_role"] else None,
    ).model_dump(mode="json")


def _management_error(exc: AdminUserManagementError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_response(message=exc.message, error_code=exc.error_code))


@router.get("/me", response_model=None)
async def admin_me(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("system.read"))) -> dict[str, Any]:
    """Return authenticated administrator context."""
    record_audit_event(db, actor=current_user, action="admin.me.read", target_type="admin_context", target_id=str(current_user.id), ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    return success_response(message="Admin context retrieved successfully", data=_serialize_admin_context(db, current_user))


@router.get("/navigation", response_model=None)
async def admin_navigation(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("system.read"))) -> dict[str, Any]:
    """Return navigation entries available to the authenticated administrator."""
    record_audit_event(db, actor=current_user, action="admin.navigation.read", target_type="admin_navigation", target_id=str(current_user.id), ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    items = [AdminNavigationItem(**item).model_dump(mode="json") for item in filter_navigation_for_user(db, current_user)]
    return success_response(message="Admin navigation retrieved successfully", data={"items": items, "mode": "admin"})


@router.get("/users", response_model=None)
async def admin_users(
    request: Request,
    search: str | None = None,
    status: str | None = Query(default=None, pattern="^(active|suspended)$"),
    verified: bool | None = None,
    role: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users.read")),
) -> dict[str, Any]:
    """Return the admin user directory."""
    result = admin_user_service.list_users(db, search=search, status=status, verified=verified, role=role, sort_by=sort_by, sort_order=sort_order, page=page, limit=limit)
    record_audit_event(db, actor=current_user, action="admin.users.read", target_type="users", target_id="directory", ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    payload = AdminUserListPayload(
        users=[_safe_user_summary(db, user) for user in result.users],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
    )
    return success_response(message="Admin user directory retrieved successfully", data=payload.model_dump(mode="json"))


@router.get("/users/{user_id}", response_model=None)
async def admin_user_detail(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("users.read"))) -> dict[str, Any] | JSONResponse:
    """Return one admin-safe user detail payload."""
    try:
        user = admin_user_service.get_user_or_raise(db, user_id)
    except AdminUserManagementError as exc:
        return _management_error(exc)
    record_audit_event(db, actor=current_user, action="admin.user.read", target_type="user", target_id=str(user.id), ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    return success_response(message="Admin user retrieved successfully", data=_safe_user_detail(db, user).model_dump(mode="json"))


@router.patch("/users/{user_id}/roles", response_model=None)
async def admin_user_roles(user_id: int, payload: RoleAssignmentRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("roles.update"))) -> dict[str, Any] | JSONResponse:
    """Assign or remove a user role."""
    if not payload.confirmation:
        return JSONResponse(status_code=400, content=error_response(message="Confirmation is required", error_code="CONFIRMATION_REQUIRED"))
    try:
        target = admin_user_service.get_user_or_raise(db, user_id)
        user = admin_user_service.assign_role(db, actor=current_user, target=target, role_id=payload.role_id, reason=payload.reason, request_id=_request_id(request)) if payload.action == "assign" else admin_user_service.remove_role(db, actor=current_user, target=target, role_id=payload.role_id, reason=payload.reason, request_id=_request_id(request))
    except AdminUserManagementError as exc:
        return _management_error(exc)
    return success_response(message="User roles updated successfully", data=_safe_user_detail(db, user).model_dump(mode="json"))


@router.patch("/users/{user_id}/status", response_model=None)
async def admin_user_status(user_id: int, payload: UserStatusRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("users.update"))) -> dict[str, Any] | JSONResponse:
    """Suspend or restore a user account."""
    if not payload.confirmation:
        return JSONResponse(status_code=400, content=error_response(message="Confirmation is required", error_code="CONFIRMATION_REQUIRED"))
    try:
        target = admin_user_service.get_user_or_raise(db, user_id)
        user = admin_user_service.update_user_status(db, actor=current_user, target=target, status=payload.status, reason=payload.reason, request_id=_request_id(request))
    except AdminUserManagementError as exc:
        return _management_error(exc)
    return success_response(message="User status updated successfully", data=_safe_user_detail(db, user).model_dump(mode="json"))



@router.get("/sources", response_model=None)
async def admin_sources(
    request: Request,
    search: str | None = None,
    category: str | None = None,
    tier: str | None = None,
    status: str | None = None,
    connector_type: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sources.read")),
) -> dict[str, Any]:
    """Return the source registry list."""
    result = source_registry_service.list_sources(db, search=search, category=category, tier=tier, status=status, connector_type=connector_type, page=page, limit=limit, sort_by=sort_by, sort_order=sort_order)
    record_audit_event(db, actor=current_user, action="admin.sources.read", target_type="source", target_id="registry", ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    return success_response(message="Source registry retrieved successfully", data=source_registry_service.source_list_payload(result).model_dump(mode="json"))


@router.post("/sources", response_model=None)
async def admin_source_create(payload: SourceCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("sources.update"))) -> dict[str, Any] | JSONResponse:
    """Create a data source registry entry."""
    try:
        source = source_registry_service.create_source(db, actor=current_user, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except SourceRegistryError as exc:
        return _source_error(exc)
    return success_response(message="Source created successfully", data=source_registry_service.source_to_read(db, source).model_dump(mode="json"))


@router.get("/sources/{source_id}", response_model=None)
async def admin_source_detail(source_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("sources.read"))) -> dict[str, Any] | JSONResponse:
    """Return one source registry entry."""
    try:
        source = source_registry_service.get_source_or_raise(db, source_id)
    except SourceRegistryError as exc:
        return _source_error(exc)
    record_audit_event(db, actor=current_user, action="admin.source.read", target_type="source", target_id=str(source.id), ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    return success_response(message="Source retrieved successfully", data=source_registry_service.source_to_read(db, source).model_dump(mode="json"))


@router.patch("/sources/{source_id}", response_model=None)
async def admin_source_update(source_id: int, payload: SourceUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("sources.update"))) -> dict[str, Any] | JSONResponse:
    """Update source identity, connector configuration, or credentials."""
    try:
        source = source_registry_service.get_source_or_raise(db, source_id)
        updated = source_registry_service.update_source(db, actor=current_user, source=source, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except SourceRegistryError as exc:
        return _source_error(exc)
    return success_response(message="Source updated successfully", data=source_registry_service.source_to_read(db, updated).model_dump(mode="json"))


@router.patch("/sources/{source_id}/status", response_model=None)
async def admin_source_status(source_id: int, payload: SourceStatusUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("sources.update"))) -> dict[str, Any] | JSONResponse:
    """Update source operational status."""
    try:
        source = source_registry_service.get_source_or_raise(db, source_id)
        updated = source_registry_service.update_source_status(db, actor=current_user, source=source, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except SourceRegistryError as exc:
        return _source_error(exc)
    return success_response(message="Source status updated successfully", data=source_registry_service.source_to_read(db, updated).model_dump(mode="json"))


@router.delete("/sources/{source_id}", response_model=None)
async def admin_source_delete(source_id: int, request: Request, reason: str = Query(min_length=3, max_length=1000), db: Session = Depends(get_db), current_user: User = Depends(require_permission("sources.update"))) -> dict[str, Any] | JSONResponse:
    """Soft-delete a source registry entry."""
    try:
        source = source_registry_service.get_source_or_raise(db, source_id)
        deleted = source_registry_service.soft_delete_source(db, actor=current_user, source=source, reason=reason, request_id=_request_id(request), ip_address=_request_ip(request))
    except SourceRegistryError as exc:
        return _source_error(exc)
    return success_response(message="Source soft-deleted successfully", data=source_registry_service.source_to_read(db, deleted).model_dump(mode="json"))

@router.get("/roles", response_model=None)
async def admin_roles(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("roles.read"))) -> dict[str, Any]:
    """Return the role catalog with inherited permissions."""
    record_audit_event(db, actor=current_user, action="admin.roles.read", target_type="roles", target_id="all", ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    roles = [_role(role) for role in admin_user_service.list_roles(db)]
    return success_response(message="Admin roles retrieved successfully", data=[role.model_dump(mode="json") for role in roles])


@router.get("/roles/{role_id}", response_model=None)
async def admin_role_detail(role_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("roles.read"))) -> dict[str, Any] | JSONResponse:
    """Return one role with inherited permission descriptions."""
    try:
        role = admin_user_service.get_role_or_raise(db, role_id)
    except AdminUserManagementError as exc:
        return _management_error(exc)
    record_audit_event(db, actor=current_user, action="admin.role.read", target_type="role", target_id=str(role.id), ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    return success_response(message="Admin role retrieved successfully", data=_role(role).model_dump(mode="json"))


@router.get("/permissions", response_model=None)
async def admin_permissions(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("roles.read"))) -> dict[str, Any]:
    """Return roles and permissions visible to the authenticated administrator."""
    permissions = list(db.scalars(select(Permission).order_by(Permission.category.asc(), Permission.code.asc())).all())
    roles = admin_user_service.list_roles(db)
    admin_context = get_admin_context(db, current_user)
    grouped: dict[str, list[PermissionRead]] = {}
    for permission in permissions:
        grouped.setdefault(permission.category, []).append(PermissionRead.model_validate(permission))
    record_audit_event(db, actor=current_user, action="admin.permissions.read", target_type="permissions", target_id="all", ip_address=_request_ip(request), request_id=_request_id(request), commit=True)
    payload = AdminPermissionsPayload(
        permissions=[PermissionRead.model_validate(permission) for permission in permissions],
        grouped_permissions=grouped,
        roles=[_role(role) for role in roles],
        user_permissions=list(admin_context["permissions"]),
        owner_bypass=bool(admin_context["is_owner"]),
        generated_at=datetime.now(UTC),
        metadata={"environment": get_settings().environment, "permission_model": "rbac", "owner_transfer_workflow": "not_implemented"},
    ).model_dump(mode="json")
    return success_response(message="Admin permissions retrieved successfully", data=payload)









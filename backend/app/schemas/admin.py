"""Admin API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import UserRead


class PermissionRead(BaseModel):
    """Permission response shape."""

    id: int
    code: str
    name: str
    category: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    """Role response shape."""

    id: int
    name: str
    slug: str
    description: str | None = None
    is_system_role: bool
    is_owner_role: bool
    is_active: bool
    assigned_user_count: int = 0
    permissions: list[PermissionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AdminUserSummary(BaseModel):
    """Safe user directory row."""

    id: int
    email: str
    username: str | None = None
    display_name: str
    roles: list[str]
    is_active: bool
    is_verified: bool
    status: Literal["active", "suspended"]
    created_at: datetime
    last_login_at: datetime | None = None
    suspended_at: datetime | None = None
    subscription_tier: str = "future"


class AdminUserDetail(AdminUserSummary):
    """Safe user detail payload."""

    permissions: list[str]
    activity_summary: dict[str, Any]
    audit_summary: list[dict[str, Any]]
    suspension_reason: str | None = None
    restored_at: datetime | None = None


class AdminUserListPayload(BaseModel):
    """Paginated user directory payload."""

    users: list[AdminUserSummary]
    total: int
    page: int
    limit: int
    has_next: bool = False
    has_prev: bool = False


class RoleAssignmentRequest(BaseModel):
    """Role assignment/removal request."""

    role_id: int = Field(gt=0)
    action: Literal["assign", "remove"]
    reason: str = Field(min_length=3, max_length=1000)
    confirmation: bool = True

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise ValueError("A reason is required")
        return reason


class UserStatusRequest(BaseModel):
    """User account status request."""

    status: Literal["active", "suspended"]
    reason: str = Field(min_length=3, max_length=1000)
    confirmation: bool = True

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise ValueError("A reason is required")
        return reason


class AdminMe(BaseModel):
    """Admin context response shape."""

    user: UserRead
    roles: list[RoleRead]
    permissions: list[str]
    is_owner: bool
    primary_role: RoleRead | None
    mode: str = "admin"


class AdminNavigationItem(BaseModel):
    """Admin navigation item."""

    label: str
    href: str
    permission: str


class SensitiveActionRequirement(BaseModel):
    """Future sensitive-action capability descriptor."""

    reauthentication_supported: bool = True
    mfa_supported: bool = True
    confirmation_workflows_supported: bool = True
    implemented: bool = False


class AuditCapability(BaseModel):
    """Audit capability descriptor."""

    records_actor: bool = True
    records_action: bool = True
    records_target: bool = True
    records_timestamp: bool = True
    records_ip_address: bool = True
    records_request_id: bool = True
    records_result: bool = True
    records_reason: bool = True


class AdminPermissionsPayload(BaseModel):
    """Permissions endpoint payload."""

    permissions: list[PermissionRead]
    grouped_permissions: dict[str, list[PermissionRead]]
    roles: list[RoleRead]
    user_permissions: list[str]
    owner_bypass: bool
    audit: AuditCapability = Field(default_factory=AuditCapability)
    sensitive_actions: SensitiveActionRequirement = Field(default_factory=SensitiveActionRequirement)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)





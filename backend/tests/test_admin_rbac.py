"""RBAC and administration foundation tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import AuditLog, Permission, Role, RolePermission, SensitiveActionRequest, UserRole
from app.schemas.auth import UserCreate
from app.services.audit_service import record_audit_event
from app.services.auth_service import create_access_token, register_user
from app.services.rbac_service import (
    ADMINISTRATOR_ROLE,
    DEFAULT_PERMISSIONS,
    OWNER_ROLE,
    OwnerProtectionError,
    USER_ROLE,
    assign_role_to_user,
    bootstrap_rbac,
    ensure_owner_protection,
    ensure_user_is_not_protected_owner,
    filter_navigation_for_user,
    get_user_permission_codes,
    is_owner,
    user_has_permission,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Provide a TestClient with database dependency overridden."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _token_for(user) -> str:
    return create_access_token(user)


def test_rbac_model_metadata() -> None:
    """RBAC and audit tables are registered in SQLAlchemy metadata."""
    tables = Base.metadata.tables

    assert "roles" in tables
    assert "permissions" in tables
    assert "role_permissions" in tables
    assert "user_roles" in tables
    assert "audit_logs" in tables
    assert "sensitive_action_requests" in tables
    assert any(column.name == "is_owner_role" for column in Role.__table__.columns)
    assert any(column.name == "metadata_json" for column in AuditLog.__table__.columns)
    assert any(column.name == "confirmation_token_hash" for column in SensitiveActionRequest.__table__.columns)


def test_bootstrap_rbac_creates_roles_permissions_and_exactly_one_owner(db_session: Session) -> None:
    """Bootstrap seeds system roles, permissions, and a single protected Owner."""
    result = bootstrap_rbac(db_session)

    assert result.roles_inserted >= 3
    assert result.permissions_inserted == len(DEFAULT_PERMISSIONS)
    assert {OWNER_ROLE, ADMINISTRATOR_ROLE, USER_ROLE}.issubset({role.slug for role in db_session.scalars(select(Role)).all()})
    owner_role = db_session.scalar(select(Role).where(Role.slug == OWNER_ROLE))
    assert owner_role is not None and owner_role.is_owner_role is True
    owner_assignments = db_session.scalars(select(UserRole).where(UserRole.role_id == owner_role.id)).all()
    assert len(owner_assignments) == 1
    ensure_owner_protection(db_session)


def test_bootstrap_rbac_is_idempotent(db_session: Session) -> None:
    """Running bootstrap repeatedly does not create duplicate roles or owners."""
    bootstrap_rbac(db_session)
    second = bootstrap_rbac(db_session)

    assert second.roles_inserted == 0
    assert second.permissions_inserted == 0
    assert db_session.scalar(select(Role).where(Role.slug == OWNER_ROLE)) is not None
    assert len(db_session.scalars(select(UserRole)).all()) == 2


def test_owner_bypasses_permission_checks(db_session: Session) -> None:
    """Owner has effective access to all bootstrapped permissions."""
    bootstrap_rbac(db_session)
    owner = db_session.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user

    assert is_owner(db_session, owner) is True
    assert user_has_permission(db_session, owner, "system.configure") is True
    assert user_has_permission(db_session, owner, "audit.export") is True
    assert set(get_user_permission_codes(db_session, owner)) == {permission["code"] for permission in DEFAULT_PERMISSIONS}


def test_non_admin_user_has_no_admin_navigation(db_session: Session) -> None:
    """Regular users do not receive admin navigation by default."""
    bootstrap_rbac(db_session)
    user = register_user(db_session, UserCreate(email="user@example.com", password="password123"))
    assign_role_to_user(db_session, user, USER_ROLE)
    db_session.commit()

    assert get_user_permission_codes(db_session, user) == set()
    assert filter_navigation_for_user(db_session, user) == []


def test_administrator_receives_configured_permissions(db_session: Session) -> None:
    """Administrator receives role permissions configured during bootstrap."""
    bootstrap_rbac(db_session)
    admin = register_user(db_session, UserCreate(email="admin@example.com", password="password123"))
    assign_role_to_user(db_session, admin, ADMINISTRATOR_ROLE)
    db_session.commit()

    assert user_has_permission(db_session, admin, "system.read") is True
    assert user_has_permission(db_session, admin, "roles.read") is True
    assert filter_navigation_for_user(db_session, admin)


def test_audit_event_records_actor_action_target_and_result(db_session: Session) -> None:
    """Audit helper stores privileged action context."""
    user = register_user(db_session, UserCreate(email="auditor@example.com", password="password123"))

    event = record_audit_event(
        db_session,
        actor=user,
        action="admin.test",
        target_type="permission",
        target_id="system.read",
        result="success",
        reason="test coverage",
        ip_address="127.0.0.1",
        request_id="req-test",
    )

    assert event.id == 1
    assert event.actor_user_id == user.id
    assert event.action == "admin.test"
    assert event.target_id == "system.read"
    assert event.result == "success"


def test_admin_routes_are_registered() -> None:
    """Admin routes are mounted under the versioned API."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/admin/me" in routes
    assert "/api/v1/admin/navigation" in routes
    assert "/api/v1/admin/permissions" in routes


def test_admin_me_requires_authentication(client: TestClient) -> None:
    """Admin endpoints require an authenticated bearer token."""
    response = client.get("/api/v1/admin/me")

    assert response.status_code == 401
    assert response.json()["success"] is False


def test_admin_me_rejects_user_without_permission(client: TestClient, db_session: Session) -> None:
    """Authenticated regular users cannot enter admin mode."""
    bootstrap_rbac(db_session)
    user = register_user(db_session, UserCreate(email="regular@example.com", password="password123"))

    response = client.get("/api/v1/admin/me", headers={"Authorization": f"Bearer {_token_for(user)}"})

    assert response.status_code == 403
    assert response.json()["success"] is False


def test_admin_me_returns_owner_context_and_audits(client: TestClient, db_session: Session) -> None:
    """Owner can read admin context and the read is audited."""
    bootstrap_rbac(db_session)
    owner = db_session.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user

    response = client.get("/api/v1/admin/me", headers={"Authorization": f"Bearer {_token_for(owner)}"})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["is_owner"] is True
    assert body["data"]["primary_role"]["slug"] == OWNER_ROLE
    assert "system.read" in body["data"]["permissions"]
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "admin.me.read")) is not None


def test_admin_navigation_filters_by_permissions(client: TestClient, db_session: Session) -> None:
    """Admin navigation returns only entries allowed by permissions."""
    bootstrap_rbac(db_session)
    owner = db_session.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user

    response = client.get("/api/v1/admin/navigation", headers={"Authorization": f"Bearer {_token_for(owner)}"})
    body = response.json()

    assert response.status_code == 200
    assert [item["href"] for item in body["data"]["items"]] == ["/admin/dashboard", "/admin/users", "/admin/roles", "/admin/settings"]


def test_admin_permissions_returns_grouped_permission_model(client: TestClient, db_session: Session) -> None:
    """Permissions endpoint exposes grouped permission metadata to administrators."""
    bootstrap_rbac(db_session)
    owner = db_session.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user

    response = client.get("/api/v1/admin/permissions", headers={"Authorization": f"Bearer {_token_for(owner)}"})
    body = response.json()

    assert response.status_code == 200
    assert body["data"]["owner_bypass"] is True
    assert "system" in body["data"]["grouped_permissions"]
    assert any(permission["code"] == "system.configure" for permission in body["data"]["permissions"])
    assert any(role["slug"] == OWNER_ROLE for role in body["data"]["roles"])


def test_owner_protection_blocks_normal_destructive_actions(db_session: Session) -> None:
    """Normal workflows cannot delete, suspend, or demote the Owner."""
    bootstrap_rbac(db_session)
    owner = db_session.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user

    with pytest.raises(OwnerProtectionError):
        ensure_user_is_not_protected_owner(db_session, owner, "delete")

    with pytest.raises(OwnerProtectionError):
        ensure_user_is_not_protected_owner(db_session, owner, "suspend")

    with pytest.raises(OwnerProtectionError):
        ensure_user_is_not_protected_owner(db_session, owner, "demote")


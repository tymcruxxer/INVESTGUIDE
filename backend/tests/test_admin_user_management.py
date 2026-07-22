"""Admin user-management API and seed tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.seed_admin_users import seed_admin_users
from app.database.session import get_db
from app.main import app
from app.models import PrivilegeChangeHistory, Role, User, UserRole, UserRoleHistory
from app.schemas.auth import UserCreate
from app.services.auth_service import create_access_token, register_user
from app.services.rbac_service import ADMINISTRATOR_ROLE, OWNER_ROLE, SUPPORT_ADMIN_ROLE, bootstrap_rbac


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _owner(db: Session) -> User:
    return db.scalar(select(UserRole).join(Role).where(Role.slug == OWNER_ROLE)).user


def _token(user: User) -> str:
    return create_access_token(user)


def _create_target_user(db: Session, email: str = "target@example.com") -> User:
    return register_user(db, UserCreate(email=email, password="password123"))


def test_admin_user_routes_are_registered() -> None:
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/admin/users" in routes
    assert "/api/v1/admin/users/{user_id}" in routes
    assert "/api/v1/admin/users/{user_id}/roles" in routes
    assert "/api/v1/admin/users/{user_id}/status" in routes
    assert "/api/v1/admin/roles" in routes
    assert "/api/v1/admin/roles/{role_id}" in routes


def test_admin_user_directory_lists_safe_user_data(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    target = _create_target_user(db_session)
    owner = _owner(db_session)

    response = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {_token(owner)}"})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["total"] >= 2
    listed = next(user for user in body["data"]["users"] if user["id"] == target.id)
    assert listed["email"] == target.email
    assert "hashed_password" not in listed
    assert listed["subscription_tier"] == "future"


def test_admin_role_assignment_rejects_duplicates_and_records_history(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    target = _create_target_user(db_session)
    support_role = db_session.scalar(select(Role).where(Role.slug == SUPPORT_ADMIN_ROLE))

    first = client.patch(
        f"/api/v1/admin/users/{target.id}/roles",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"role_id": support_role.id, "action": "assign", "reason": "Support coverage", "confirmation": True},
    )
    duplicate = client.patch(
        f"/api/v1/admin/users/{target.id}/roles",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"role_id": support_role.id, "action": "assign", "reason": "Duplicate check", "confirmation": True},
    )

    assert first.status_code == 200
    assert "support-admin" in first.json()["data"]["roles"]
    assert duplicate.status_code == 409
    assert db_session.scalar(select(PrivilegeChangeHistory).where(PrivilegeChangeHistory.action == "role.assign")) is not None
    assert db_session.scalar(select(UserRoleHistory).where(UserRoleHistory.action == "role.assign")) is not None


def test_admin_cannot_assign_or_remove_owner_role(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    target = _create_target_user(db_session)
    owner_role = db_session.scalar(select(Role).where(Role.slug == OWNER_ROLE))

    response = client.patch(
        f"/api/v1/admin/users/{target.id}/roles",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"role_id": owner_role.id, "action": "assign", "reason": "Try owner", "confirmation": True},
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "OWNER_ROLE_PROTECTED"


def test_admin_status_update_blocks_owner_and_allows_restore(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    target = _create_target_user(db_session)

    blocked = client.patch(
        f"/api/v1/admin/users/{owner.id}/status",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"status": "suspended", "reason": "Should fail", "confirmation": True},
    )
    suspended = client.patch(
        f"/api/v1/admin/users/{target.id}/status",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"status": "suspended", "reason": "Policy review", "confirmation": True},
    )
    restored = client.patch(
        f"/api/v1/admin/users/{target.id}/status",
        headers={"Authorization": f"Bearer {_token(owner)}"},
        json={"status": "active", "reason": "Review complete", "confirmation": True},
    )

    assert blocked.status_code == 409
    assert suspended.status_code == 200
    assert suspended.json()["data"]["status"] == "suspended"
    assert restored.status_code == 200
    assert restored.json()["data"]["status"] == "active"


def test_admin_role_catalog_exposes_permission_metadata(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)

    response = client.get("/api/v1/admin/roles", headers={"Authorization": f"Bearer {_token(owner)}"})
    roles = response.json()["data"]

    assert response.status_code == 200
    assert any(role["slug"] == ADMINISTRATOR_ROLE and role["permissions"] for role in roles)
    assert any(role["slug"] == SUPPORT_ADMIN_ROLE for role in roles)


def test_admin_sample_seed_is_idempotent(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    bootstrap_rbac(db_session)

    first = seed_admin_users(db_session)
    second = seed_admin_users(db_session)

    assert first.inserted >= 5
    assert second.inserted == 0
    assert second.skipped >= 5
    assert db_session.scalar(select(User).where(User.email == "support@investguide.local")) is not None


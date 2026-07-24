"""Data Source Registry admin API and service tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.seed_sources import seed_sources
from app.database.session import get_db
from app.main import app
from app.models import AuditLog, Source, SourceCredential, SourceStatus, SourceVersion, User
from app.models.rbac import Role, UserRole
from app.schemas.auth import UserCreate
from app.schemas.source_registry import SourceCreate
from app.services.auth_service import create_access_token, register_user
from app.services.rbac_service import OWNER_ROLE, bootstrap_rbac


@pytest.fixture()
def db_session(monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    monkeypatch.setenv("APP_ENV", "development")
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
    return db.scalar(select(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(Role.slug == OWNER_ROLE))


def _auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user)}"}


def _source_payload(name: str = "test_source") -> dict[str, object]:
    return {
        "name": name,
        "display_name": "Test Source",
        "description": "A controlled test source.",
        "category": "market",
        "tier": "tier_1",
        "organization": "Test Org",
        "classification": "test",
        "supported_capabilities": ["market_prices", "dividends", "market_prices"],
        "connector_type": "rest_api",
        "authentication_type": "api_key",
        "status": "disabled",
        "configuration": {
            "base_url": "https://example.com",
            "refresh_policy": "daily",
            "timeout_seconds": 20,
            "retry_count": 2,
            "rate_limit_per_minute": 60,
            "parser": {"kind": "json"},
            "connector_config": {"endpoint": "/data"},
        },
        "credentials": [{"key": "api_key", "label": "API key", "secret_type": "api_key", "secret_value": "super-secret"}],
        "reason": "test setup",
    }


def test_source_registry_model_metadata() -> None:
    tables = Base.metadata.tables

    assert "sources" in tables
    assert "source_configurations" in tables
    assert "source_credentials" in tables
    assert "source_versions" in tables
    assert any(column.name == "encrypted_value" for column in SourceCredential.__table__.columns)
    assert any(column.name == "supported_capabilities" for column in Source.__table__.columns)


def test_source_routes_are_registered() -> None:
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/admin/sources" in routes
    assert "/api/v1/admin/sources/{source_id}" in routes
    assert "/api/v1/admin/sources/{source_id}/status" in routes


def test_source_create_masks_credentials_and_records_audit(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)

    response = client.post("/api/v1/admin/sources", headers=_auth(owner), json=_source_payload())
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["supported_capabilities"] == ["dividends", "market_prices"]
    assert body["data"]["credentials"][0]["masked_value"] == "********"
    assert "super-secret" not in str(body)
    credential = db_session.scalar(select(SourceCredential).where(SourceCredential.key == "api_key"))
    assert credential is not None
    assert credential.encrypted_value != "super-secret"
    assert db_session.scalar(select(SourceVersion).where(SourceVersion.change_type == "create")) is not None
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "admin.source.create")) is not None


def test_source_list_supports_search_and_filters(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    client.post("/api/v1/admin/sources", headers=_auth(owner), json=_source_payload("alpha_source"))
    client.post("/api/v1/admin/sources", headers=_auth(owner), json={**_source_payload("news_source"), "category": "news", "tier": "tier_3", "connector_type": "rss"})

    response = client.get("/api/v1/admin/sources", headers=_auth(owner), params={"search": "news", "category": "news", "tier": "tier_3", "connector_type": "rss"})
    data = response.json()["data"]

    assert response.status_code == 200
    assert data["total"] == 1
    assert data["sources"][0]["name"] == "news_source"


def test_source_update_status_and_soft_delete(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    created = client.post("/api/v1/admin/sources", headers=_auth(owner), json=_source_payload("status_source")).json()["data"]

    status_response = client.patch(f"/api/v1/admin/sources/{created['id']}/status", headers=_auth(owner), json={"status": "maintenance", "reason": "maintenance window"})
    delete_response = client.delete(f"/api/v1/admin/sources/{created['id']}", headers=_auth(owner), params={"reason": "retired source"})
    list_response = client.get("/api/v1/admin/sources", headers=_auth(owner))
    source = db_session.get(Source, created["id"])

    assert status_response.status_code == 200
    assert status_response.json()["data"]["status"] == "maintenance"
    assert delete_response.status_code == 200
    assert source.status == SourceStatus.DELETED.value
    assert all(item["id"] != created["id"] for item in list_response.json()["data"]["sources"])


def test_source_update_replaces_secret_without_exposing_value(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    created = client.post("/api/v1/admin/sources", headers=_auth(owner), json=_source_payload("update_source")).json()["data"]

    response = client.patch(
        f"/api/v1/admin/sources/{created['id']}",
        headers=_auth(owner),
        json={
            "display_name": "Updated Source",
            "tier": "tier_2",
            "configuration": {"base_url": "https://updated.example.com", "refresh_policy": "weekly"},
            "credentials": [{"key": "api_key", "label": "Updated API key", "secret_type": "api_key", "secret_value": "new-secret"}],
            "reason": "rotation",
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["data"]["display_name"] == "Updated Source"
    assert body["data"]["supported_capabilities"] == ["dividends", "market_prices"]
    assert body["data"]["credentials"][0]["masked_value"] == "********"
    assert "new-secret" not in str(body)
    assert db_session.scalar(select(SourceVersion).where(SourceVersion.change_type == "update")) is not None


def test_source_registry_requires_authorization(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    user = register_user(db_session, UserCreate(email="regular-source@example.com", password="password123"))

    response = client.get("/api/v1/admin/sources", headers=_auth(user))

    assert response.status_code == 403
    assert response.json()["success"] is False


def test_source_seed_is_idempotent(db_session: Session) -> None:
    bootstrap_rbac(db_session)

    first = seed_sources(db_session)
    second = seed_sources(db_session)

    assert first.inserted >= 20
    assert second.inserted == 0
    assert second.skipped >= first.inserted
    zse = db_session.scalar(select(Source).where(Source.name == "zimbabwe_stock_exchange"))
    assert zse is not None
    assert "market_prices" in zse.supported_capabilities
    assert "corporate_actions" in zse.supported_capabilities



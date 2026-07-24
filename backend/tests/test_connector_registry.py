"""Connector Registry admin API and service tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.seed_connectors import seed_connectors
from app.database.seed_sources import seed_sources
from app.database.session import get_db
from app.main import app
from app.models import AuditLog, Connector, ConnectorValidation, ConnectorVersion, Source, User
from app.models.rbac import Role, UserRole
from app.schemas.auth import UserCreate
from app.schemas.connector_registry import ConnectorCreate, ConnectorValidationRequest
from app.services.auth_service import create_access_token, register_user
from app.services.connector_registry_service import create_connector, validate_connector
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


def _connector_payload(name: str = "test_rest_connector") -> dict[str, object]:
    return {
        "name": name,
        "display_name": "Test REST Connector",
        "description": "Metadata-only connector contract.",
        "version": "1.0.0",
        "vendor": "InvestGuide",
        "author": "Platform",
        "classification": "test",
        "connector_type": "rest_api",
        "lifecycle": "active",
        "authentication_strategy": "api_key",
        "configuration_schema": {"base_url": "string", "endpoint_templates": "object"},
        "required_fields": ["base_url"],
        "supported_source_categories": ["market", "government"],
        "compatibility_notes": "Test connector contract.",
        "capabilities": [{"capability": "market_prices", "description": "Market prices."}, {"capability": "dividends", "description": "Dividends."}],
        "configuration_contract": {
            "schema": {"base_url": "string", "endpoint_templates": "object"},
            "required_fields": ["base_url"],
            "endpoint_templates": {"prices": "/prices"},
            "headers_schema": {"allowed_headers": ["Accept"]},
            "pagination_strategy": "page_number",
            "parser_identifier": "test.rest.v1",
            "rate_limit_policy": {"requests_per_minute": 60},
            "default_timeout_seconds": 20,
            "default_retry_count": 2,
            "request_method": "GET",
            "user_agent": "InvestGuideTest/1.0",
        },
        "reason": "test setup",
    }


def test_connector_registry_model_metadata() -> None:
    tables = Base.metadata.tables

    assert "connectors" in tables
    assert "connector_capabilities" in tables
    assert "connector_configuration_schemas" in tables
    assert "connector_versions" in tables
    assert "connector_validations" in tables
    assert any(column.name == "connector_id" for column in Source.__table__.columns)


def test_connector_routes_are_registered() -> None:
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/admin/connectors" in routes
    assert "/api/v1/admin/connectors/capabilities" in routes
    assert "/api/v1/admin/connectors/{connector_id}" in routes
    assert "/api/v1/admin/connectors/{connector_id}/validate" in routes
    assert "/api/v1/admin/connectors/{connector_id}/status" in routes


def test_connector_create_list_filter_and_audit(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)

    response = client.post("/api/v1/admin/connectors", headers=_auth(owner), json=_connector_payload())
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["capabilities"] == ["dividends", "market_prices"]
    assert body["data"]["compatible_source_count"] == 0
    assert db_session.scalar(select(ConnectorVersion).where(ConnectorVersion.change_type == "create")) is not None
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "admin.connector.create")) is not None

    list_response = client.get("/api/v1/admin/connectors", headers=_auth(owner), params={"search": "rest", "connector_type": "rest_api", "capability": "dividends"})
    data = list_response.json()["data"]

    assert list_response.status_code == 200
    assert data["total"] == 1
    assert data["connectors"][0]["name"] == "test_rest_connector"


def test_connector_validation_uses_metadata_only(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    created = client.post("/api/v1/admin/connectors", headers=_auth(owner), json=_connector_payload("validation_connector")).json()["data"]

    response = client.post(
        f"/api/v1/admin/connectors/{created['id']}/validate",
        headers=_auth(owner),
        json={"configuration": {"base_url": "https://example.test"}, "reason": "validate metadata"},
    )
    data = response.json()["data"]

    assert response.status_code == 200
    assert data["status"] == "passed"
    assert "No live network validation" in data["summary"]
    assert db_session.scalar(select(ConnectorValidation).where(ConnectorValidation.status == "passed")) is not None
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "admin.connector.validate")) is not None


def test_connector_validation_rejects_secret_schema(db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    payload = _connector_payload("unsafe_schema")
    payload["configuration_schema"] = {"api_secret": "string"}

    with pytest.raises(ValueError):
        create_connector(db_session, actor=owner, payload=ConnectorCreate(**payload))


def test_connector_status_soft_archives(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    created = client.post("/api/v1/admin/connectors", headers=_auth(owner), json=_connector_payload("archive_connector")).json()["data"]

    response = client.patch(f"/api/v1/admin/connectors/{created['id']}/status", headers=_auth(owner), json={"lifecycle": "archived", "reason": "retired connector"})
    list_response = client.get("/api/v1/admin/connectors", headers=_auth(owner))
    connector = db_session.get(Connector, created["id"])

    assert response.status_code == 200
    assert response.json()["data"]["lifecycle"] == "archived"
    assert connector.archived_at is not None
    assert all(item["id"] != created["id"] for item in list_response.json()["data"]["connectors"])


def test_connector_seed_is_idempotent_and_binds_sources(db_session: Session) -> None:
    bootstrap_rbac(db_session)
    seed_sources(db_session)

    first = seed_connectors(db_session)
    second = seed_connectors(db_session)

    assert first.inserted == 5
    assert first.bound_sources > 0
    assert second.inserted == 0
    assert second.skipped >= 5
    zse = db_session.scalar(select(Source).where(Source.name == "zimbabwe_stock_exchange"))
    assert zse is not None
    assert zse.connector_id is not None
    assert zse.connector.display_name == "Generic HTML Scraper Connector"


def test_connector_registry_requires_authorization(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    user = register_user(db_session, UserCreate(email="regular-connector@example.com", password="password123"))

    response = client.get("/api/v1/admin/connectors", headers=_auth(user))

    assert response.status_code == 403
    assert response.json()["success"] is False


def test_connector_service_validation_detects_source_category_mismatch(db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    seed_sources(db_session)
    source = db_session.scalar(select(Source).where(Source.name == "herald_business"))
    connector = create_connector(db_session, actor=owner, payload=ConnectorCreate(**_connector_payload("category_connector")))

    validation = validate_connector(db_session, actor=owner, connector=connector, payload=ConnectorValidationRequest(configuration={"base_url": "https://example.test"}, source_id=source.id, reason="check category"))

    assert validation.status == "failed"
    assert any("Source category" in error for error in validation.errors)

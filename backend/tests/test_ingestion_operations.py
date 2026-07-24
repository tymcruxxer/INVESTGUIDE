"""Ingestion Operations Centre admin API and service tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.seed_ingestion_operations import seed_ingestion_operations
from app.database.seed_sources import seed_sources
from app.database.session import get_db
from app.main import app
from app.models import AuditLog, ExecutionFailure, ExecutionMetric, IngestionExecution, IngestionJob, Role, Source, User, UserRole
from app.schemas.auth import UserCreate
from app.schemas.source_registry import SourceConfigurationInput, SourceCreate
from app.services.auth_service import create_access_token, register_user
from app.services.rbac_service import OWNER_ROLE, bootstrap_rbac
from app.services.source_registry_service import create_source


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


def _source(db: Session, owner: User) -> Source:
    existing = db.scalar(select(Source).where(Source.name == "ops_test_source"))
    if existing:
        return existing
    return create_source(
        db,
        actor=owner,
        payload=SourceCreate(
            name="ops_test_source",
            display_name="Operations Test Source",
            description="Test source for operations.",
            category="market",
            tier="tier_1",
            organization="Test",
            classification="test",
            supported_capabilities=["news", "market_prices"],
            connector_type="website",
            authentication_type="none",
            status="disabled",
            configuration=SourceConfigurationInput(base_url="https://example.com"),
            credentials=[],
            reason="test setup",
        ),
    )


def _job_payload(source_id: int, name: str = "News monitor") -> dict[str, object]:
    return {
        "source_id": source_id,
        "name": name,
        "job_type": "news",
        "description": "A controlled test ingestion job.",
        "configuration": {"executes_live_ingestion": False},
        "execution_mode": "manual",
        "priority": "normal",
        "max_retries": 2,
        "timeout_seconds": 120,
        "concurrency_limit": 1,
        "status": "pending",
        "is_enabled": False,
        "manual_only": True,
        "freshness_status": "unknown",
        "reason": "test setup",
    }


def test_ingestion_operations_model_metadata() -> None:
    tables = Base.metadata.tables

    assert "ingestion_jobs" in tables
    assert "ingestion_executions" in tables
    assert "execution_metrics" in tables
    assert "execution_failures" in tables


def test_ingestion_operation_routes_are_registered() -> None:
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/admin/ingestion/jobs" in routes
    assert "/api/v1/admin/ingestion/jobs/{job_id}" in routes
    assert "/api/v1/admin/ingestion/jobs/{job_id}/run" in routes
    assert "/api/v1/admin/ingestion/executions" in routes
    assert "/api/v1/admin/ingestion/executions/{execution_id}" in routes


def test_create_list_and_detail_job(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    source = _source(db_session, owner)

    create_response = client.post("/api/v1/admin/ingestion/jobs", headers=_auth(owner), json=_job_payload(source.id))
    list_response = client.get("/api/v1/admin/ingestion/jobs", headers=_auth(owner), params={"search": "news", "priority": "normal"})
    detail_response = client.get(f"/api/v1/admin/ingestion/jobs/{create_response.json()['data']['id']}", headers=_auth(owner))

    assert create_response.status_code == 200
    assert create_response.json()["data"]["source_name"] == source.display_name
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["configuration"]["executes_live_ingestion"] is False


def test_job_lifecycle_requests_record_execution_metric_and_audit(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    source = _source(db_session, owner)
    job_id = client.post("/api/v1/admin/ingestion/jobs", headers=_auth(owner), json=_job_payload(source.id, "Lifecycle job")).json()["data"]["id"]

    run_response = client.post(f"/api/v1/admin/ingestion/jobs/{job_id}/run", headers=_auth(owner), json={"reason": "operator dry run"})
    pause_response = client.post(f"/api/v1/admin/ingestion/jobs/{job_id}/pause", headers=_auth(owner), json={"reason": "pause requested"})
    executions_response = client.get("/api/v1/admin/ingestion/executions", headers=_auth(owner), params={"job_id": job_id})

    assert run_response.status_code == 200
    assert run_response.json()["data"]["status"] == "queued"
    assert pause_response.status_code == 200
    assert pause_response.json()["data"]["status"] == "paused"
    assert executions_response.json()["data"]["total"] == 2
    assert db_session.scalar(select(IngestionExecution).where(IngestionExecution.job_id == job_id)) is not None
    assert db_session.scalar(select(ExecutionMetric)) is not None
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "admin.ingestion.job.run")) is not None


def test_update_job_and_execution_detail(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    owner = _owner(db_session)
    source = _source(db_session, owner)
    job_id = client.post("/api/v1/admin/ingestion/jobs", headers=_auth(owner), json=_job_payload(source.id, "Update job")).json()["data"]["id"]

    update_response = client.patch(f"/api/v1/admin/ingestion/jobs/{job_id}", headers=_auth(owner), json={"priority": "critical", "freshness_status": "stale", "reason": "priority escalation"})
    client.post(f"/api/v1/admin/ingestion/jobs/{job_id}/retry", headers=_auth(owner), json={"reason": "retry requested"})
    execution = db_session.scalar(select(IngestionExecution).where(IngestionExecution.job_id == job_id))
    detail_response = client.get(f"/api/v1/admin/ingestion/executions/{execution.id}", headers=_auth(owner))

    assert update_response.status_code == 200
    assert update_response.json()["data"]["priority"] == "critical"
    assert update_response.json()["data"]["freshness_status"] == "stale"
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["trigger_type"] == "retry"


def test_ingestion_operations_require_authorization(client: TestClient, db_session: Session) -> None:
    bootstrap_rbac(db_session)
    regular = register_user(db_session, UserCreate(email="regular-ingestion@example.com", password="password123"))

    response = client.get("/api/v1/admin/ingestion/jobs", headers=_auth(regular))

    assert response.status_code == 403
    assert response.json()["success"] is False


def test_seed_ingestion_operations_is_idempotent(db_session: Session) -> None:
    bootstrap_rbac(db_session)
    seed_sources(db_session)

    first = seed_ingestion_operations(db_session)
    second = seed_ingestion_operations(db_session)

    assert first.inserted_jobs >= 5
    assert first.inserted_executions >= 5
    assert first.inserted_failures >= 1
    assert second.inserted_jobs == 0
    assert second.skipped_jobs >= first.inserted_jobs
    assert db_session.scalar(select(IngestionJob).where(IngestionJob.name == "RBZ exchange rates monitor")) is not None
    assert db_session.scalar(select(ExecutionFailure)) is not None

"""Tests for Sprint 049 ingestion operations and data quality."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.router import api_router
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.company import Company
from app.models.ingestion import IngestionRecordIssue, IngestionRun
from app.services.data_quality import (
    company_quality_report,
    data_quality_summary,
    export_issues,
    list_issues,
    score_entity,
    source_health,
)
from app.services.ingestion import EntityType, IngestionMode, IssueCode, SourceType
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.registry import build_default_registry
from app.services.ingestion.sources import JsonSourceAdapter

FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


@contextmanager
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


def _pipeline(entity: EntityType, source_file: str) -> IngestionPipeline:
    registration = build_default_registry().get(entity)
    source = JsonSourceAdapter(
        FIXTURES / source_file,
        source_name="Development Fixture",
        source_type=SourceType.DEVELOPMENT_FIXTURE,
        dataset_version="test",
        is_development_data=True,
    )
    return IngestionPipeline(entity, source, registration.normalizer, registration.validator, registration.importer)


def test_issue_codes_are_stable() -> None:
    assert IssueCode.MISSING_REQUIRED_FIELD.value == "MISSING_REQUIRED_FIELD"
    assert IssueCode.BALANCE_SHEET_IMBALANCE.value == "BALANCE_SHEET_IMBALANCE"
    assert IssueCode.DATABASE_WRITE_FAILED.value == "DATABASE_WRITE_FAILED"


def test_pipeline_persists_record_level_issues() -> None:
    with db_session() as session:
        _pipeline(EntityType.BALANCE_SHEETS, "balance_sheets.json").run(session, IngestionMode.DRY_RUN)
        issues = session.scalars(select(IngestionRecordIssue)).all()

        assert issues
        assert {issue.severity for issue in issues} >= {"Warning", "Rejected"}
        assert "BALANCE_SHEET_IMBALANCE" in {issue.issue_code for issue in issues}
        assert all("password" not in (issue.message or "").lower() for issue in issues)


def test_data_quality_summary_and_source_health_are_explained() -> None:
    with db_session() as session:
        _pipeline(EntityType.COMPANIES, "companies.json").run(session, IngestionMode.LENIENT)
        _pipeline(EntityType.BALANCE_SHEETS, "balance_sheets.json").run(session, IngestionMode.DRY_RUN)

        summary = data_quality_summary(session)
        sources = source_health(session)
        company_quality = score_entity(session, "companies")

        assert summary["entities"]
        assert summary["development_record_count"] >= 0
        assert sources[0]["source_name"] == "Development Fixture"
        assert company_quality["quality_score"]["reasons"]
        assert company_quality["completeness"]["reasons"]
        assert company_quality["provenance"]["reasons"]


def test_company_data_quality_report_recommends_specific_actions() -> None:
    with db_session() as session:
        _pipeline(EntityType.COMPANIES, "companies.json").run(session, IngestionMode.LENIENT)
        _pipeline(EntityType.ASSETS, "assets.json").run(session, IngestionMode.LENIENT)
        report = company_quality_report(session, "DLTA")

        assert report is not None
        assert report["ticker"] == "DLTA"
        assert any("profile" in action.lower() for action in report["suggested_operator_actions"])
        assert "components" in report


def test_issue_pagination_and_safe_export() -> None:
    with db_session() as session:
        _pipeline(EntityType.MARKET_SNAPSHOTS, "market_snapshots.json").run(session, IngestionMode.DRY_RUN)
        page = list_issues(session, limit=2)
        csv_output = export_issues(session, output_format="csv")

        assert page.total >= 1
        assert "issue_code" in csv_output
        assert "raw_value_summary" not in csv_output


def test_internal_operations_endpoints_return_envelopes() -> None:
    with db_session() as session:
        _pipeline(EntityType.COMPANIES, "companies.json").run(session, IngestionMode.LENIENT)
        run = session.scalar(select(IngestionRun))
        assert run is not None

        def override_get_db() -> Iterator[Session]:
            yield session

        app.dependency_overrides[get_db] = override_get_db
        try:
            client = TestClient(app)
            assert client.get("/api/v1/internal/ingestion/runs").json()["success"] is True
            assert client.get(f"/api/v1/internal/ingestion/runs/{run.id}").json()["success"] is True
            assert client.get(f"/api/v1/internal/ingestion/runs/{run.id}/issues").json()["success"] is True
            assert client.get("/api/v1/internal/ingestion/sources").json()["success"] is True
            assert client.get("/api/v1/internal/data-quality/summary").json()["success"] is True
            assert client.get("/api/v1/internal/data-quality/entities/companies").json()["success"] is True
            assert client.get("/api/v1/internal/data-quality/companies/DLTA").json()["success"] is True
        finally:
            app.dependency_overrides.clear()


def test_internal_routes_registered_once() -> None:
    paths = {route.path for route in api_router.routes if hasattr(route, "path")}
    assert "/api/v1/internal/ingestion/runs" in paths
    assert "/api/v1/internal/data-quality/summary" in paths





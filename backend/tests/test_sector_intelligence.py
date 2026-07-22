"""Sector Intelligence tests."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.v1 import sectors as sectors_module
from app.database.base import Base
from app.main import app
from app.models.asset import AssetStatus, Currency, Exchange
from app.models.company import Company
from app.models.sector import Industry, Sector
from app.services import sector_service
from app.services.intelligence.sector_engine import (
    build_company_sector_summary,
    build_industry_research,
    build_sector_macro_relationships,
    build_sector_research,
    clear_sector_intelligence_cache,
)

client = TestClient(app)


def make_sector(**overrides: object) -> SimpleNamespace:
    data = {
        "id": 1,
        "name": "Consumer Staples",
        "slug": "consumer-staples",
        "description": "Everyday consumer goods.",
        "exchange_coverage": "ZSE, VFEX",
        "country": "Zimbabwe",
        "overview": "Consumer Staples covers everyday goods.",
        "source_name": "Development Sector Fixture",
        "source_type": "DEVELOPMENT_FIXTURE",
        "source_url": None,
        "imported_at": datetime(2026, 7, 15, tzinfo=UTC),
        "verified_at": None,
        "verification_status": "Development",
        "dataset_version": "test",
        "is_development_data": True,
        "created_at": datetime(2026, 7, 15, tzinfo=UTC),
        "updated_at": datetime(2026, 7, 15, tzinfo=UTC),
        "industries": [],
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_industry(**overrides: object) -> SimpleNamespace:
    sector = make_sector()
    data = {
        "id": 1,
        "sector_id": 1,
        "name": "Beverages",
        "slug": "beverages",
        "description": "Beverage producers and distributors.",
        "overview": "Beverage businesses depend on demand, distribution, and input costs.",
        "source_name": "Development Industry Fixture",
        "source_type": "DEVELOPMENT_FIXTURE",
        "source_url": None,
        "imported_at": datetime(2026, 7, 15, tzinfo=UTC),
        "verified_at": None,
        "verification_status": "Development",
        "dataset_version": "test",
        "is_development_data": True,
        "created_at": datetime(2026, 7, 15, tzinfo=UTC),
        "updated_at": datetime(2026, 7, 15, tzinfo=UTC),
        "sector": sector,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_company(**overrides: object) -> SimpleNamespace:
    data = {
        "ticker": "DLTA",
        "name": "Delta Corporation Limited",
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "exchange": "ZSE",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_sector_model_metadata() -> None:
    """Sector and Industry models expose provenance and relationships."""
    assert "slug" in Sector.__table__.columns
    assert "source_name" in Sector.__table__.columns
    assert "is_development_data" in Sector.__table__.columns
    assert "sector_id" in Industry.__table__.columns
    assert any(index.name == "ix_sectors_slug" for index in Sector.__table__.indexes)
    assert any(index.name == "ix_industries_slug" for index in Industry.__table__.indexes)


def test_sector_research_contains_macro_companies_and_learning() -> None:
    """Sector research explains sector context without recommendations."""
    sector = make_sector()
    industry = make_industry(sector=sector)
    sector.industries = [industry]
    payload = build_sector_research(sector, [make_company()], [industry])

    assert payload["sector"]["slug"] == "consumer-staples"
    assert payload["companies"][0]["ticker"] == "DLTA"
    assert payload["macro_relationships"]
    assert payload["knowledge_graph"]["edges"]
    assert "not investment advice" in payload["transparency"]["not_advice"].lower()


def test_industry_research_contains_parent_sector_and_companies() -> None:
    """Industry research links industry, sector, macro exposure, and companies."""
    payload = build_industry_research(make_industry(), [make_company()])

    assert payload["industry"]["slug"] == "beverages"
    assert payload["sector"]["slug"] == "consumer-staples"
    assert payload["related_companies"][0]["ticker"] == "DLTA"
    assert payload["knowledge_graph"]["root"] == "Beverages"


def test_company_sector_summary_and_cache_are_deterministic() -> None:
    """Company page summary is stable and cache can be cleared."""
    clear_sector_intelligence_cache()
    first = build_company_sector_summary(make_company())
    second = build_company_sector_summary(make_company())

    assert first == second
    assert first["sector_path"] == "/sector/consumer-staples"
    assert first["macro_relationships"]


def test_sector_macro_relationships_include_paths() -> None:
    """Sector macro relationships link to existing macro pages."""
    rows = build_sector_macro_relationships("Consumer Staples")

    assert rows[0]["path"].startswith("/macro/")
    assert any(row["indicator_type"] == "inflation" for row in rows)


def test_sector_service_prefers_verified_rows() -> None:
    """Verified sector rows win over development preview rows."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        db.add_all(
            [
                Sector(name="Consumer Staples", slug="consumer-staples", is_development_data=True),
                Sector(name="Consumer Staples Verified", slug="consumer-staples", is_development_data=False),
            ]
        )
        db.commit()
        sector = sector_service.get_sector_by_slug(db, "consumer-staples")

    assert sector is not None
    assert sector.name == "Consumer Staples Verified"


def test_sector_routes_are_registered() -> None:
    """Sector and industry routes are mounted."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/sectors" in routes
    assert "/api/v1/sectors/{slug}" in routes
    assert "/api/v1/sectors/{slug}/research" in routes
    assert "/api/v1/industries" in routes
    assert "/api/v1/industries/{slug}" in routes
    assert "/api/v1/industries/{slug}/research" in routes


def test_sector_api_returns_success_envelope(monkeypatch) -> None:
    """Sector API returns a standard success envelope."""
    sector = make_sector()
    industry = make_industry(sector=sector)
    sector.industries = [industry]

    monkeypatch.setattr(sectors_module.sector_service, "get_sector_by_slug", lambda *args, **kwargs: sector)
    monkeypatch.setattr(sectors_module.sector_service, "companies_for_sector", lambda *args, **kwargs: [make_company()])

    response = client.get("/api/v1/sectors/consumer-staples/research")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["sector"]["slug"] == "consumer-staples"

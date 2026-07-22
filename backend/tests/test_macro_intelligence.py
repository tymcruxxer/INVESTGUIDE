"""Macro Intelligence tests."""

from __future__ import annotations

from datetime import UTC, date, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.main import app
from app.models.company import Company
from app.models.macro import MacroIndicator, MacroIndicatorType
from app.api.v1 import macro as macro_module
from app.services import macro_service
from app.services.intelligence.macro_engine import (
    build_company_macro_impact,
    build_macro_knowledge_graph,
    build_macro_research,
    build_sector_macro_impact,
    clear_macro_intelligence_cache,
    related_companies_for_macro,
)

client = TestClient(app)


def make_indicator(**overrides: object) -> SimpleNamespace:
    data = {
        "id": 1,
        "indicator_type": MacroIndicatorType.INFLATION,
        "name": "Annual Inflation",
        "value": 57.4,
        "unit": "%",
        "reporting_period": date(2026, 6, 30),
        "country": "Zimbabwe",
        "currency": "ZWG",
        "commodity": None,
        "notes": None,
        "source_name": "Development Macro Fixture",
        "source_type": "DEVELOPMENT_FIXTURE",
        "source_url": "https://www.zimstat.co.zw/",
        "imported_at": datetime(2026, 7, 1, tzinfo=UTC),
        "verified_at": None,
        "verification_status": "Development",
        "dataset_version": "test",
        "is_development_data": True,
        "created_at": datetime(2026, 7, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 7, 1, tzinfo=UTC),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_company(**overrides: object) -> SimpleNamespace:
    data = {
        "id": 1,
        "ticker": "DLTA",
        "name": "Delta Corporation Limited",
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "exchange": "ZSE",
        "assets": [],
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_macro_model_metadata_contains_provenance_fields() -> None:
    """Macro model supports source, verification, ingestion, and fixture metadata."""
    columns = MacroIndicator.__table__.columns

    assert "indicator_type" in columns
    assert "reporting_period" in columns
    assert "source_name" in columns
    assert "source_url" in columns
    assert "verified_at" in columns
    assert "is_development_data" in columns
    assert any(index.name == "ix_macro_indicators_type" for index in MacroIndicator.__table__.indexes)


def test_macro_research_explains_without_prediction_language() -> None:
    """Macro research returns educational explanations and no forecast language."""
    payload = build_macro_research(MacroIndicatorType.INFLATION, [make_indicator()], [make_company()])

    assert payload["label"] == "Inflation"
    assert "prices" in payload["overview"].lower()
    assert payload["current_value"]["data_origin"] == "Development Preview"
    assert payload["affected_companies"][0]["ticker"] == "DLTA"
    assert "prediction" in payload["transparency"]["not_advice"].lower()
    assert payload["learn_next"]


def test_company_macro_impact_contains_relationship_chain() -> None:
    """Company impact explains the chain from macro factor to business effects."""
    impact = build_company_macro_impact(make_company(), [make_indicator()])

    inflation = next(item for item in impact["factors"] if item["indicator_type"] == "inflation")
    assert inflation["relationship_chain"][0] == "Inflation"
    assert "Consumer purchasing power" in inflation["relationship_chain"]
    assert impact["transparency"]["not_advice"].startswith("Macro Factors")


def test_sector_impact_and_related_companies_are_deterministic() -> None:
    """Sector and related-company helpers use fixed mappings."""
    sector = build_sector_macro_impact("Financial Services")
    related = related_companies_for_macro(
        MacroIndicatorType.INTEREST_RATE,
        [make_company(ticker="CBZ", name="CBZ Holdings", sector="Financial Services", industry="Banking")],
    )

    assert sector["sensitivities"][0]["indicator_type"] == "interest_rate"
    assert related[0]["ticker"] == "CBZ"
    assert "rate" in related[0]["reason"].lower()


def test_macro_knowledge_graph_contains_explained_edges_and_cache() -> None:
    """Knowledge graph and cache helpers are deterministic."""
    clear_macro_intelligence_cache()
    graph = build_macro_knowledge_graph(MacroIndicatorType.EXCHANGE_RATE)
    first = build_company_macro_impact(make_company(), [make_indicator()])
    second = build_company_macro_impact(make_company(), [make_indicator()])

    assert graph["root"] == "Exchange Rates"
    assert graph["edges"][0]["reason"]
    assert first["factors"] == second["factors"]


def test_macro_service_prefers_verified_over_development() -> None:
    """Verified macro rows win over development preview rows."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        db.add_all(
            [
                MacroIndicator(
                    indicator_type=MacroIndicatorType.INFLATION,
                    name="Annual Inflation",
                    value=99,
                    unit="%",
                    reporting_period=date(2026, 6, 30),
                    country="Zimbabwe",
                    currency="ZWG",
                    source_type="DEVELOPMENT_FIXTURE",
                    is_development_data=True,
                ),
                MacroIndicator(
                    indicator_type=MacroIndicatorType.INFLATION,
                    name="Annual Inflation",
                    value=10,
                    unit="%",
                    reporting_period=date(2026, 5, 31),
                    country="Zimbabwe",
                    currency="ZWG",
                    source_type="MANUAL_CURATED_IMPORT",
                    is_development_data=False,
                ),
            ]
        )
        db.commit()
        rows = macro_service.list_macro_indicators(db)

    assert len(rows) == 1
    assert float(rows[0].value) == 10


def test_macro_routes_are_registered() -> None:
    """Macro routes are mounted under the versioned API."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/macro" in routes
    assert "/api/v1/macro/{indicator_slug}" in routes
    assert "/api/v1/macro/{indicator_slug}/research" in routes
    assert "/api/v1/macro/company/{ticker}" in routes


def test_macro_api_returns_success_envelope(monkeypatch) -> None:
    """Macro API returns the global envelope and research payload."""
    indicator = make_indicator()
    company = make_company()

    monkeypatch.setattr(macro_module.macro_service, "get_indicators_by_type", lambda *args, **kwargs: [indicator])
    monkeypatch.setattr(macro_module.company_service, "list_companies", lambda *args, **kwargs: ([company], 1))

    response = client.get("/api/v1/macro/inflation/research")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["label"] == "Inflation"
    assert body["data"]["affected_companies"][0]["ticker"] == "DLTA"


"""Deterministic AI Research engine tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import assets as assets_module
from app.api.v1 import companies as companies_module
from app.main import app
from app.models.asset import AssetStatus, AssetType, Currency, Exchange
from app.models.company_profile import ResearchStatus
from app.services.intelligence.education_engine import EducationEngine
from app.services.intelligence.evidence_engine import EvidenceEngine
from app.services.intelligence.opportunity_engine import OpportunityEngine
from app.services.intelligence.question_engine import QuestionEngine
from app.services.intelligence.research_service import build_asset_research, build_company_research, clear_research_cache
from app.services.intelligence.risk_engine import RiskEngine

client = TestClient(app)


def make_asset(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 9, tzinfo=UTC)
    data = {
        "id": 1,
        "ticker": "DLTA",
        "company_name": "Delta Corporation Limited",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "asset_type": AssetType.EQUITY,
        "currency": Currency.ZWG,
        "description": "Established Zimbabwe-listed beverages company with leading consumer brands.",
        "logo_url": None,
        "official_website": "https://www.delta.co.zw/",
        "market_cap": 120_000_000,
        "listing_date": datetime(2020, 1, 1, tzinfo=UTC).date(),
        "status": AssetStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_company(asset: SimpleNamespace | None = None, **overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 9, tzinfo=UTC)
    data = {
        "id": 1,
        "name": "Delta Corporation Limited",
        "legal_name": "Delta Corporation Limited",
        "ticker": "DLTA",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "country": "Zimbabwe",
        "headquarters": "Harare",
        "website": "https://www.delta.co.zw/",
        "description": "A Zimbabwe-listed consumer staples company.",
        "founded_year": 1946,
        "employee_count": None,
        "market": "ZSE",
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "logo_url": None,
        "created_at": now,
        "updated_at": now,
        "assets": [asset] if asset is not None else [],
        "news_articles": [],
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_profile(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 9, tzinfo=UTC)
    data = {
        "id": 1,
        "company_id": 1,
        "business_summary": "Delta manufactures and distributes beverage products in Zimbabwe.",
        "primary_business": "Consumer beverages",
        "products_services": ["Beverages", "Distribution"],
        "industry": "Consumer Staples",
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": now,
        "source_name": "InvestGuide fixture",
        "source_url": "https://www.delta.co.zw/",
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_research_engines_return_structured_sections() -> None:
    asset = make_asset()

    opportunity = OpportunityEngine().assess(asset)
    risk = RiskEngine().assess(asset)
    evidence = EvidenceEngine().assess(asset)
    education = EducationEngine().explain(asset, opportunity["label"], risk["risk_level"])
    questions = QuestionEngine().suggest(asset)

    assert 0 <= opportunity["score"] <= 100
    assert risk["risk_level"] in {"Low", "Moderate", "Elevated", "High"}
    assert evidence["strength"] in {"Strong", "Moderate", "Limited", "Experimental"}
    assert "why_it_matters" in education
    assert len(questions) >= 4


def test_build_asset_research_returns_safe_payload() -> None:
    clear_research_cache()
    payload = build_asset_research(make_asset())
    text = str(payload).lower()

    assert payload["ticker"] == "DLTA"
    assert payload["subject_type"] == "asset"
    assert payload["assessment_version"] == "1"
    assert payload["engine_version"] == "1.0.0"
    assert payload["opportunity"]["label"]
    assert payload["risk"]["things_to_watch"]
    assert payload["evidence"]["data_used"]
    assert payload["eli18"]["summary"]
    assert "strong buy" not in text
    assert "sell recommendation" not in text


def test_build_company_research_uses_company_profile_context() -> None:
    clear_research_cache()
    asset = make_asset()
    company = make_company(asset)
    profile = make_profile()

    payload = build_company_research(company, primary_asset=asset, profile=profile)

    assert payload["ticker"] == "DLTA"
    assert payload["subject_type"] == "company"
    assert payload["transparency"]["research_status"]
    assert any("description" in item for item in payload["evidence"]["data_used"])


def test_asset_research_endpoint_returns_success_envelope(monkeypatch) -> None:
    def fake_get_asset_by_ticker(*args, **kwargs):
        return make_asset()

    monkeypatch.setattr(assets_module.asset_service, "get_asset_by_ticker", fake_get_asset_by_ticker)

    response = client.get("/api/v1/assets/DLTA/research")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Asset research retrieved successfully"
    assert body["data"]["ticker"] == "DLTA"
    assert body["data"]["opportunity"]["score"] >= 0
    assert body["data"]["evidence"]["strength"] in {"Strong", "Moderate", "Limited", "Experimental"}


def test_asset_research_not_found_returns_error_envelope(monkeypatch) -> None:
    def fake_get_asset_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(assets_module.asset_service, "get_asset_by_ticker", fake_get_asset_by_ticker)

    response = client.get("/api/v1/assets/unknown/research")
    body = response.json()

    assert response.status_code == 404
    assert body["error_code"] == "ASSET_NOT_FOUND"


def test_company_research_endpoint_returns_success_envelope(monkeypatch) -> None:
    asset = make_asset()
    company = make_company(asset)
    profile = make_profile()

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_get_or_build_company_profile(*args, **kwargs):
        return profile

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.company_enrichment, "get_or_build_company_profile", fake_get_or_build_company_profile)

    response = client.get("/api/v1/companies/DLTA/research")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company research retrieved successfully"
    assert body["data"]["ticker"] == "DLTA"
    assert body["data"]["subject_type"] == "company"


def test_company_research_not_found_returns_error_envelope(monkeypatch) -> None:
    def fake_get_company_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)

    response = client.get("/api/v1/companies/unknown/research")
    body = response.json()

    assert response.status_code == 404
    assert body["error_code"] == "COMPANY_NOT_FOUND"
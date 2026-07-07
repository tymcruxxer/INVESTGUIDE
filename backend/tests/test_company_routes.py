"""Company route tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import companies as companies_module
from app.main import app
from app.models.asset import AssetStatus, AssetType, Currency, Exchange
from app.models.company_profile import ResearchStatus

client = TestClient(app)


def make_company(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped company object for route tests."""
    now = datetime(2026, 7, 3, tzinfo=UTC)
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
        "assets": [],
        "news_articles": [],
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_asset(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped asset object for company route tests."""
    now = datetime(2026, 7, 3, tzinfo=UTC)
    data = {
        "id": 1,
        "company_id": 1,
        "ticker": "DLTA",
        "company_name": "Delta Corporation Limited",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "asset_type": AssetType.EQUITY,
        "currency": Currency.ZWG,
        "description": "Beverages company.",
        "logo_url": None,
        "official_website": "https://www.delta.co.zw/",
        "market_cap": None,
        "listing_date": None,
        "status": AssetStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_news(asset: SimpleNamespace | None = None, **overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped news object for company route tests."""
    now = datetime(2026, 7, 3, tzinfo=UTC)
    data = {
        "id": 1,
        "title": "Delta sample update",
        "summary": "Company news sample.",
        "content": None,
        "content_hash": "a" * 64,
        "source": "InvestGuide Sample",
        "author": None,
        "published_at": now,
        "url": None,
        "image_url": None,
        "language": "en",
        "sentiment": None,
        "relevance_score": None,
        "credibility_score": None,
        "assets": [asset] if asset else [],
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_company_routes_are_registered_under_api_v1() -> None:
    """Read-only company routes are mounted under the versioned router."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/companies" in routes
    assert "/api/v1/companies/{ticker}" in routes
    assert "/api/v1/companies/{ticker}/assessment" in routes


def test_list_companies_endpoint_returns_success_envelope(monkeypatch) -> None:
    """List endpoint returns the global envelope and pagination metadata."""

    def fake_list_companies(*args, **kwargs):
        return [make_company()], 1

    monkeypatch.setattr(companies_module.company_service, "list_companies", fake_list_companies)

    response = client.get("/api/v1/companies?exchange=ZSE&page=1&limit=10")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Companies retrieved successfully"
    assert body["data"][0]["ticker"] == "DLTA"
    assert body["data"][0]["name"] == "Delta Corporation Limited"
    assert body["meta"]["total"] == 1


def test_company_detail_returns_related_assets_and_news(monkeypatch) -> None:
    """Detail endpoint returns company overview, assets, news, and assessment availability."""
    asset = make_asset()
    company = make_company(assets=[asset])
    news = make_news(asset)

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_get_company_news(*args, **kwargs):
        return [news]

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.company_service, "get_company_news", fake_get_company_news)

    response = client.get("/api/v1/companies/DLTA")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["company"]["ticker"] == "DLTA"
    assert body["data"]["related_assets"][0]["ticker"] == "DLTA"
    assert body["data"]["latest_news"][0]["title"] == "Delta sample update"
    assert body["data"]["assessment_available"] is True


def test_company_not_found_returns_error_envelope(monkeypatch) -> None:
    """Missing companies return a 404 response envelope."""

    def fake_get_company_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)

    response = client.get("/api/v1/companies/unknown")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "Company 'UNKNOWN' was not found",
        "error_code": "COMPANY_NOT_FOUND",
        "details": {},
    }

def make_profile(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped company profile object for route tests."""
    now = datetime(2026, 7, 3, tzinfo=UTC)
    data = {
        "id": None,
        "company_id": 1,
        "business_summary": "Development fixture summary.",
        "primary_business": "Consumer beverages",
        "products_services": ["Beverages", "Distribution"],
        "industry": "Consumer Staples",
        "sub_industry": "Beverages",
        "headquarters": "Harare, Zimbabwe",
        "founded_year": 1946,
        "website": "https://www.delta.co.zw/",
        "email": None,
        "phone": None,
        "country": "Zimbabwe",
        "exchange": Exchange.ZSE,
        "currency": Currency.ZWG,
        "employees": None,
        "status": AssetStatus.ACTIVE,
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": now,
        "source_name": "InvestGuide development fixture data",
        "source_url": "https://www.delta.co.zw/",
        "created_at": None,
        "updated_at": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_company_profile_endpoint_returns_source_transparency(monkeypatch) -> None:
    """Company profile endpoint returns structured profile and verification metadata."""
    company = make_company()
    profile = make_profile()

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_get_or_build_company_profile(*args, **kwargs):
        return profile

    def fake_build_verification_payload(profile_arg):
        return {
            "last_verified": profile_arg.last_verified,
            "source_name": profile_arg.source_name,
            "source_url": profile_arg.source_url,
            "research_status": profile_arg.research_status,
        }

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.company_enrichment, "get_or_build_company_profile", fake_get_or_build_company_profile)
    monkeypatch.setattr(companies_module.company_enrichment, "build_verification_payload", fake_build_verification_payload)

    response = client.get("/api/v1/companies/DLTA/profile")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company profile retrieved successfully"
    assert body["data"]["company"]["ticker"] == "DLTA"
    assert body["data"]["profile"]["primary_business"] == "Consumer beverages"
    assert body["data"]["verification"]["research_status"] == "development"
    assert body["data"]["verification"]["source_name"] == "InvestGuide development fixture data"


def test_company_profile_not_found_returns_error_envelope(monkeypatch) -> None:
    """Missing company profile requests return a company 404 envelope."""

    def fake_get_company_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)

    response = client.get("/api/v1/companies/unknown/profile")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "Company 'UNKNOWN' was not found",
        "error_code": "COMPANY_NOT_FOUND",
        "details": {},
    }

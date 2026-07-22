"""Business Intelligence Engine tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import companies as companies_module
from app.api.v1 import industries as industries_module
from app.main import app
from app.services.intelligence.business_engine import build_business_intelligence, clear_business_cache
from app.services.intelligence.competitor_engine import build_competitor_map
from app.services.intelligence.industry_engine import build_industry_intelligence

client = TestClient(app)


def make_company(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": 1,
        "ticker": "DLTA",
        "name": "Delta Corporation Limited",
        "legal_name": "Delta Corporation Limited",
        "exchange": "ZSE",
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "country": "Zimbabwe",
        "headquarters": "Harare",
        "website": "https://example.com",
        "description": "Established beverages company with leading consumer brands and broad distribution.",
        "founded_year": 1946,
        "employee_count": None,
        "market": "ZSE",
        "currency": "ZWG",
        "status": "active",
        "assets": [],
        "news_articles": [],
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_profile(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": 1,
        "business_summary": "Delta manufactures and distributes beverages in Zimbabwe.",
        "primary_business": "Beverage manufacturing and distribution",
        "products_services": ["Lager beer", "Sparkling beverages", "Sorghum beer"],
        "industry": "Beverages",
        "country": "Zimbabwe",
        "headquarters": "Harare",
        "founded_year": 1946,
        "employees": None,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_business_engine_returns_deep_dive_sections() -> None:
    clear_business_cache()
    company = make_company()
    peer = make_company(id=2, ticker="INN", name="Innscor Africa Limited", industry="Food Products")

    payload = build_business_intelligence(company, companies=[company, peer], profile=make_profile())
    text = str(payload).lower()

    assert payload["ticker"] == "DLTA"
    assert payload["business_summary"]["summary"]
    assert payload["business_model"]["how_it_makes_money"]
    assert payload["revenue_drivers"]
    assert payload["operational_risks"]
    assert payload["competitive_position"]["label"] in {
        "Market Leader",
        "Strong Competitor",
        "Emerging Player",
        "Niche Player",
    }
    assert payload["business_maturity"]["label"] == "Mature with Stable Cash Flows"
    assert payload["knowledge_graph"]["nodes"]
    assert "strong buy" not in text
    assert "price target" not in text


def test_industry_engine_returns_risks_opportunities_and_learning() -> None:
    payload = build_industry_intelligence("Beverages", [make_company()])

    assert payload["industry"] == "Beverages"
    assert payload["common_risks"]
    assert payload["common_opportunities"]
    assert payload["learn_next"]
    assert payload["companies"][0]["ticker"] == "DLTA"


def test_competitor_engine_explains_relationships() -> None:
    company = make_company()
    direct = make_company(id=2, ticker="INN", name="Innscor Africa Limited")
    unrelated = make_company(id=3, ticker="CMCL", name="Caledonia Mining", sector="Mining", industry="Mining")

    payload = build_competitor_map(company, [company, direct, unrelated])

    assert payload["direct_competitors"]
    assert payload["direct_competitors"][0]["reasons"]
    assert payload["transparency"]["not_recommendation"]


def test_company_business_endpoint_returns_success_envelope(monkeypatch) -> None:
    company = make_company()
    profile = make_profile()

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_profile(*args, **kwargs):
        return profile

    def fake_list_companies(*args, **kwargs):
        return [company], 1

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.company_enrichment, "get_or_build_company_profile", fake_profile)
    monkeypatch.setattr(companies_module.company_service, "list_companies", fake_list_companies)

    response = client.get("/api/v1/companies/DLTA/business")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company business intelligence retrieved successfully"
    assert body["data"]["business_model"]["main_products_services"]


def test_company_business_endpoint_returns_404(monkeypatch) -> None:
    def fake_get_company_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)

    response = client.get("/api/v1/companies/UNKNOWN/business")
    body = response.json()

    assert response.status_code == 404
    assert body["error_code"] == "COMPANY_NOT_FOUND"


def test_industry_endpoint_returns_success_envelope(monkeypatch) -> None:
    industry = SimpleNamespace(
        id=1,
        sector_id=10,
        name="Beverages",
        slug="beverages",
        description="Beverage production and distribution.",
        overview="Consumer beverage industry.",
        source_name="Development Fixture",
        source_type="development_fixture",
        source_url=None,
        imported_at=datetime.now(UTC),
        verified_at=None,
        verification_status="development_preview",
        dataset_version="dev-1",
        external_key="industry:beverages",
        is_development_data=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        sector=SimpleNamespace(id=10, name="Consumer Staples", slug="consumer-staples", description="Essential consumer goods.", country="Zimbabwe", is_development_data=True),
    )

    def fake_get_industry_by_slug(*args, **kwargs):
        return industry

    def fake_companies_for_industry(*args, **kwargs):
        return [make_company()]

    monkeypatch.setattr(industries_module.sector_service, "get_industry_by_slug", fake_get_industry_by_slug)
    monkeypatch.setattr(industries_module.sector_service, "companies_for_industry", fake_companies_for_industry)

    response = client.get("/api/v1/industries/Beverages")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Industry retrieved successfully"
    assert body["data"]["companies"][0]["ticker"] == "DLTA"






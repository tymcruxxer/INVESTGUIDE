"""Deterministic comparison, related, and knowledge graph tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import compare as compare_module
from app.api.v1 import companies as companies_module
from app.main import app
from app.models.asset import AssetStatus, AssetType, Currency, Exchange
from app.services.intelligence.comparison_engine import build_comparison
from app.services.intelligence.knowledge_graph import build_knowledge_graph
from app.services.intelligence.related_engine import build_related_research

client = TestClient(app)


def make_asset(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": 1,
        "ticker": "DLTA",
        "company_name": "Delta Corporation Limited",
        "name": "Delta Corporation Limited",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "asset_type": AssetType.EQUITY,
        "currency": Currency.ZWG,
        "description": "Established beverages company with consumer staples exposure and local brands.",
        "market_cap": 120_000_000,
        "listing_date": datetime(2020, 1, 1, tzinfo=UTC).date(),
        "status": AssetStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_company(**overrides: object) -> SimpleNamespace:
    asset = overrides.pop("asset", None)
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": 1,
        "name": "Delta Corporation Limited",
        "legal_name": "Delta Corporation Limited",
        "ticker": "DLTA",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "country": "Zimbabwe",
        "description": "Zimbabwe consumer staples and beverages company.",
        "market": "ZSE",
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "assets": [asset] if asset is not None else [],
        "news_articles": [],
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_knowledge_graph_returns_learn_next_paths() -> None:
    graph = build_knowledge_graph(make_asset())

    assert graph["version"] == "1"
    assert graph["root"] == "Delta Corporation Limited"
    assert any(topic["topic"] == "Consumer Staples" for topic in graph["learn_next"])
    assert graph["edges"]


def test_related_engine_ranks_explained_company_relationships() -> None:
    delta = make_company(asset=make_asset())
    innscor = make_company(
        id=2,
        ticker="INN",
        name="Innscor Africa Limited",
        sector="Consumer Staples",
        industry="Food Products",
        description="Food manufacturing consumer staples company.",
    )
    cbz = make_company(
        id=3,
        ticker="CBZ",
        name="CBZ Holdings Limited",
        sector="Financial Services",
        industry="Banking",
        description="Banking and financial services group.",
    )

    payload = build_related_research(delta, [delta, innscor, cbz])

    assert payload["ticker"] == "DLTA"
    assert payload["related_companies"][0]["ticker"] == "INN"
    assert payload["related_companies"][0]["reasons"]
    assert payload["educational_topics"]
    assert "not investment recommendations" in payload["transparency"]["not_recommendation"]


def test_comparison_engine_returns_structured_sections() -> None:
    left = make_asset()
    right = make_asset(
        id=2,
        ticker="TIGZ",
        company_name="Tigere REIT",
        name="Tigere REIT",
        sector="Real Estate",
        industry="REIT",
        asset_type=AssetType.REIT,
        currency=Currency.USD,
        description="Property investment trust focused on rental income and real estate exposure.",
    )

    payload = build_comparison(left, right, subject_type="asset")
    text = str(payload).lower()

    assert payload["version"] == "1"
    assert payload["subject_type"] == "asset"
    assert payload["business_comparison"]["rows"]
    assert payload["evidence_comparison"]["stronger_evidence"] in {"left", "right", "similar"}
    assert payload["suggested_follow_up_questions"]
    assert "strong buy" not in text


def test_compare_endpoint_returns_success_envelope(monkeypatch) -> None:
    left = make_asset()
    right = make_asset(ticker="TIGZ", company_name="Tigere REIT", name="Tigere REIT", sector="Real Estate", industry="REIT")

    def fake_get_asset_by_ticker(_db, ticker):
        return left if ticker == "DLTA" else right if ticker == "TIGZ" else None

    monkeypatch.setattr(compare_module.asset_service, "get_asset_by_ticker", fake_get_asset_by_ticker)

    response = client.get("/api/v1/compare?asset_a=DLTA&asset_b=TIGZ")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Comparison retrieved successfully"
    assert body["data"]["left"]["ticker"] == "DLTA"
    assert body["data"]["right"]["ticker"] == "TIGZ"


def test_compare_endpoint_rejects_incomplete_request() -> None:
    response = client.get("/api/v1/compare?asset_a=DLTA")
    body = response.json()

    assert response.status_code == 400
    assert body["error_code"] == "INVALID_COMPARE_REQUEST"


def test_company_related_endpoint_returns_success_envelope(monkeypatch) -> None:
    delta = make_company(asset=make_asset())
    innscor = make_company(id=2, ticker="INN", name="Innscor Africa Limited", sector="Consumer Staples", industry="Food Products")

    def fake_get_company_by_ticker(*args, **kwargs):
        return delta

    def fake_list_companies(*args, **kwargs):
        return [delta, innscor], 2

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.company_service, "list_companies", fake_list_companies)

    response = client.get("/api/v1/companies/DLTA/related")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company relationships retrieved successfully"
    assert body["data"]["related_companies"][0]["ticker"] == "INN"
    assert body["data"]["knowledge_graph"]["learn_next"]

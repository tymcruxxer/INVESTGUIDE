"""Deterministic News Intelligence Engine tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import news as news_module
from app.main import app
from app.services.intelligence.news_engine import (
    build_news_research,
    classify_event,
    clear_news_intelligence_cache,
    find_related_companies,
)

client = TestClient(app)


def make_article(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    asset = SimpleNamespace(
        ticker="DLTA",
        company_name="Delta Corporation Limited",
        sector="Consumer Staples",
        asset_type="equity",
        company=None,
    )
    data = {
        "id": 42,
        "title": "ZSE regulatory update affects Delta and Innscor dividend reporting",
        "summary": "The ZSE published a regulatory announcement for listed companies.",
        "content": "Delta Corporation and Innscor Africa are among companies investors may monitor after the exchange update.",
        "content_hash": "a" * 64,
        "source": "ZSE",
        "author": "ZSE",
        "published_at": now,
        "url": "https://example.com/zse-update",
        "image_url": None,
        "language": "en",
        "sentiment": None,
        "relevance_score": None,
        "credibility_score": None,
        "assets": [asset],
        "companies": [],
        "asset_tickers": ["DLTA"],
        "created_at": now,
        "updated_at": now,
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
        "description": "Zimbabwe beverages and consumer staples company.",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_event_classifier_detects_dividend_news() -> None:
    category, reasons = classify_event("Delta declares a dividend payout after annual results")

    assert category == "Dividend"
    assert any("dividend" in reason.lower() for reason in reasons)


def test_event_classifier_detects_regulatory_news() -> None:
    category, reasons = classify_event("RBZ regulatory policy directive affects listed financial institutions")

    assert category == "Regulatory"
    assert reasons


def test_news_research_scores_high_importance_for_official_multi_company_event() -> None:
    clear_news_intelligence_cache()
    article = make_article()
    companies = [make_company(), make_company(id=2, ticker="INN", name="Innscor Africa Limited")]

    payload = build_news_research(article, companies)
    text = str(payload).lower()

    assert payload["event_category"]["label"] == "Regulatory"
    assert payload["importance"]["label"] == "High"
    assert payload["evidence"]["source_quality"]["tier"] == "Tier 1 - Official"
    assert payload["related_companies"]
    assert payload["learn_next"]
    assert payload["knowledge_graph"]["nodes"]
    assert "strong buy" not in text
    assert "price target" not in text


def test_related_companies_match_explicit_mentions() -> None:
    article = make_article(content="Econet Wireless and Delta Corporation were mentioned in market news.")
    companies = [
        make_company(),
        make_company(id=2, ticker="ECO", name="Econet Wireless Zimbabwe", sector="Telecommunications"),
    ]

    related = find_related_companies(article, companies)
    tickers = {item["ticker"] for item in related}

    assert {"DLTA", "ECO"}.issubset(tickers)


def test_news_research_endpoint_returns_success_envelope(monkeypatch) -> None:
    clear_news_intelligence_cache()
    article = make_article()
    companies = [make_company(), make_company(id=2, ticker="INN", name="Innscor Africa Limited")]

    def fake_get_news(*args, **kwargs):
        return article

    def fake_list_companies(*args, **kwargs):
        return companies, len(companies)

    monkeypatch.setattr(news_module.news_service, "get_news", fake_get_news)
    monkeypatch.setattr(news_module.company_service, "list_companies", fake_list_companies)

    response = client.get("/api/v1/news/42/research")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "News research retrieved successfully"
    assert body["data"]["article_id"] == 42
    assert body["data"]["importance"]["label"] in {"Low", "Medium", "High"}
    assert body["data"]["transparency"]["not_advice"]


def test_news_research_endpoint_returns_404_for_missing_article(monkeypatch) -> None:
    def fake_get_news(*args, **kwargs):
        return None

    monkeypatch.setattr(news_module.news_service, "get_news", fake_get_news)

    response = client.get("/api/v1/news/999/research")
    body = response.json()

    assert response.status_code == 404
    assert body["error_code"] == "NEWS_NOT_FOUND"




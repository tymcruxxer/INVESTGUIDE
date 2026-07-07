"""News route tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import news as news_module
from app.main import app

client = TestClient(app)


def make_news(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped news object for route tests."""
    now = datetime(2026, 6, 25, tzinfo=UTC)
    data = {
        "id": 1,
        "title": "Sample: Delta market note",
        "summary": "Development placeholder.",
        "content": "Sample article only.",
        "source": "InvestGuide Sample Data",
        "author": "InvestGuide Development",
        "published_at": now,
        "url": None,
        "image_url": None,
        "language": "en",
        "sentiment": None,
        "relevance_score": None,
        "credibility_score": None,
        "assets": [SimpleNamespace(ticker="DLTA")],
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_news_routes_are_registered_under_api_v1() -> None:
    """Read-only news routes are mounted under the versioned router."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/news" in routes
    assert "/api/v1/news/{news_id}" in routes


def test_list_news_endpoint_returns_success_envelope(monkeypatch) -> None:
    """List endpoint returns the global envelope and pagination metadata."""

    def fake_list_news(*args, **kwargs):
        return [make_news()], 1

    monkeypatch.setattr(news_module.news_service, "list_news", fake_list_news)

    response = client.get("/api/v1/news?asset=DLTA&page=1&limit=10&sort=desc")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "News retrieved successfully"
    assert body["data"][0]["asset_tickers"] == ["DLTA"]
    assert body["meta"]["asset"] == "DLTA"
    assert body["meta"]["has_next"] is False


def test_news_detail_not_found_returns_error_envelope(monkeypatch) -> None:
    """Missing news articles return a 404 response envelope."""

    def fake_get_news(*args, **kwargs):
        return None

    monkeypatch.setattr(news_module.news_service, "get_news", fake_get_news)

    response = client.get("/api/v1/news/999")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "News article '999' was not found",
        "error_code": "NEWS_NOT_FOUND",
        "details": {},
    }

"""Asset route tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import assets as assets_module
from app.main import app
from app.models.asset import AssetStatus, AssetType, Currency, Exchange

client = TestClient(app)


def make_asset(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped asset object for route tests."""
    now = datetime(2026, 6, 25, tzinfo=UTC)
    data = {
        "id": 1,
        "ticker": "DLTA",
        "company_name": "Delta Corporation Limited",
        "exchange": Exchange.ZSE,
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "asset_type": AssetType.EQUITY,
        "currency": Currency.ZWG,
        "description": "Zimbabwe-listed beverages company.",
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


def test_asset_routes_are_registered_under_api_v1() -> None:
    """Read-only asset routes are mounted under the versioned router."""
    routes = {route.path for route in app.routes}

    assert "/api/v1/assets" in routes
    assert "/api/v1/assets/{ticker}" in routes


def test_list_assets_endpoint_returns_success_envelope(monkeypatch) -> None:
    """List endpoint returns the global envelope and pagination metadata."""

    def fake_list_assets(*args, **kwargs):
        return [make_asset()], 1

    monkeypatch.setattr(assets_module.asset_service, "list_assets", fake_list_assets)

    response = client.get("/api/v1/assets?exchange=ZSE&page=1&limit=10")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Assets retrieved successfully"
    assert body["data"][0]["ticker"] == "DLTA"
    assert body["meta"] == {
        "page": 1,
        "limit": 10,
        "total": 1,
        "has_next": False,
    }


def test_asset_detail_not_found_returns_error_envelope(monkeypatch) -> None:
    """Missing assets return a 404 response envelope."""

    def fake_get_asset_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(
        assets_module.asset_service,
        "get_asset_by_ticker",
        fake_get_asset_by_ticker,
    )

    response = client.get("/api/v1/assets/unknown")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "Asset 'UNKNOWN' was not found",
        "error_code": "ASSET_NOT_FOUND",
        "details": {},
    }


def test_asset_assessment_endpoint_returns_success_envelope(monkeypatch) -> None:
    """Asset assessment endpoint returns the global envelope with a structured assessment."""

    def fake_get_asset_by_ticker(*args, **kwargs):
        return make_asset(
            sector="Mining",
            industry="Gold Mining",
            asset_type=AssetType.EQUITY,
            currency=Currency.USD,
            exchange=Exchange.VFEX,
            market_cap=100_000_000,
            description="Gold miner with strong local presence.",
            listing_date=datetime(2020, 1, 1, tzinfo=UTC).date(),
        )

    monkeypatch.setattr(
        assets_module.asset_service,
        "get_asset_by_ticker",
        fake_get_asset_by_ticker,
    )

    response = client.get("/api/v1/assets/DLTA/assessment")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Asset assessment retrieved successfully"
    assert body["data"]["ticker"] == "DLTA"
    assert body["data"]["assessment_version"] == "1"
    assert body["data"]["overall_assessment"] in {
        "Neutral",
        "Moderately Attractive",
        "Attractive",
    }
    assert isinstance(body["data"]["key_strengths"], list)
    assert isinstance(body["data"]["things_to_watch"], list)
    assert "generated_at" in body["data"]


def test_asset_assessment_not_found_returns_error_envelope(monkeypatch) -> None:
    """Missing asset assessment returns a 404 error envelope."""

    def fake_get_asset_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(
        assets_module.asset_service,
        "get_asset_by_ticker",
        fake_get_asset_by_ticker,
    )

    response = client.get("/api/v1/assets/unknown/assessment")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "Asset 'UNKNOWN' was not found",
        "error_code": "ASSET_NOT_FOUND",
        "details": {},
    }
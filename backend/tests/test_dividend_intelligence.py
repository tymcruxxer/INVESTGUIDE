"""Dividend Intelligence tests."""

from datetime import UTC, date, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import companies as companies_module
from app.main import app
from app.models.dividend import Dividend, DividendType
from app.services.intelligence.dividend_engine import build_dividend_intelligence, clear_dividend_cache

client = TestClient(app)


def make_company(**overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 14, tzinfo=UTC)
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
        "description": "Established beverages company.",
        "founded_year": 1946,
        "employee_count": None,
        "market": "ZSE",
        "currency": "USD",
        "status": "active",
        "assets": [],
        "news_articles": [],
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_dividend(year: int, amount: float = 27_000_000, dps: float = 0.021, **overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 14, tzinfo=UTC)
    data = {
        "id": year,
        "company_id": 1,
        "asset_id": 1,
        "announcement_date": date(year, 6, 14),
        "record_date": date(year, 7, 5),
        "ex_dividend_date": date(year, 7, 3),
        "payment_date": date(year, 7, 26),
        "fiscal_year": year,
        "dividend_type": DividendType.FINAL,
        "dividend_per_share": dps,
        "currency": "USD",
        "shares_outstanding": None,
        "total_dividend_amount": amount,
        "source_name": "InvestGuide development dividend fixture data",
        "source_type": "development_fixture",
        "source_url": None,
        "imported_at": now,
        "verified_at": None,
        "is_development_data": True,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_income(year: int, net_profit: float = 92_000_000, **overrides: object) -> SimpleNamespace:
    data = {
        "fiscal_year": year,
        "net_profit": net_profit,
        "currency": "USD",
        "source_name": "InvestGuide development financial statement fixture data",
        "is_development_data": True,
        "updated_at": datetime(2026, 7, 14, tzinfo=UTC),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_cash_flow(year: int, operating_cash_flow: float = 118_000_000, **overrides: object) -> SimpleNamespace:
    data = {
        "fiscal_year": year,
        "operating_cash_flow": operating_cash_flow,
        "free_cash_flow": 70_000_000,
        "currency": "USD",
        "source_name": "InvestGuide development financial statement fixture data",
        "is_development_data": True,
        "updated_at": datetime(2026, 7, 14, tzinfo=UTC),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_dividend_model_metadata() -> None:
    assert Dividend.__tablename__ == "dividends"
    assert "uq_dividends_company_asset_year_type_announcement" in {constraint.name for constraint in Dividend.__table__.constraints}
    assert "ix_dividends_company_id" in {index.name for index in Dividend.__table__.indexes}


def test_dividend_engine_builds_history_coverage_and_transparency() -> None:
    clear_dividend_cache()
    payload = build_dividend_intelligence(
        make_company(),
        dividends=[make_dividend(2024), make_dividend(2023, amount=18_000_000, dps=0.014)],
        income_statements=[make_income(2024), make_income(2023, net_profit=76_000_000)],
        cash_flow_statements=[make_cash_flow(2024), make_cash_flow(2023, operating_cash_flow=95_000_000)],
    )
    text = str(payload).lower()

    assert payload["dividend_status"]["label"] == "Consistent Dividend History"
    assert payload["payout_ratio"]["status"] == "Available"
    assert payload["cash_payout_ratio"]["status"] == "Available"
    assert payload["dividend_growth"]["trend_label"] == "Increasing"
    assert payload["data_transparency"]["development_data"] is True
    assert "strong buy" not in text
    assert "guaranteed income" not in text
    assert "price target" not in text


def test_dividend_yield_requires_reference_price() -> None:
    payload = build_dividend_intelligence(make_company(), dividends=[make_dividend(2024)])

    assert payload["dividend_yield"]["status"] == "Unavailable"
    assert "current or relevant reference price" in payload["dividend_yield"]["missing_inputs"]


def test_negative_profit_makes_payout_ratio_not_meaningful() -> None:
    payload = build_dividend_intelligence(
        make_company(),
        dividends=[make_dividend(2024)],
        income_statements=[make_income(2024, net_profit=-5_000_000)],
        cash_flow_statements=[make_cash_flow(2024)],
    )

    assert payload["payout_ratio"]["status"] == "Not Meaningful"
    assert payload["payout_ratio"]["value"] is None


def test_dividend_engine_handles_missing_records_transparently() -> None:
    payload = build_dividend_intelligence(make_company())

    assert payload["dividend_status"]["label"] == "Dividend Data Unavailable"
    assert "dividend history" in payload["data_transparency"]["missing_data"]
    assert payload["sustainability_assessment"]["label"] == "Insufficient Evidence"


def test_company_dividends_endpoint_returns_history(monkeypatch) -> None:
    company = make_company()
    dividends = [make_dividend(2024)]

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", lambda *args, **kwargs: company)
    monkeypatch.setattr(companies_module.dividend_service, "get_company_dividends", lambda *args, **kwargs: dividends)

    response = client.get("/api/v1/companies/DLTA/dividends")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["dividends"][0]["fiscal_year"] == 2024
    assert body["data"]["data_origin"] == "Development Preview"


def test_company_dividend_intelligence_endpoint_returns_payload(monkeypatch) -> None:
    company = make_company()
    dividends = [make_dividend(2024), make_dividend(2023, amount=18_000_000, dps=0.014)]

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", lambda *args, **kwargs: company)
    monkeypatch.setattr(companies_module.dividend_service, "get_company_dividends", lambda *args, **kwargs: dividends)
    monkeypatch.setattr(companies_module.financial_statement_service, "get_company_financial_statements", lambda *args, **kwargs: ([make_income(2024), make_income(2023, net_profit=76_000_000)], [], [make_cash_flow(2024), make_cash_flow(2023, operating_cash_flow=95_000_000)]))

    response = client.get("/api/v1/companies/DLTA/dividend-intelligence")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["intelligence"]["dividend_status"]["label"] == "Consistent Dividend History"
    assert body["data"]["intelligence"]["data_transparency"]["development_data"] is True


def test_dividend_endpoint_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", lambda *args, **kwargs: None)

    response = client.get("/api/v1/companies/UNKNOWN/dividends")

    assert response.status_code == 404
    assert response.json()["error_code"] == "COMPANY_NOT_FOUND"

"""Financial Intelligence Engine tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import companies as companies_module
from app.main import app
from app.services.intelligence.financial_engine import (
    analyze_trends,
    build_financial_intelligence,
    calculate_ratios,
    clear_financial_cache,
)

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


def make_income(year: int, **overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": year,
        "company_id": 1,
        "fiscal_year": year,
        "period": "annual",
        "currency": "USD",
        "source_name": "InvestGuide development financial statement fixture data",
        "source_url": None,
        "is_development_data": True,
        "revenue": 780_000_000 if year == 2024 else 690_000_000,
        "gross_profit": 310_000_000 if year == 2024 else 265_000_000,
        "operating_profit": 145_000_000 if year == 2024 else 118_000_000,
        "net_profit": 92_000_000 if year == 2024 else 76_000_000,
        "interest_expense": 12_000_000,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_balance(year: int, **overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": year,
        "company_id": 1,
        "fiscal_year": year,
        "period": "annual",
        "currency": "USD",
        "source_name": "InvestGuide development financial statement fixture data",
        "source_url": None,
        "is_development_data": True,
        "total_assets": 620_000_000 if year == 2024 else 565_000_000,
        "current_assets": 265_000_000,
        "inventory": 85_000_000,
        "total_liabilities": 260_000_000,
        "current_liabilities": 150_000_000,
        "total_debt": 115_000_000,
        "total_equity": 360_000_000,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_cash_flow(year: int, **overrides: object) -> SimpleNamespace:
    now = datetime(2026, 7, 13, tzinfo=UTC)
    data = {
        "id": year,
        "company_id": 1,
        "fiscal_year": year,
        "period": "annual",
        "currency": "USD",
        "source_name": "InvestGuide development financial statement fixture data",
        "source_url": None,
        "is_development_data": True,
        "operating_cash_flow": 118_000_000 if year == 2024 else 95_000_000,
        "free_cash_flow": 70_000_000 if year == 2024 else 53_000_000,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_ratio_engine_returns_interpretations_and_education() -> None:
    ratios = calculate_ratios(
        {"revenue": 100, "gross_profit": 40, "operating_profit": 20, "net_profit": 10, "interest_expense": 4},
        {"current_assets": 80, "inventory": 20, "current_liabilities": 40, "total_debt": 30, "total_equity": 100, "total_liabilities": 70, "total_assets": 170},
        {"operating_cash_flow": 35},
    )

    ratio = next(item for item in ratios if item["name"] == "Net Margin")
    assert ratio["value"] == 0.1
    assert ratio["interpretation"]
    assert ratio["why_it_matters"]
    assert ratio["educational_explanation"]


def test_trend_analysis_identifies_increasing_revenue() -> None:
    trends = analyze_trends(
        [{"fiscal_year": 2023, "revenue": 100}, {"fiscal_year": 2024, "revenue": 120}],
        [],
        [],
    )

    revenue = next(item for item in trends if item["metric"] == "Revenue")
    assert revenue["direction"] == "Increasing"
    assert revenue["why_it_matters"]


def test_financial_engine_builds_health_and_transparency() -> None:
    clear_financial_cache()
    payload = build_financial_intelligence(
        make_company(),
        income_statements=[make_income(2024), make_income(2023)],
        balance_sheets=[make_balance(2024), make_balance(2023)],
        cash_flow_statements=[make_cash_flow(2024), make_cash_flow(2023)],
    )
    text = str(payload).lower()

    assert payload["financial_health"]["label"] in {"Excellent", "Strong", "Healthy", "Moderate", "Weak", "Concerning"}
    assert payload["ratios"]
    assert payload["trend_analysis"]
    assert payload["knowledge_graph"]["nodes"]
    assert payload["transparency"]["development_data"] is True
    assert "strong buy" not in text
    assert "price target" not in text


def test_financial_engine_marks_missing_data() -> None:
    payload = build_financial_intelligence(make_company())

    assert payload["financial_health"]["missing_data"]
    assert payload["financial_health"]["uncertainty"] == "High"
    assert payload["transparency"]["missing_data"]


def test_company_financials_endpoint_returns_success_envelope(monkeypatch) -> None:
    company = make_company()

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_statements(*args, **kwargs):
        return [make_income(2024), make_income(2023)], [make_balance(2024), make_balance(2023)], [make_cash_flow(2024), make_cash_flow(2023)]

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.financial_statement_service, "get_company_financial_statements", fake_statements)

    response = client.get("/api/v1/companies/DLTA/financials")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company financial intelligence retrieved successfully"
    assert body["data"]["intelligence"]["financial_health"]["label"]
    assert len(body["data"]["income_statements"]) == 2


def test_company_financial_health_endpoint_returns_focused_payload(monkeypatch) -> None:
    company = make_company()

    def fake_get_company_by_ticker(*args, **kwargs):
        return company

    def fake_statements(*args, **kwargs):
        return [make_income(2024)], [make_balance(2024)], [make_cash_flow(2024)]

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)
    monkeypatch.setattr(companies_module.financial_statement_service, "get_company_financial_statements", fake_statements)

    response = client.get("/api/v1/companies/DLTA/financial-health")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Company financial health retrieved successfully"
    assert body["data"]["financial_health"]["label"]
    assert body["data"]["ratios"]


def test_company_financial_endpoint_returns_404(monkeypatch) -> None:
    def fake_get_company_by_ticker(*args, **kwargs):
        return None

    monkeypatch.setattr(companies_module.company_service, "get_company_by_ticker", fake_get_company_by_ticker)

    response = client.get("/api/v1/companies/UNKNOWN/financials")

    assert response.status_code == 404
    assert response.json()["error_code"] == "COMPANY_NOT_FOUND"


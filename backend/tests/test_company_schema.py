"""Company schema tests."""

from datetime import UTC, datetime

from app.models.asset import AssetStatus, Currency, Exchange
from app.schemas.company import CompanyRead


def test_company_read_normalizes_ticker() -> None:
    """Company schemas normalize ticker symbols for stable frontend routing."""
    company = CompanyRead.model_validate(
        {
            "id": 1,
            "name": "Delta Corporation Limited",
            "legal_name": "Delta Corporation Limited",
            "ticker": " dlta ",
            "exchange": Exchange.ZSE,
            "sector": "Consumer Staples",
            "industry": "Beverages",
            "country": "Zimbabwe",
            "headquarters": "Harare",
            "website": "https://www.delta.co.zw/",
            "description": "A consumer staples company.",
            "founded_year": 1946,
            "employee_count": None,
            "market": "ZSE",
            "currency": Currency.ZWG,
            "status": AssetStatus.ACTIVE,
            "logo_url": None,
            "created_at": datetime(2026, 7, 3, tzinfo=UTC),
            "updated_at": datetime(2026, 7, 3, tzinfo=UTC),
        }
    )

    assert company.ticker == "DLTA"
    assert company.status == AssetStatus.ACTIVE
    assert company.currency == Currency.ZWG
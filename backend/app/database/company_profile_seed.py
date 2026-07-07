"""Development fixture data for company enrichment profiles.

These records are intentionally marked as development seed data. They provide
structured examples for local development and tests only; they are not live
research, scraped data, or financial metrics.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.models.asset import AssetStatus, Currency, Exchange
from app.models.company_profile import ResearchStatus

DEVELOPMENT_VERIFICATION_DATE = datetime(2026, 7, 3, tzinfo=UTC)
DEVELOPMENT_SOURCE_NAME = "InvestGuide development fixture data"

COMPANY_PROFILE_FIXTURES: dict[str, dict[str, Any]] = {
    "DLTA": {
        "business_summary": "Development fixture: Delta Corporation is represented as a Zimbabwe-listed consumer staples group for local research page testing.",
        "primary_business": "Consumer beverages and related fast-moving consumer goods",
        "products_services": ["Beverages", "Consumer goods distribution"],
        "industry": "Consumer Staples",
        "sub_industry": "Beverages",
        "headquarters": "Harare, Zimbabwe",
        "founded_year": 1946,
        "website": "https://www.delta.co.zw/",
        "country": "Zimbabwe",
        "exchange": Exchange.ZSE,
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": DEVELOPMENT_VERIFICATION_DATE,
        "source_name": DEVELOPMENT_SOURCE_NAME,
        "source_url": "https://www.delta.co.zw/",
    },
    "ECO": {
        "business_summary": "Development fixture: Econet Wireless Zimbabwe is represented as a telecommunications company for enrichment workflow testing.",
        "primary_business": "Mobile telecommunications and digital connectivity services",
        "products_services": ["Mobile network services", "Data services", "Digital connectivity"],
        "industry": "Telecommunications",
        "sub_industry": "Mobile Telecommunications",
        "headquarters": "Harare, Zimbabwe",
        "website": "https://www.econet.co.zw/",
        "country": "Zimbabwe",
        "exchange": Exchange.ZSE,
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": DEVELOPMENT_VERIFICATION_DATE,
        "source_name": DEVELOPMENT_SOURCE_NAME,
        "source_url": "https://www.econet.co.zw/",
    },
    "CBZ": {
        "business_summary": "Development fixture: CBZ Holdings is represented as a diversified financial services company for structured profile testing.",
        "primary_business": "Banking and financial services",
        "products_services": ["Banking", "Financial services", "Insurance-related services"],
        "industry": "Financial Services",
        "sub_industry": "Banking",
        "headquarters": "Harare, Zimbabwe",
        "website": "https://www.cbz.co.zw/",
        "country": "Zimbabwe",
        "exchange": Exchange.ZSE,
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": DEVELOPMENT_VERIFICATION_DATE,
        "source_name": DEVELOPMENT_SOURCE_NAME,
        "source_url": "https://www.cbz.co.zw/",
    },
    "INN": {
        "business_summary": "Development fixture: Innscor Africa is represented as a consumer-focused food and light manufacturing group for enrichment workflow testing.",
        "primary_business": "Food production and consumer staples operations",
        "products_services": ["Food manufacturing", "Consumer staples", "Distribution"],
        "industry": "Consumer Staples",
        "sub_industry": "Food Production",
        "headquarters": "Harare, Zimbabwe",
        "website": "https://www.innscorafrica.com/",
        "country": "Zimbabwe",
        "exchange": Exchange.ZSE,
        "currency": Currency.ZWG,
        "status": AssetStatus.ACTIVE,
        "research_status": ResearchStatus.DEVELOPMENT,
        "last_verified": DEVELOPMENT_VERIFICATION_DATE,
        "source_name": DEVELOPMENT_SOURCE_NAME,
        "source_url": "https://www.innscorafrica.com/",
    },
}


def get_company_profile_fixture(ticker: str) -> dict[str, Any] | None:
    """Return a development profile fixture by ticker."""
    return COMPANY_PROFILE_FIXTURES.get(ticker.strip().upper())
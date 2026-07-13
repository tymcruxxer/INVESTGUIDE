"""Deterministic industry intelligence engine."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

from app.services.intelligence.utils import normalized_value, unique_ordered

INDUSTRY_ENGINE_VERSION = "1"

_INDUSTRY_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "beverages": {
        "description": "Beverage companies produce, distribute, and sell drinks through retail, wholesale, and hospitality channels.",
        "characteristics": ["Consumer demand driven", "Brand and distribution intensive", "Sensitive to input costs"],
        "risks": ["Consumer spending pressure", "Input cost inflation", "Currency exposure", "Regulatory risk"],
        "opportunities": ["Strong brands", "Broad distribution", "Defensive everyday demand"],
        "sensitivity": "Moderate economic sensitivity",
        "cycle": "Defensive",
        "education": "Beverage businesses can be easier for beginners to understand because revenue often depends on everyday consumption, pricing power, and distribution reach.",
        "related": ["Consumer Staples", "Retail", "Agriculture"],
    },
    "banking": {
        "description": "Banking businesses earn money from lending, transaction services, deposits, and financial products.",
        "characteristics": ["Interest-rate exposed", "Credit-risk sensitive", "Regulated"],
        "risks": ["Credit risk", "Interest rate risk", "Regulatory risk", "Liquidity pressure"],
        "opportunities": ["Transaction growth", "Deposit base strength", "Digital banking adoption"],
        "sensitivity": "High economic sensitivity",
        "cycle": "Cyclical",
        "education": "Banking analysis usually starts with credit quality, regulation, interest rates, and deposit strength.",
        "related": ["Financial Services", "Insurance", "Money Markets"],
    },
    "reit": {
        "description": "REITs own income-producing property and distribute rental income to investors where rules allow.",
        "characteristics": ["Income oriented", "Property backed", "Interest-rate sensitive"],
        "risks": ["Vacancy risk", "Tenant concentration", "Interest rates", "Property valuation risk"],
        "opportunities": ["Rental income", "Property diversification", "Long-term leases"],
        "sensitivity": "Moderate economic sensitivity",
        "cycle": "Income-oriented",
        "education": "REITs help users learn how property income, tenants, and interest rates shape an investment.",
        "related": ["Real Estate", "Income Investing", "Interest Rates"],
    },
    "mining": {
        "description": "Mining companies extract and sell commodities whose prices are often influenced by global markets.",
        "characteristics": ["Commodity-price exposed", "Capital intensive", "Foreign-currency sensitive"],
        "risks": ["Commodity price volatility", "Operational disruption", "Currency exposure", "Regulatory risk"],
        "opportunities": ["Export earnings", "Commodity upside", "Foreign-currency revenue"],
        "sensitivity": "High economic sensitivity",
        "cycle": "Cyclical",
        "education": "Mining analysis usually focuses on commodity prices, production reliability, costs, and currency exposure.",
        "related": ["Commodity Prices", "Foreign Currency Earnings", "Cyclical Risk"],
    },
    "telecommunications": {
        "description": "Telecommunications companies provide connectivity, digital services, and network access.",
        "characteristics": ["Infrastructure intensive", "Recurring usage", "Regulated"],
        "risks": ["Regulatory risk", "Technology investment", "Currency exposure", "Competition"],
        "opportunities": ["Data usage growth", "Digital services", "Network effects"],
        "sensitivity": "Moderate economic sensitivity",
        "cycle": "Mixed defensive and growth",
        "education": "Telecom analysis often looks at subscriber activity, network investment, regulation, and digital services.",
        "related": ["Digital Services", "Regulatory Risk", "Network Effects"],
    },
    "food products": {
        "description": "Food product companies manufacture or distribute food and related consumer staples.",
        "characteristics": ["Everyday demand", "Supply chain dependent", "Brand and distribution important"],
        "risks": ["Input cost inflation", "Supply chain", "Consumer spending pressure"],
        "opportunities": ["Defensive demand", "Brand strength", "Regional distribution"],
        "sensitivity": "Moderate economic sensitivity",
        "cycle": "Defensive",
        "education": "Food businesses show how everyday demand, input costs, and pricing power affect company quality.",
        "related": ["Consumer Staples", "Agriculture", "Retail"],
    },
}

_DEFAULT_INDUSTRY = {
    "description": "This industry does not yet have a specialized InvestGuide profile, so analysis is limited to available company facts.",
    "characteristics": ["Structured industry profile pending", "Use company facts first"],
    "risks": ["Limited structured industry data"],
    "opportunities": ["Further research can improve context"],
    "sensitivity": "Unavailable",
    "cycle": "Unavailable",
    "education": "When industry data is limited, users should focus on what the company sells, who its customers are, and what operating risks are disclosed.",
    "related": ["Evidence Strength", "Risk", "Business Model"],
}


def build_industry_intelligence(industry: str, companies: Iterable[Any] | None = None) -> dict[str, Any]:
    """Return deterministic industry context and related listed companies."""
    normalized = _normalize_industry(industry)
    template = _industry_template(normalized)
    company_rows = _companies_for_industry(normalized, companies or [])

    return {
        "version": INDUSTRY_ENGINE_VERSION,
        "industry": industry.strip() or "Unknown Industry",
        "description": template["description"],
        "typical_characteristics": template["characteristics"],
        "common_risks": template["risks"],
        "common_opportunities": template["opportunities"],
        "economic_sensitivity": template["sensitivity"],
        "cycle_profile": template["cycle"],
        "educational_summary": template["education"],
        "companies": company_rows,
        "learn_next": _learn_next(template),
        "related_industries": template["related"],
        "transparency": {
            "methodology": "Industry intelligence is selected from deterministic InvestGuide industry profiles and company metadata.",
            "data_boundary": "If an industry profile is unavailable, the engine marks the limitation instead of inventing details.",
        },
    }


def clear_industry_cache() -> None:
    """Clear cached industry templates."""
    _industry_template.cache_clear()


def _normalize_industry(industry: str) -> str:
    return " ".join((industry or "").lower().replace("&", "and").split())


@lru_cache(maxsize=128)
def _industry_template(normalized_industry: str) -> dict[str, Any]:
    for key, value in _INDUSTRY_KNOWLEDGE.items():
        if key in normalized_industry or normalized_industry in key:
            return value
    return _DEFAULT_INDUSTRY


def _companies_for_industry(industry: str, companies: Iterable[Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for company in companies:
        company_industry = _normalize_industry(normalized_value(company, "industry"))
        company_sector = normalized_value(company, "sector")
        if industry and (industry in company_industry or company_industry in industry):
            rows.append(
                {
                    "ticker": normalized_value(company, "ticker").upper(),
                    "name": normalized_value(company, "name") or normalized_value(company, "company_name"),
                    "sector": company_sector or "Unavailable",
                    "reason": f"Listed because its industry is recorded as {normalized_value(company, 'industry') or 'matching this industry'}.",
                }
            )
    return rows[:12]


def _learn_next(template: dict[str, Any]) -> list[dict[str, str]]:
    topics = unique_ordered([*template["characteristics"], *template["risks"], *template["opportunities"]])
    return [
        {
            "topic": topic,
            "why_it_matters": f"Learning about {topic.lower()} helps explain how this industry creates value or risk.",
            "path": f"/education?topic={topic.lower().replace(' ', '-')}",
        }
        for topic in topics[:6]
    ]

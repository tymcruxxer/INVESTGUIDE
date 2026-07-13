"""Deterministic Business Intelligence Engine."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable

from app.services.intelligence.competitor_engine import build_competitor_map
from app.services.intelligence.industry_engine import build_industry_intelligence
from app.services.intelligence.knowledge_graph import build_knowledge_graph
from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered

BUSINESS_ENGINE_VERSION = "1"

_BUSINESS_CACHE: dict[str, dict[str, Any]] = {}

_REVENUE_DRIVER_RULES: dict[str, list[dict[str, str]]] = {
    "consumer staples": [
        {"name": "Consumer spending", "why_it_matters": "Everyday demand influences sales volumes and pricing power."},
        {"name": "Input cost inflation", "why_it_matters": "Higher input costs can pressure margins if prices cannot adjust quickly."},
        {"name": "Distribution reach", "why_it_matters": "Broad distribution can help brands reach more customers consistently."},
    ],
    "financial services": [
        {"name": "Interest rates", "why_it_matters": "Interest rates affect lending margins, borrowing demand, and deposit behavior."},
        {"name": "Banking activity", "why_it_matters": "Transaction volumes and credit growth influence financial services revenue."},
        {"name": "Credit quality", "why_it_matters": "Loan quality affects profits and risk provisions."},
    ],
    "real estate": [
        {"name": "Rental income", "why_it_matters": "Rental collections are the core cash flow source for property-backed vehicles."},
        {"name": "Occupancy", "why_it_matters": "Vacancy levels affect income stability."},
        {"name": "Interest rates", "why_it_matters": "Rates influence property values and financing costs."},
    ],
    "mining": [
        {"name": "Commodity prices", "why_it_matters": "Commodity prices affect revenue for producers that sell into global markets."},
        {"name": "Production volume", "why_it_matters": "Operational output determines how much product can be sold."},
        {"name": "Currency exposure", "why_it_matters": "Foreign-currency revenue and local costs can affect profitability."},
    ],
    "telecommunications": [
        {"name": "Telecommunications usage", "why_it_matters": "Data, voice, and digital service usage drive recurring activity."},
        {"name": "Network investment", "why_it_matters": "Infrastructure quality affects service reliability and competitive position."},
        {"name": "Regulatory conditions", "why_it_matters": "Rules and licensing can shape operating costs and service pricing."},
    ],
}

_RISK_RULES: dict[str, list[dict[str, str]]] = {
    "consumer staples": [
        {"name": "Input cost inflation", "why_it_matters": "Cost pressure can reduce margins when pricing power is limited."},
        {"name": "Currency exposure", "why_it_matters": "Imported inputs or USD-linked costs can affect local-currency operations."},
        {"name": "Competition", "why_it_matters": "Competing brands can pressure pricing and market share."},
    ],
    "financial services": [
        {"name": "Regulatory risk", "why_it_matters": "Financial firms operate under rules that can affect lending and capital."},
        {"name": "Credit risk", "why_it_matters": "Borrower stress can lead to higher impairments."},
        {"name": "Liquidity pressure", "why_it_matters": "Funding stability matters for banks and financial institutions."},
    ],
    "real estate": [
        {"name": "Tenant concentration", "why_it_matters": "Dependence on a few tenants can make income less resilient."},
        {"name": "Vacancy risk", "why_it_matters": "Empty properties reduce rental income."},
        {"name": "Interest rates", "why_it_matters": "Rates can affect property valuations and financing costs."},
    ],
    "mining": [
        {"name": "Commodity exposure", "why_it_matters": "Revenue can move with global commodity prices."},
        {"name": "Operational disruption", "why_it_matters": "Mining output depends on reliable operations and logistics."},
        {"name": "Regulatory risk", "why_it_matters": "Mining rights, royalties, and policy can affect operations."},
    ],
    "telecommunications": [
        {"name": "Regulatory risk", "why_it_matters": "Telecoms depend on licensing, tariffs, and policy decisions."},
        {"name": "Technology investment", "why_it_matters": "Networks require continual investment to stay competitive."},
        {"name": "Competition", "why_it_matters": "Alternative providers and digital services can pressure growth."},
    ],
}


def clear_business_cache() -> None:
    """Clear process-local Business Intelligence cache."""
    _BUSINESS_CACHE.clear()


def build_business_intelligence(company: Any, companies: Iterable[Any] | None = None, profile: Any | None = None) -> dict[str, Any]:
    """Build deterministic company business intelligence."""
    companies = list(companies or [])
    cache_key = _cache_key(company, profile, companies)
    if cache_key in _BUSINESS_CACHE:
        return _BUSINESS_CACHE[cache_key]

    subject = _company_subject(company, profile)
    sector_key = _sector_key(subject)
    industry = subject["industry"] or subject["sector"] or "Unknown Industry"
    industry_payload = build_industry_intelligence(industry, companies)
    competitor_payload = build_competitor_map(company, companies)
    graph = _expanded_business_graph(company, sector_key)

    payload = {
        "version": BUSINESS_ENGINE_VERSION,
        "ticker": subject["ticker"],
        "company_name": subject["name"],
        "business_summary": _business_summary(subject),
        "business_model": _business_model(subject),
        "revenue_drivers": _drivers_for(sector_key),
        "competitive_position": _competitive_position(subject, competitor_payload),
        "industry_position": _industry_position(subject, industry_payload),
        "business_maturity": _business_maturity(subject),
        "geographic_exposure": _geographic_exposure(subject),
        "operational_risks": _risks_for(sector_key),
        "industry_intelligence": industry_payload,
        "competitors": competitor_payload,
        "knowledge_graph": graph,
        "educational_notes": _educational_notes(subject, industry_payload),
        "transparency": {
            "methodology": "Business Intelligence uses company metadata, CompanyProfile fields, related assets, industry profiles, and deterministic relationship scoring.",
            "data_boundary": "If a fact is missing, the engine marks it unavailable instead of inventing it.",
            "not_advice": "This is educational company research, not a prediction or investment recommendation.",
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _BUSINESS_CACHE[cache_key] = payload
    return payload


def _company_subject(company: Any, profile: Any | None) -> dict[str, Any]:
    products = asset_value(profile, "products_services", []) if profile is not None else []
    if products is None:
        products = []
    assets = getattr(company, "assets", []) or []
    return {
        "ticker": normalized_value(company, "ticker").upper(),
        "name": normalized_value(company, "name") or normalized_value(company, "company_name"),
        "legal_name": normalized_value(company, "legal_name"),
        "sector": normalized_value(company, "sector"),
        "industry": normalized_value(profile, "industry") if profile is not None else normalized_value(company, "industry"),
        "description": " ".join(
            part
            for part in [
                normalized_value(company, "description"),
                normalized_value(profile, "business_summary") if profile is not None else "",
                normalized_value(profile, "primary_business") if profile is not None else "",
            ]
            if part
        ),
        "primary_business": normalized_value(profile, "primary_business") if profile is not None else "",
        "products_services": [str(product) for product in products if product],
        "country": normalized_value(profile, "country") if profile is not None else normalized_value(company, "country"),
        "headquarters": normalized_value(profile, "headquarters") if profile is not None else normalized_value(company, "headquarters"),
        "founded_year": asset_value(profile, "founded_year") if profile is not None else asset_value(company, "founded_year"),
        "employee_count": asset_value(profile, "employees") if profile is not None else asset_value(company, "employee_count"),
        "exchange": normalized_value(company, "exchange"),
        "market": normalized_value(company, "market"),
        "assets": assets,
        "updated_at": asset_value(profile, "updated_at") if profile is not None else asset_value(company, "updated_at"),
    }


def _business_summary(subject: dict[str, Any]) -> dict[str, Any]:
    summary = subject["description"] or f"{subject['name']} has limited structured business description data available."
    return {
        "summary": summary,
        "why_investguide_thinks_this": _data_reasons(subject, ["description", "primary_business", "products_services"]),
    }


def _business_model(subject: dict[str, Any]) -> dict[str, Any]:
    products = subject["products_services"] or ["Products and services unavailable"]
    primary = subject["primary_business"] or subject["industry"] or subject["sector"] or "Unavailable"
    return {
        "how_it_makes_money": f"{subject['name']} appears to generate revenue through {primary.lower()} activities based on available structured profile data.",
        "main_products_services": products,
        "primary_customers": _customers_for(subject),
        "distribution_model": _distribution_for(subject),
        "why_investguide_thinks_this": _data_reasons(subject, ["primary_business", "products_services", "industry", "sector"]),
    }


def _drivers_for(sector_key: str) -> list[dict[str, str]]:
    return _REVENUE_DRIVER_RULES.get(
        sector_key,
        [{"name": "Company-specific demand", "why_it_matters": "Revenue drivers are limited because structured sector data is not yet available."}],
    )


def _risks_for(sector_key: str) -> list[dict[str, str]]:
    return _RISK_RULES.get(
        sector_key,
        [{"name": "Limited structured risk data", "why_it_matters": "Operational risks should be verified from official filings and company reports."}],
    )


def _competitive_position(subject: dict[str, Any], competitor_payload: dict[str, Any]) -> dict[str, Any]:
    description = subject["description"].lower()
    competitor_count = (
        len(competitor_payload["direct_competitors"])
        + len(competitor_payload["similar_businesses"])
        + len(competitor_payload["related_businesses"])
    )
    if any(word in description for word in ["leading", "largest", "established", "major"]):
        label = "Market Leader"
        confidence = "Medium"
        reasons = ["Available description indicates an established or leading market role."]
    elif competitor_count >= 2:
        label = "Strong Competitor"
        confidence = "Medium"
        reasons = ["The company has multiple cataloged peers in related sectors or industries."]
    elif subject["description"] or subject["products_services"]:
        label = "Niche Player"
        confidence = "Low"
        reasons = ["Available data describes the business, but peer coverage is limited."]
    else:
        label = "Emerging Player"
        confidence = "Low"
        reasons = ["Structured business and competitor data is limited."]
    return {"label": label, "confidence": confidence, "reasons": reasons}


def _industry_position(subject: dict[str, Any], industry_payload: dict[str, Any]) -> dict[str, Any]:
    industry = subject["industry"] or subject["sector"] or "Unavailable"
    peers = industry_payload.get("companies", [])
    return {
        "industry": industry,
        "summary": f"{subject['name']} is mapped to {industry}.",
        "peer_count": len(peers),
        "why_investguide_thinks_this": _data_reasons(subject, ["industry", "sector"]),
    }


def _business_maturity(subject: dict[str, Any]) -> dict[str, Any]:
    founded_year = subject["founded_year"]
    description = subject["description"].lower()
    if founded_year and founded_year <= 1990:
        label = "Mature with Stable Cash Flows"
        reason = "The company has a long operating history based on the recorded founded year."
    elif any(word in description for word in ["established", "leading", "largest", "major"]):
        label = "Mature"
        reason = "Available description suggests an established operating base."
    elif any(word in description for word in ["growth", "expansion", "new"]):
        label = "Growth"
        reason = "Available description contains growth or expansion language."
    elif subject["description"]:
        label = "Transitional"
        reason = "There is enough description for context, but maturity signals are limited."
    else:
        label = "Transitional"
        reason = "Structured data is too limited to classify maturity with confidence."
    return {"label": label, "confidence": "Medium" if subject["description"] else "Low", "reason": reason}


def _geographic_exposure(subject: dict[str, Any]) -> dict[str, Any]:
    country = subject["country"] or "Zimbabwe"
    headquarters = subject["headquarters"] or "Unavailable"
    return {
        "primary_country": country,
        "headquarters": headquarters,
        "summary": f"Current structured data maps the business primarily to {country}.",
        "why_investguide_thinks_this": _data_reasons(subject, ["country", "headquarters", "exchange"]),
    }


def _educational_notes(subject: dict[str, Any], industry_payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "title": "Start with the business model",
            "note": "Before looking at prices, understand what the company sells and what makes revenue move.",
        },
        {
            "title": f"Understand {industry_payload['industry']}",
            "note": industry_payload["educational_summary"],
        },
        {
            "title": "Separate facts from assumptions",
            "note": "InvestGuide marks missing data clearly so users can see where more research is needed.",
        },
    ]


def _expanded_business_graph(company: Any, sector_key: str) -> dict[str, Any]:
    graph = build_knowledge_graph(company)
    additions = {
        "consumer staples": ["Consumer Spending", "Inflation", "Dividend Investing", "Portfolio Diversification"],
        "financial services": ["Interest Rates", "Credit Risk", "Financial Stability", "Portfolio Diversification"],
        "real estate": ["Rental Income", "Interest Rates", "Income Investing", "Portfolio Diversification"],
        "mining": ["Commodity Prices", "Foreign Currency Earnings", "Cyclical Risk", "Portfolio Diversification"],
        "telecommunications": ["Digital Services", "Network Effects", "Regulatory Risk", "Portfolio Diversification"],
    }.get(sector_key, ["Business Model", "Risk", "Evidence Strength"])
    root = graph["root"]
    for topic in additions:
        if topic not in graph["nodes"]:
            graph["nodes"].append(topic)
        graph["edges"].append({"from": root, "to": topic, "reason": f"{topic} helps explain how {root} operates."})
    graph["learn_next"] = [
        *graph["learn_next"],
        *[
            {
                "topic": topic,
                "why_it_matters": f"Learning about {topic.lower()} helps explain this business model.",
                "path": f"/education?topic={topic.lower().replace(' ', '-')}",
            }
            for topic in additions[:4]
        ],
    ][:8]
    return graph


def _sector_key(subject: dict[str, Any]) -> str:
    sector = subject["sector"].lower()
    industry = subject["industry"].lower()
    for key in _REVENUE_DRIVER_RULES:
        if key in sector or key in industry:
            return key
    if "bank" in industry:
        return "financial services"
    if "reit" in industry or "real estate" in sector:
        return "real estate"
    if "beverage" in industry or "food" in industry:
        return "consumer staples"
    return sector or industry


def _customers_for(subject: dict[str, Any]) -> str:
    sector = _sector_key(subject)
    if sector == "financial services":
        return "Retail, business, and institutional financial-services customers."
    if sector == "telecommunications":
        return "Consumers and businesses using connectivity or digital services."
    if sector == "real estate":
        return "Tenants and property users connected to the company's property portfolio."
    if sector == "mining":
        return "Commodity buyers and export markets where production is sold."
    if sector == "consumer staples":
        return "Consumers, retailers, wholesalers, and hospitality channels."
    return "Primary customers are not specified in the available structured data."


def _distribution_for(subject: dict[str, Any]) -> str:
    sector = _sector_key(subject)
    if sector == "consumer staples":
        return "Likely retail, wholesale, and distributor channels based on sector context."
    if sector == "financial services":
        return "Branch, digital, and relationship channels based on sector context."
    if sector == "telecommunications":
        return "Network, retail, and digital-service channels based on sector context."
    if sector == "real estate":
        return "Property leases and tenant relationships based on sector context."
    return "Distribution model is not specified in the available structured data."


def _data_reasons(subject: dict[str, Any], fields: list[str]) -> list[str]:
    labels = {
        "description": "company description",
        "primary_business": "primary business field",
        "products_services": "products and services list",
        "industry": "industry field",
        "sector": "sector field",
        "country": "country field",
        "headquarters": "headquarters field",
        "exchange": "exchange field",
    }
    reasons = [f"Uses {labels[field]}." for field in fields if subject.get(field)]
    return reasons or ["Structured source data is limited, so this section is marked with low confidence."]


def _cache_key(company: Any, profile: Any | None, companies: list[Any]) -> str:
    fields = [
        normalized_value(company, "ticker").upper(),
        normalized_value(company, "updated_at"),
        normalized_value(profile, "updated_at") if profile is not None else "",
        str(len(companies)),
        ",".join(unique_ordered([normalized_value(candidate, "ticker").upper() for candidate in companies])),
    ]
    return "|".join(fields)

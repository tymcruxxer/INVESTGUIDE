"""Deterministic Sector and Industry Intelligence Engine."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Iterable

from app.models.macro import MacroIndicatorType
from app.services.intelligence.macro_engine import build_sector_macro_impact
from app.services.intelligence.utils import normalized_value, unique_ordered
from app.services.sector_service import serialize_industry_summary, serialize_sector

SECTOR_ENGINE_VERSION = "1"

_SECTOR_TEMPLATES: dict[str, dict[str, Any]] = {
    "consumer-staples": {
        "characteristics": ["Stable everyday demand", "Brand and distribution matter", "Input-cost sensitivity", "Often mature businesses"],
        "opportunities": ["Defensive consumption", "Pricing power", "Dividend potential", "Regional distribution", "Food security relevance"],
        "risks": ["Inflation pressure", "Currency-linked input costs", "Consumer spending pressure", "Competition", "Supply-chain disruption"],
        "financial": ["Revenue can be relatively stable", "Margins depend on input costs and pricing power", "Cash flow can support dividends when operations are mature", "Capital intensity varies by manufacturing depth"],
        "learn": ["Inflation", "Consumer Spending", "Pricing Power", "Margins", "Dividend Sustainability"],
        "related": [("Retail", "Consumer staples often reach customers through retail channels."), ("Agriculture", "Food and beverage supply chains can depend on agricultural inputs."), ("Manufacturing", "Many staples businesses convert raw inputs into consumer products.")],
    },
    "financial-services": {
        "characteristics": ["Interest-rate exposed", "Credit quality matters", "Regulated", "Balance-sheet intensive"],
        "opportunities": ["Deposit franchise", "Transaction growth", "Digital banking", "Credit expansion during stronger economic periods"],
        "risks": ["Credit losses", "Interest-rate shifts", "Regulatory changes", "Liquidity pressure", "Inflation effects on borrowers"],
        "financial": ["Revenue can include interest and fees", "Margins depend on funding cost and lending rates", "Cash flow analysis differs from industrial companies", "Capital adequacy matters"],
        "learn": ["Interest Rates", "Credit Risk", "Deposits", "Regulation", "Financial Statements"],
        "related": [("Money Markets", "Rates influence both bank economics and money-market alternatives."), ("Insurance", "Financial services often overlap with risk transfer and financial products."), ("Macro Economy", "Banks are closely linked to economic activity.")],
    },
    "telecommunications": {
        "characteristics": ["Recurring usage", "Infrastructure intensive", "Regulated", "Technology investment required"],
        "opportunities": ["Data usage growth", "Digital services", "Network effects", "Enterprise connectivity"],
        "risks": ["Regulatory changes", "Network capital expenditure", "Currency-linked equipment costs", "Competition"],
        "financial": ["Revenue may be recurring", "Margins depend on scale and network costs", "Cash flow must fund infrastructure investment", "Debt and capex require monitoring"],
        "learn": ["Network Effects", "Capital Expenditure", "Regulation", "Exchange Rates", "Digital Services"],
        "related": [("Technology", "Telecom platforms support digital services."), ("Financial Services", "Mobile money can connect telecom and financial activity."), ("Infrastructure", "Networks require physical and digital infrastructure.")],
    },
    "real-estate": {
        "characteristics": ["Property-backed income", "Tenant quality matters", "Interest-rate sensitive", "Occupancy driven"],
        "opportunities": ["Rental income", "Long leases", "Diversification", "Inflation-linked rent review potential"],
        "risks": ["Vacancy risk", "Tenant concentration", "Interest rates", "Property valuation risk", "Maintenance costs"],
        "financial": ["Revenue often comes from rent", "Cash flow depends on occupancy and collections", "Capital intensity can be high", "Distributions depend on lease income and debt cost"],
        "learn": ["REITs", "Rental Income", "Interest Rates", "Occupancy", "Income Investing"],
        "related": [("Construction", "Property supply and maintenance connect to construction activity."), ("Retail", "Retail tenants can drive shopping-centre income."), ("Income Investing", "REITs are often researched for income characteristics.")],
    },
    "basic-materials": {
        "characteristics": ["Commodity-price exposed", "Capital intensive", "Operationally sensitive", "Often foreign-currency linked"],
        "opportunities": ["Export earnings", "Commodity upside", "Foreign-currency revenue", "Resource base"],
        "risks": ["Commodity price volatility", "Operational disruption", "Regulation", "Energy costs", "Capital expenditure"],
        "financial": ["Revenue can move with commodity prices", "Margins depend on production cost and grade", "Cash flow can be cyclical", "Capital spending needs can be high"],
        "learn": ["Commodity Prices", "Export Earnings", "Operating Costs", "Cyclical Risk", "Exchange Rates"],
        "related": [("Mining", "Basic materials includes mining and commodity production."), ("Energy", "Mining operations can be energy intensive."), ("Manufacturing", "Raw materials feed manufacturing supply chains.")],
    },
}

_DEFAULT_TEMPLATE = {
    "characteristics": ["Sector profile still being verified", "Use company-level facts first"],
    "opportunities": ["Further verified data can improve sector context"],
    "risks": ["Limited structured sector data"],
    "financial": ["Financial characteristics are unavailable until sector reference data improves"],
    "learn": ["Evidence Strength", "Risk", "Business Model"],
    "related": [("Market Structure", "This helps explain how companies fit together.")],
}


def clear_sector_intelligence_cache() -> None:
    """Clear cached sector and industry template output."""
    _template_for.cache_clear()


def build_sector_research(sector: Any, companies: Iterable[Any], industries: Iterable[Any] | None = None) -> dict[str, Any]:
    """Build deterministic research for a persisted sector."""
    companies = list(companies)
    industries = list(industries if industries is not None else getattr(sector, "industries", []))
    template = _template_for(normalized_value(sector, "slug"))
    macro_relationships = build_sector_macro_relationships(normalized_value(sector, "name"))
    company_rows = _company_rows(companies, sector_name=normalized_value(sector, "name"))
    graph = build_sector_knowledge_graph(sector, companies=company_rows, macro_relationships=macro_relationships)
    return {
        "version": SECTOR_ENGINE_VERSION,
        "sector": serialize_sector(sector),
        "overview": {
            "what_it_is": normalized_value(sector, "overview") or normalized_value(sector, "description") or "Sector overview is not available yet.",
            "typical_businesses": [industry.name for industry in industries] or ["Industry mapping pending"],
            "why_investors_study_it": f"Investors study {sector.name} to understand demand drivers, common risks, financial characteristics, and macro exposure across similar companies.",
        },
        "typical_characteristics": template["characteristics"],
        "typical_opportunities": [{"label": item, "why_it_matters": f"{item} can shape how businesses in this sector create value, but it is not a recommendation."} for item in template["opportunities"]],
        "typical_risks": [{"label": item, "why_it_matters": _risk_reason(item)} for item in template["risks"]],
        "macro_relationships": macro_relationships,
        "financial_characteristics": template["financial"],
        "industries": [serialize_industry_summary(industry) for industry in industries],
        "companies": company_rows,
        "related_sectors": [{"name": name, "reason": reason} for name, reason in template["related"]],
        "evidence": _evidence_for(sector, companies, industries),
        "knowledge_graph": graph,
        "learn_next": graph["learn_next"],
        "transparency": _transparency(sector, "sector"),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def build_industry_research(industry: Any, companies: Iterable[Any]) -> dict[str, Any]:
    """Build deterministic research for a persisted industry."""
    companies = list(companies)
    sector = industry.sector
    template = _template_for(normalized_value(sector, "slug"))
    company_rows = _company_rows(companies, industry_name=normalized_value(industry, "name"))
    graph = build_industry_knowledge_graph(industry, companies=company_rows)
    return {
        "version": SECTOR_ENGINE_VERSION,
        "industry": {
            "id": industry.id,
            "name": industry.name,
            "slug": industry.slug,
            "description": industry.description,
            "overview": industry.overview,
            "data_origin": "Development Preview" if industry.is_development_data else "Persisted Backend",
        },
        "sector": {
            "name": sector.name,
            "slug": sector.slug,
            "description": sector.description,
        },
        "overview": industry.overview or industry.description or f"{industry.name} is part of {sector.name}.",
        "typical_business_model": f"{industry.name} businesses usually create value through products, services, assets, or distribution models linked to {sector.name.lower()}.",
        "macro_exposure": build_sector_macro_relationships(sector.name),
        "typical_risks": [{"label": item, "why_it_matters": _risk_reason(item)} for item in template["risks"][:5]],
        "typical_opportunities": [{"label": item, "why_it_matters": f"{item} can matter when comparing companies in this industry."} for item in template["opportunities"][:5]],
        "related_companies": company_rows,
        "learn_next": graph["learn_next"],
        "knowledge_graph": graph,
        "transparency": _transparency(industry, "industry"),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def build_sector_macro_relationships(sector_name: str) -> list[dict[str, str]]:
    """Return macro relationships for a sector."""
    impact = build_sector_macro_impact(sector_name)
    rows = []
    for item in impact["sensitivities"]:
        rows.append(
            {
                "indicator_type": item["indicator_type"],
                "label": item["label"],
                "relationship": item["why_it_matters"],
                "path": _macro_path(item["indicator_type"]),
            }
        )
    return rows


def build_sector_knowledge_graph(sector: Any, companies: list[dict[str, Any]], macro_relationships: list[dict[str, str]]) -> dict[str, Any]:
    """Build sector knowledge graph relationships."""
    root = normalized_value(sector, "name")
    nodes = unique_ordered([root, *[item["label"] for item in macro_relationships], *[company["ticker"] for company in companies[:5]], "Financial Statements", "Dividends", "Research"])
    edges = [
        {"from": item["label"], "to": root, "reason": item["relationship"]}
        for item in macro_relationships
    ]
    edges.extend({"from": root, "to": company["ticker"], "reason": company["reason"]} for company in companies[:5])
    edges.append({"from": root, "to": "Research", "reason": "Sector context helps explain company research without ranking companies."})
    learn = _learn_next(_template_for(normalized_value(sector, "slug")))
    return {"version": SECTOR_ENGINE_VERSION, "root": root, "nodes": nodes, "edges": edges[:12], "learn_next": learn}


def build_industry_knowledge_graph(industry: Any, companies: list[dict[str, Any]]) -> dict[str, Any]:
    """Build industry knowledge graph relationships."""
    root = industry.name
    nodes = unique_ordered([root, industry.sector.name, *[company["ticker"] for company in companies[:5]], "Business Model", "Macro Exposure"])
    edges = [
        {"from": industry.sector.name, "to": root, "reason": f"{root} is an industry within {industry.sector.name}."},
        {"from": root, "to": "Business Model", "reason": "Industry context explains how similar businesses typically make money."},
        {"from": root, "to": "Macro Exposure", "reason": "Industries respond differently to inflation, rates, GDP, currency, and commodities."},
    ]
    edges.extend({"from": root, "to": company["ticker"], "reason": company["reason"]} for company in companies[:5])
    return {"version": SECTOR_ENGINE_VERSION, "root": root, "nodes": nodes, "edges": edges[:12], "learn_next": _learn_next(_template_for(industry.sector.slug))}


def build_company_sector_summary(company: Any, sector_research: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a compact sector summary for a company page."""
    sector = normalized_value(company, "sector") or "Unavailable"
    industry = normalized_value(company, "industry") or "Unavailable"
    template = _template_for(_slug(sector))
    return {
        "sector": sector,
        "industry": industry,
        "sector_path": f"/sector/{_slug(sector)}",
        "overview": sector_research["overview"]["what_it_is"] if sector_research else f"{sector} groups companies with similar business drivers and risks.",
        "typical_risks": template["risks"][:4],
        "macro_relationships": build_sector_macro_relationships(sector),
        "related_industries": [name for name, _reason in template["related"]],
        "learn_next": _learn_next(template)[:4],
        "transparency": {
            "methodology": "Company sector summaries use the persisted sector reference layer plus deterministic sector templates.",
            "not_advice": "Sector context is educational and does not rank companies or recommend investments.",
        },
    }


@lru_cache(maxsize=128)
def _template_for(slug: str) -> dict[str, Any]:
    return _SECTOR_TEMPLATES.get(slug, _DEFAULT_TEMPLATE)


def _company_rows(companies: Iterable[Any], *, sector_name: str | None = None, industry_name: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for company in companies:
        company_sector = normalized_value(company, "sector")
        company_industry = normalized_value(company, "industry")
        sector_match = sector_name and company_sector.lower() == sector_name.lower()
        industry_match = industry_name and industry_name.lower() in company_industry.lower()
        if not (sector_match or industry_match):
            continue
        rows.append(
            {
                "ticker": normalized_value(company, "ticker").upper(),
                "name": normalized_value(company, "name") or normalized_value(company, "company_name"),
                "sector": company_sector or "Unavailable",
                "industry": company_industry or "Unavailable",
                "exchange": normalized_value(company, "exchange") or "Unavailable",
                "href": f"/company/{normalized_value(company, 'ticker').lower()}",
                "reason": f"Listed because its {'industry' if industry_match else 'sector'} is recorded as {company_industry if industry_match else company_sector}.",
            }
        )
    return rows[:20]


def _evidence_for(subject: Any, companies: list[Any], industries: list[Any]) -> dict[str, Any]:
    is_dev = bool(getattr(subject, "is_development_data", True))
    has_source = bool(getattr(subject, "source_name", None))
    confidence = "Medium" if has_source and not is_dev else "Low" if is_dev else "High"
    return {
        "evidence_strength": confidence,
        "available_data": unique_ordered(["sector reference row", f"{len(companies)} related company row(s)", f"{len(industries)} industry row(s)"]),
        "missing_data": [] if not is_dev else ["verified sector taxonomy", "official sector coverage source"],
        "transparency": "Development Preview sector data is used only until verified sector reference data exists.",
    }


def _transparency(subject: Any, subject_type: str) -> dict[str, Any]:
    return {
        "source_name": getattr(subject, "source_name", None),
        "source_url": getattr(subject, "source_url", None),
        "verification_status": getattr(subject, "verification_status", "Unavailable"),
        "data_origin": "Development Preview" if getattr(subject, "is_development_data", True) else "Persisted Backend",
        "methodology": f"{subject_type.title()} Intelligence combines persisted reference data, company metadata, macro relationship mappings, and deterministic educational templates.",
        "not_advice": "This is educational sector research, not investment advice, prediction, or recommendation.",
    }


def _risk_reason(label: str) -> str:
    return f"{label} matters because it can affect demand, margins, cash flow, financing needs, or investor interpretation across similar businesses."


def _learn_next(template: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "topic": topic,
            "why_it_matters": f"Learning about {topic.lower()} helps connect sector context to company research.",
            "path": f"/education?topic={_slug(topic)}",
        }
        for topic in unique_ordered(template["learn"])[:6]
    ]


def _slug(value: str) -> str:
    return value.lower().replace("&", "and").replace(" ", "-")


def _macro_path(indicator_type: str) -> str:
    return {
        MacroIndicatorType.INFLATION.value: "/macro/inflation",
        MacroIndicatorType.INTEREST_RATE.value: "/macro/interest-rates",
        MacroIndicatorType.EXCHANGE_RATE.value: "/macro/exchange-rates",
        MacroIndicatorType.GDP.value: "/macro/gdp",
        MacroIndicatorType.COMMODITY_PRICE.value: "/macro/commodities",
    }.get(indicator_type, "/macro/inflation")

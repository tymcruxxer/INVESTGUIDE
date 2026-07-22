"""Deterministic Macro Intelligence Engine.

The engine explains economic indicators and relationships without forecasting,
LLMs, buy/sell language, or personalized financial advice.
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Iterable

from app.models.macro import MacroIndicatorType
from app.services.intelligence.utils import normalized_value, unique_ordered
from app.services.macro_service import serialize_indicator

MACRO_INTELLIGENCE_VERSION = "1"

_TYPE_LABELS = {
    MacroIndicatorType.INFLATION: "Inflation",
    MacroIndicatorType.INTEREST_RATE: "Interest Rates",
    MacroIndicatorType.EXCHANGE_RATE: "Exchange Rates",
    MacroIndicatorType.GDP: "GDP",
    MacroIndicatorType.COMMODITY_PRICE: "Commodity Prices",
}

_MACRO_EDUCATION: dict[MacroIndicatorType, dict[str, Any]] = {
    MacroIndicatorType.INFLATION: {
        "what_it_is": "Inflation measures how quickly prices for goods and services are rising.",
        "why_investors_care": "Inflation can affect household spending power, company input costs, pricing decisions, margins, and dividend capacity.",
        "eli18": "If everyday prices rise faster than incomes, customers may buy less and companies may pay more to operate.",
        "business_impacts": ["Higher input costs", "Pressure on consumer purchasing power", "Pricing power becomes more important", "Working-capital needs may rise"],
        "sector_impacts": ["Consumer staples watch demand and margins", "Banks watch credit quality", "Retailers watch spending power", "Property owners watch rent affordability"],
        "learn": ["Interest Rates", "Consumer Spending", "Pricing Power", "Dividend Sustainability", "Risk"],
    },
    MacroIndicatorType.INTEREST_RATE: {
        "what_it_is": "Interest rates show the cost of borrowing money and the return available from safer interest-bearing products.",
        "why_investors_care": "Rates influence business financing costs, bank margins, consumer borrowing, property demand, and the attractiveness of income products.",
        "eli18": "When borrowing becomes expensive, people and companies may slow down spending or expansion.",
        "business_impacts": ["Borrowing costs can rise", "Consumer spending may slow", "Banks may see margin and credit-quality changes", "Property funding costs can increase"],
        "sector_impacts": ["Banks are rate sensitive", "Real estate is funding-cost sensitive", "Consumer companies watch spending", "Money-market products become more relevant"],
        "learn": ["Inflation", "Money Markets", "Banking", "Debt", "Income Investing"],
    },
    MacroIndicatorType.EXCHANGE_RATE: {
        "what_it_is": "Exchange rates compare the value of one currency against another.",
        "why_investors_care": "Currency movements can affect imported costs, export earnings, VFEX/USD exposure, and the real value of local-currency returns.",
        "eli18": "If the local currency weakens, imported goods can become more expensive, while USD earners may report differently.",
        "business_impacts": ["Imported inputs can become more expensive", "Export and USD revenues may provide a hedge", "Local purchasing power can change", "Currency denomination matters"],
        "sector_impacts": ["Mining often watches USD export revenue", "Manufacturers watch imported inputs", "Retail and consumer staples watch consumer prices", "VFEX listings add USD context"],
        "learn": ["USD Exposure", "VFEX", "Import Costs", "Export Revenue", "Currency Risk"],
    },
    MacroIndicatorType.GDP: {
        "what_it_is": "GDP measures the size or growth of economic activity in a country.",
        "why_investors_care": "Growth affects consumer demand, business expansion, employment, credit demand, and investor confidence.",
        "eli18": "GDP is like a broad scorecard for whether the economy is expanding or slowing.",
        "business_impacts": ["Demand can improve when economic activity grows", "Expansion plans may become more attractive", "Credit demand can change", "Cyclical sectors may be more sensitive"],
        "sector_impacts": ["Banks watch credit demand", "Consumer sectors watch household spending", "Industrial businesses watch activity levels", "Real estate watches occupancy and rents"],
        "learn": ["Economic Growth", "Consumer Demand", "Cyclical Risk", "Business Expansion", "Diversification"],
    },
    MacroIndicatorType.COMMODITY_PRICE: {
        "what_it_is": "Commodity prices track globally traded inputs and outputs such as gold, fuel, crops, and minerals.",
        "why_investors_care": "Commodity prices influence mining revenue, fuel and energy costs, agriculture incomes, manufacturing inputs, and consumer prices.",
        "eli18": "If important raw materials get more expensive or cheaper, companies connected to them can feel it in costs or sales.",
        "business_impacts": ["Mining revenue can change with export prices", "Fuel and energy costs affect many companies", "Agriculture incomes depend on crop prices", "Manufacturing input costs can move"],
        "sector_impacts": ["Mining is commodity-price sensitive", "Agriculture is crop-price sensitive", "Manufacturing watches inputs", "Consumer staples watch food and fuel costs"],
        "learn": ["Mining", "Agriculture", "Input Costs", "Foreign Currency Earnings", "Cyclical Risk"],
    },
}

_SECTOR_SENSITIVITIES: dict[str, list[tuple[MacroIndicatorType, str]]] = {
    "financial services": [
        (MacroIndicatorType.INTEREST_RATE, "Banks can be affected by lending rates, deposit costs, and credit quality."),
        (MacroIndicatorType.INFLATION, "Inflation can affect household affordability and loan repayment pressure."),
        (MacroIndicatorType.EXCHANGE_RATE, "Currency changes can affect clients with foreign-currency exposure."),
    ],
    "consumer staples": [
        (MacroIndicatorType.INFLATION, "Food and beverage demand can be affected by consumer purchasing power and input costs."),
        (MacroIndicatorType.EXCHANGE_RATE, "Imported ingredients, packaging, or equipment can become more expensive."),
        (MacroIndicatorType.GDP, "Broad economic activity influences household demand."),
    ],
    "telecommunications": [
        (MacroIndicatorType.INFLATION, "Operating and equipment costs can rise while customers watch affordability."),
        (MacroIndicatorType.EXCHANGE_RATE, "Network equipment often has foreign-currency cost exposure."),
        (MacroIndicatorType.GDP, "Digital service usage often follows business and consumer activity."),
    ],
    "real estate": [
        (MacroIndicatorType.INTEREST_RATE, "Property funding costs and alternative income yields are rate sensitive."),
        (MacroIndicatorType.INFLATION, "Rental adjustments and tenant affordability both matter."),
        (MacroIndicatorType.GDP, "Occupancy and demand can follow business activity."),
    ],
    "mining": [
        (MacroIndicatorType.COMMODITY_PRICE, "Mining revenue is linked to commodity prices and output mix."),
        (MacroIndicatorType.EXCHANGE_RATE, "Export revenue and costs often involve foreign currency."),
        (MacroIndicatorType.INFLATION, "Fuel, labour, and local operating costs may rise."),
    ],
    "agriculture": [
        (MacroIndicatorType.COMMODITY_PRICE, "Crop and input prices can shape margins."),
        (MacroIndicatorType.EXCHANGE_RATE, "Export proceeds and imported inputs can be currency sensitive."),
        (MacroIndicatorType.INFLATION, "Food prices and input costs affect producers and consumers."),
    ],
}

_DEFAULT_SENSITIVITIES = [
    (MacroIndicatorType.INFLATION, "Inflation can affect costs, pricing, and consumer demand."),
    (MacroIndicatorType.INTEREST_RATE, "Interest rates can affect financing costs and investor alternatives."),
    (MacroIndicatorType.EXCHANGE_RATE, "Exchange rates can affect imported costs, USD revenues, and currency exposure."),
    (MacroIndicatorType.GDP, "GDP context helps explain broad demand and activity levels."),
]


def clear_macro_intelligence_cache() -> None:
    """Clear deterministic macro caches."""
    _company_impact_cached.cache_clear()
    _sector_impact_cached.cache_clear()


def build_macro_overview(indicators: Iterable[Any], companies: Iterable[Any]) -> dict[str, Any]:
    """Build a macro overview payload."""
    indicators = list(indicators)
    companies = list(companies)
    return {
        "indicators": [serialize_indicator(row) for row in indicators],
        "research": [build_macro_research(row.indicator_type, [row], companies) for row in indicators],
        "transparency": {
            "methodology": "Latest acceptable verified rows are used first. Development Preview rows appear only when allowed and no verified row is available.",
            "not_advice": "Macro Intelligence explains economic relationships. It does not forecast outcomes or provide financial advice.",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "engine_version": MACRO_INTELLIGENCE_VERSION,
    }


def build_macro_research(indicator_type: MacroIndicatorType, indicators: Iterable[Any], companies: Iterable[Any]) -> dict[str, Any]:
    """Build deterministic research for one macro indicator family."""
    rows = list(indicators)
    companies = list(companies)
    education = _MACRO_EDUCATION[indicator_type]
    sectors = build_sector_macro_impact_for_type(indicator_type)
    related_companies = related_companies_for_macro(indicator_type, companies)
    graph = build_macro_knowledge_graph(indicator_type, related_companies=related_companies, sectors=[item["sector"] for item in sectors])
    latest = max(rows, key=lambda row: (row.reporting_period, row.id)) if rows else None
    return {
        "indicator_type": indicator_type.value,
        "label": _TYPE_LABELS[indicator_type],
        "current_value": serialize_indicator(latest) if latest else None,
        "historical_availability": {
            "records_available": len(rows),
            "periods": [row.reporting_period.isoformat() for row in sorted(rows, key=lambda item: item.reporting_period, reverse=True)],
        },
        "overview": education["what_it_is"],
        "why_investors_care": education["why_investors_care"],
        "typical_business_impacts": education["business_impacts"],
        "typical_sector_impacts": education["sector_impacts"],
        "evidence": build_macro_evidence(rows),
        "explain_like_im_18": education["eli18"],
        "affected_sectors": sectors,
        "affected_companies": related_companies,
        "knowledge_graph": graph,
        "learn_next": graph["learn_next"],
        "transparency": {
            "methodology": "Rule-based macro research maps indicator families to documented business, sector, and company sensitivities.",
            "data_origin": _data_origin(rows),
            "not_advice": "This explains relationships and learning paths only. It is not a forecast, prediction, or buy/sell recommendation.",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "engine_version": MACRO_INTELLIGENCE_VERSION,
    }


def build_company_macro_impact(company: Any, indicators: Iterable[Any]) -> dict[str, Any]:
    """Explain how macro factors typically relate to one company."""
    signature = _company_signature(company, indicators)
    return _company_impact_cached(*signature)


def build_sector_macro_impact(sector: str) -> dict[str, Any]:
    """Return reusable sector macro sensitivities."""
    return _sector_impact_cached((sector or "General").lower())


def build_sector_macro_impact_for_type(indicator_type: MacroIndicatorType) -> list[dict[str, str]]:
    """Return sectors commonly affected by one macro type."""
    affected: list[dict[str, str]] = []
    for sector, sensitivities in _SECTOR_SENSITIVITIES.items():
        for macro_type, reason in sensitivities:
            if macro_type == indicator_type:
                affected.append({"sector": sector.title(), "reason": reason})
                break
    return affected[:6]


def related_companies_for_macro(indicator_type: MacroIndicatorType, companies: Iterable[Any]) -> list[dict[str, str]]:
    """Return companies with sectors commonly connected to a macro type."""
    related: list[dict[str, str]] = []
    for company in companies:
        sector = normalized_value(company, "sector").lower()
        sensitivities = _sensitivities_for_sector(sector)
        for macro_type, reason in sensitivities:
            if macro_type == indicator_type:
                related.append(
                    {
                        "ticker": normalized_value(company, "ticker").upper(),
                        "name": normalized_value(company, "name") or normalized_value(company, "company_name"),
                        "sector": normalized_value(company, "sector") or "Unavailable",
                        "reason": reason,
                        "href": f"/company/{normalized_value(company, 'ticker').lower()}",
                    }
                )
                break
    return [item for item in related if item["ticker"]][:8]


def build_macro_evidence(rows: Iterable[Any]) -> dict[str, Any]:
    """Explain source quality and data availability for macro values."""
    rows = list(rows)
    if not rows:
        return {
            "confidence": "Low",
            "source_quality": "Unavailable",
            "data_completeness": 0,
            "data_used": [],
            "missing_data": ["macro indicator values", "source metadata"],
            "why_confidence": ["No persisted macro data is available for this indicator yet."],
        }
    verified = [row for row in rows if not row.is_development_data]
    has_sources = all(row.source_name for row in rows)
    has_verified_at = any(row.verified_at for row in rows)
    completeness = 100 if has_sources and (verified or has_verified_at) else 70 if has_sources else 45
    confidence = "High" if verified and has_verified_at else "Medium" if verified or has_sources else "Low"
    source_quality = "Verified Source" if verified else "Development Preview"
    return {
        "confidence": confidence,
        "source_quality": source_quality,
        "data_completeness": completeness,
        "data_used": unique_ordered([row.source_name or "Unknown source" for row in rows]),
        "missing_data": [] if confidence == "High" else ["verified live source metadata"] if not verified else ["verified_at timestamp"],
        "why_confidence": [
            f"{len(rows)} latest acceptable macro record(s) are available.",
            "Verified rows take precedence over Development Preview rows.",
            "Development Preview data is used only when verified data is unavailable and fixtures are allowed.",
        ],
    }


def build_macro_knowledge_graph(indicator_type: MacroIndicatorType, related_companies: list[dict[str, str]] | None = None, sectors: list[str] | None = None) -> dict[str, Any]:
    """Return deterministic macro concept graph."""
    label = _TYPE_LABELS[indicator_type]
    education = _MACRO_EDUCATION[indicator_type]
    topics = unique_ordered([label, *education["learn"], *(sectors or [])])
    companies = related_companies or []
    nodes = unique_ordered([label, *topics, *[company["ticker"] for company in companies[:4]]])
    edges = [{"from": label, "to": topic, "reason": f"{topic} helps explain how {label.lower()} affects investors."} for topic in topics[1:6]]
    for company in companies[:4]:
        edges.append({"from": label, "to": company["ticker"], "reason": company["reason"]})
    learn_next = [
        {
            "topic": topic,
            "why_it_matters": f"Learning about {topic.lower()} helps connect macro context to company research.",
            "path": f"/education?topic={topic.lower().replace(' ', '-')}",
        }
        for topic in unique_ordered(education["learn"])[:6]
    ]
    return {"version": MACRO_INTELLIGENCE_VERSION, "root": label, "nodes": nodes, "edges": edges[:12], "learn_next": learn_next}


def _data_origin(rows: Iterable[Any]) -> str:
    rows = list(rows)
    if not rows:
        return "Unavailable"
    if any(not row.is_development_data for row in rows):
        return "Persisted Backend"
    return "Development Preview"


def _sensitivities_for_sector(sector: str) -> list[tuple[MacroIndicatorType, str]]:
    sector_key = sector.lower()
    for key, sensitivities in _SECTOR_SENSITIVITIES.items():
        if key in sector_key:
            return sensitivities
    return _DEFAULT_SENSITIVITIES


def _company_signature(company: Any, indicators: Iterable[Any]) -> tuple[str, str, str, str, tuple[tuple[str, str, bool], ...]]:
    indicator_sig = tuple(sorted((row.indicator_type.value, row.reporting_period.isoformat(), bool(row.is_development_data)) for row in indicators))
    return (
        normalized_value(company, "ticker").upper(),
        normalized_value(company, "name") or normalized_value(company, "company_name"),
        normalized_value(company, "sector"),
        normalized_value(company, "industry"),
        indicator_sig,
    )


@lru_cache(maxsize=256)
def _company_impact_cached(ticker: str, name: str, sector: str, industry: str, indicator_sig: tuple[tuple[str, str, bool], ...]) -> dict[str, Any]:
    sensitivities = _sensitivities_for_sector(sector)
    factors = []
    for macro_type, reason in sensitivities:
        chain = _impact_chain(macro_type, sector, name or ticker)
        factors.append(
            {
                "indicator_type": macro_type.value,
                "label": _TYPE_LABELS[macro_type],
                "why_it_matters": reason,
                "relationship_chain": chain,
                "explanation": " -> ".join(chain),
                "not_prediction": "This is a relationship map, not a forecast of company performance.",
            }
        )
    return {
        "ticker": ticker,
        "company_name": name or ticker,
        "sector": sector or "Unavailable",
        "industry": industry or "Unavailable",
        "factors": factors,
        "knowledge_graph": build_macro_knowledge_graph(sensitivities[0][0] if sensitivities else MacroIndicatorType.INFLATION),
        "transparency": {
            "methodology": "Company impact uses deterministic sector and industry sensitivity mappings plus persisted macro-data availability.",
            "data_points_seen": len(indicator_sig),
            "not_advice": "Macro Factors are educational relationships only and do not predict prices, profits, dividends, or returns.",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "engine_version": MACRO_INTELLIGENCE_VERSION,
    }


@lru_cache(maxsize=128)
def _sector_impact_cached(sector_key: str) -> dict[str, Any]:
    sensitivities = _sensitivities_for_sector(sector_key)
    return {
        "sector": sector_key.title() if sector_key else "General",
        "sensitivities": [
            {
                "indicator_type": macro_type.value,
                "label": _TYPE_LABELS[macro_type],
                "why_it_matters": reason,
            }
            for macro_type, reason in sensitivities
        ],
        "transparency": {
            "methodology": "Sector macro sensitivity is mapped deterministically from InvestGuide's education taxonomy.",
            "not_advice": "This explains sector exposure concepts only.",
        },
    }


def _impact_chain(macro_type: MacroIndicatorType, sector: str, company_name: str) -> list[str]:
    if macro_type == MacroIndicatorType.INFLATION:
        return ["Inflation", "Consumer purchasing power", sector or "Business demand", company_name, "Revenue and margins", "Cash flow", "Dividend capacity"]
    if macro_type == MacroIndicatorType.INTEREST_RATE:
        return ["Interest rates", "Borrowing cost", "Consumer spending or funding", company_name, "Profitability", "Investment capacity"]
    if macro_type == MacroIndicatorType.EXCHANGE_RATE:
        return ["Exchange rate", "Imported costs or USD earnings", sector or "Operating exposure", company_name, "Margins", "Real investor returns"]
    if macro_type == MacroIndicatorType.GDP:
        return ["GDP", "Economic activity", "Consumer and business demand", company_name, "Sales activity", "Expansion confidence"]
    return ["Commodity prices", "Input costs or export revenue", sector or "Sector exposure", company_name, "Margins", "Cash generation"]


def _indicator_summary(indicator_type: MacroIndicatorType) -> str:
    return _MACRO_EDUCATION[indicator_type]["why_investors_care"]


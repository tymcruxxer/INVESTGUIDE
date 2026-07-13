"""Deterministic related investment engine."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

from app.services.intelligence.knowledge_graph import build_knowledge_graph
from app.services.intelligence.utils import normalized_value, unique_ordered

RELATED_ENGINE_VERSION = "1"


def build_related_research(company: Any, companies: Iterable[Any], limit: int = 4) -> dict[str, Any]:
    """Build related company, sector, asset type, and education relationships."""
    related = _rank_related_companies(company, companies, limit=limit)
    graph = build_knowledge_graph(company)
    sector = normalized_value(company, "sector") or "General"
    exchange = normalized_value(company, "exchange") or "Market"
    asset_types = _asset_types_for(company)

    return {
        "version": RELATED_ENGINE_VERSION,
        "ticker": normalized_value(company, "ticker").upper(),
        "related_companies": related,
        "related_sectors": [
            {
                "name": sector,
                "reason": f"{sector} helps group businesses with similar operating drivers.",
            },
            {
                "name": exchange,
                "reason": f"{exchange} context explains listing rules, currency exposure, and liquidity considerations.",
            },
        ],
        "related_asset_types": asset_types,
        "educational_topics": graph["learn_next"],
        "knowledge_graph": graph,
        "transparency": {
            "methodology": "Related items are ranked by shared sector, industry, exchange, asset type, and descriptive overlap.",
            "not_recommendation": "These links are educational research paths, not investment recommendations.",
        },
    }


def clear_related_cache() -> None:
    """Clear deterministic related-engine cache."""
    _relationship_score.cache_clear()


def _rank_related_companies(company: Any, companies: Iterable[Any], limit: int) -> list[dict[str, Any]]:
    ticker = normalized_value(company, "ticker").upper()
    scored: list[tuple[int, str, Any, list[str]]] = []
    for candidate in companies:
        candidate_ticker = normalized_value(candidate, "ticker").upper()
        if not candidate_ticker or candidate_ticker == ticker:
            continue
        score, reasons = _relationship_score(_signature(company), _signature(candidate))
        if score <= 0:
            continue
        scored.append((score, candidate_ticker, candidate, reasons))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [
        {
            "ticker": normalized_value(candidate, "ticker").upper(),
            "name": normalized_value(candidate, "name") or normalized_value(candidate, "company_name"),
            "sector": normalized_value(candidate, "sector") or "Unavailable",
            "industry": normalized_value(candidate, "industry") or "Unavailable",
            "exchange": normalized_value(candidate, "exchange") or "Unavailable",
            "relationship_score": score,
            "reasons": reasons,
            "href": f"/company/{normalized_value(candidate, 'ticker').lower()}",
        }
        for score, _ticker, candidate, reasons in scored[:limit]
    ]


def _asset_types_for(company: Any) -> list[dict[str, str]]:
    assets = getattr(company, "assets", []) or []
    asset_types = unique_ordered([normalized_value(asset, "asset_type") for asset in assets])
    if not asset_types:
        asset_types = ["company"]
    return [
        {
            "name": asset_type,
            "reason": f"{asset_type.replace('_', ' ').title()} changes how investors evaluate income, growth, liquidity, and risk.",
        }
        for asset_type in asset_types
    ]


def _signature(subject: Any) -> tuple[str, str, str, str, str]:
    assets = getattr(subject, "assets", []) or []
    asset_type = normalized_value(assets[0], "asset_type") if assets else normalized_value(subject, "asset_type")
    return (
        normalized_value(subject, "sector").lower(),
        normalized_value(subject, "industry").lower(),
        normalized_value(subject, "exchange").lower(),
        asset_type.lower(),
        normalized_value(subject, "description").lower(),
    )


@lru_cache(maxsize=512)
def _relationship_score(left: tuple[str, str, str, str, str], right: tuple[str, str, str, str, str]) -> tuple[int, list[str]]:
    left_sector, left_industry, left_exchange, left_type, left_description = left
    right_sector, right_industry, right_exchange, right_type, right_description = right
    score = 0
    reasons: list[str] = []

    if left_sector and left_sector == right_sector:
        score += 45
        reasons.append(f"Both operate in the {left_sector.title()} sector.")
    if left_industry and left_industry == right_industry:
        score += 30
        reasons.append(f"Both share the {left_industry.title()} industry.")
    if left_exchange and left_exchange == right_exchange:
        score += 15
        reasons.append(f"Both are connected to the {left_exchange.upper()} market.")
    if left_type and left_type == right_type:
        score += 10
        reasons.append(f"Both use the {left_type.replace('_', ' ')} investment structure.")

    shared_words = sorted(set(left_description.split()) & set(right_description.split()))
    meaningful = [word for word in shared_words if len(word) > 6]
    if meaningful:
        score += min(10, len(meaningful) * 2)
        reasons.append("Descriptions contain overlapping business terms.")

    if not reasons and left_exchange and right_exchange:
        score += 5
        reasons.append("Both are part of the local investable universe.")

    return score, reasons[:4]

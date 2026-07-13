"""Deterministic competitor and related-business engine."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

from app.services.intelligence.utils import normalized_value

COMPETITOR_ENGINE_VERSION = "1"


def build_competitor_map(company: Any, companies: Iterable[Any], limit: int = 6) -> dict[str, Any]:
    """Return direct, similar, and related businesses with explanations."""
    subject_signature = _signature(company)
    rows: list[tuple[int, str, str, Any, list[str]]] = []

    for candidate in companies:
        if normalized_value(candidate, "ticker").upper() == subject_signature[0]:
            continue
        score, category, reasons = _competitor_score(subject_signature, _signature(candidate))
        if score <= 0:
            continue
        rows.append((score, category, normalized_value(candidate, "ticker").upper(), candidate, reasons))

    rows.sort(key=lambda item: (-item[0], item[2]))

    return {
        "version": COMPETITOR_ENGINE_VERSION,
        "ticker": subject_signature[0],
        "direct_competitors": _rows_for(rows, "Direct Competitor", limit),
        "similar_businesses": _rows_for(rows, "Similar Business", limit),
        "related_businesses": _rows_for(rows, "Related Business", limit),
        "transparency": {
            "methodology": "Competitors are ranked by shared industry, sector, exchange, market, and descriptive overlap.",
            "data_boundary": "The engine only returns companies present in the current company catalog.",
            "not_recommendation": "These relationships are research links, not investment recommendations.",
        },
    }


def clear_competitor_cache() -> None:
    """Clear deterministic competitor scoring cache."""
    _competitor_score.cache_clear()


def _rows_for(rows: list[tuple[int, str, str, Any, list[str]]], category: str, limit: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for score, row_category, _ticker, company, reasons in rows:
        if row_category != category:
            continue
        result.append(
            {
                "ticker": normalized_value(company, "ticker").upper(),
                "name": normalized_value(company, "name") or normalized_value(company, "company_name"),
                "sector": normalized_value(company, "sector") or "Unavailable",
                "industry": normalized_value(company, "industry") or "Unavailable",
                "relationship_score": score,
                "relationship_type": category,
                "reasons": reasons,
                "href": f"/company/{normalized_value(company, 'ticker').lower()}",
            }
        )
        if len(result) >= limit:
            break
    return result


def _signature(company: Any) -> tuple[str, str, str, str, str, str]:
    return (
        normalized_value(company, "ticker").upper(),
        normalized_value(company, "sector").lower(),
        normalized_value(company, "industry").lower(),
        normalized_value(company, "exchange").lower(),
        normalized_value(company, "market").lower(),
        normalized_value(company, "description").lower(),
    )


@lru_cache(maxsize=512)
def _competitor_score(left: tuple[str, str, str, str, str, str], right: tuple[str, str, str, str, str, str]) -> tuple[int, str, list[str]]:
    _left_ticker, left_sector, left_industry, left_exchange, left_market, left_description = left
    _right_ticker, right_sector, right_industry, right_exchange, right_market, right_description = right
    score = 0
    reasons: list[str] = []

    if left_industry and left_industry == right_industry:
        score += 55
        reasons.append(f"Both operate in the {left_industry.title()} industry.")
    if left_sector and left_sector == right_sector:
        score += 30
        reasons.append(f"Both operate in the {left_sector.title()} sector.")
    if left_exchange and left_exchange == right_exchange:
        score += 8
        reasons.append(f"Both are listed in the {left_exchange.upper()} market.")
    if left_market and left_market == right_market:
        score += 5
        reasons.append("Both share the same market context.")

    shared_terms = sorted(set(left_description.split()) & set(right_description.split()))
    meaningful = [term for term in shared_terms if len(term) > 6]
    if meaningful:
        score += min(12, len(meaningful) * 3)
        reasons.append("Company descriptions contain overlapping business terms.")

    if score >= 75:
        category = "Direct Competitor"
    elif score >= 35:
        category = "Similar Business"
    else:
        category = "Related Business"

    return score, category, reasons[:4]

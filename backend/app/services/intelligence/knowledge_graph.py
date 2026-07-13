"""Lightweight deterministic financial knowledge graph.

This is intentionally not a graph database. It provides a small structured
relationship map that deterministic research surfaces can use to keep users
moving from one concept to the next without inventing recommendations.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.services.intelligence.utils import normalized_value, unique_ordered

KNOWLEDGE_GRAPH_VERSION = "1"

_SECTOR_TOPICS: dict[str, list[str]] = {
    "consumer staples": ["Consumer Staples", "Defensive Businesses", "Dividend Investing", "Long-Term Investing"],
    "telecommunications": ["Telecommunications", "Network Effects", "Digital Services", "Regulatory Risk"],
    "financial services": ["Banking", "Credit Risk", "Interest Rates", "Financial Stability"],
    "real estate": ["REITs", "Rental Income", "Property Diversification", "Income Investing"],
    "mining": ["Mining", "Commodity Prices", "Foreign Currency Earnings", "Cyclical Risk"],
    "agriculture": ["Agriculture", "Export Markets", "Weather Risk", "Food Security"],
}

_ASSET_TYPE_TOPICS: dict[str, list[str]] = {
    "equity": ["Equities", "Business Ownership", "Capital Growth", "Market Volatility"],
    "reit": ["REITs", "Rental Income", "Property Diversification", "Income Investing"],
    "bond": ["Bonds", "Interest Income", "Credit Quality", "Duration Risk"],
    "money_market": ["Money Markets", "Liquidity", "Capital Preservation", "Interest Rates"],
    "alternative": ["Alternative Assets", "Specialized Risk", "Diversification"],
}

_EXCHANGE_TOPICS: dict[str, list[str]] = {
    "zse": ["Zimbabwe Stock Exchange", "Local Currency Exposure", "Market Liquidity"],
    "vfex": ["Victoria Falls Stock Exchange", "USD Exposure", "Exchange Rules"],
}

_CONCEPT_EDGES: dict[str, list[str]] = {
    "Consumer Staples": ["Defensive Businesses", "Dividend Investing", "Long-Term Investing"],
    "Dividend Investing": ["Income Investing", "Payout Sustainability", "Portfolio Diversification"],
    "REITs": ["Rental Income", "Property Diversification", "Interest Rates"],
    "Banking": ["Credit Risk", "Interest Rates", "Financial Stability"],
    "Mining": ["Commodity Prices", "Foreign Currency Earnings", "Cyclical Risk"],
    "Telecommunications": ["Network Effects", "Regulatory Risk", "Digital Services"],
    "Equities": ["Business Ownership", "Market Volatility", "Long-Term Investing"],
    "Risk": ["Liquidity", "Diversification", "Evidence Strength"],
    "Portfolio Diversification": ["Sector Exposure", "Asset Types", "Risk Balance"],
}

_TOPIC_DESCRIPTIONS: dict[str, str] = {
    "Consumer Staples": "Companies that sell everyday goods can behave differently from highly cyclical businesses.",
    "Dividend Investing": "Dividend education helps users understand income, payout sustainability, and reinvestment.",
    "REITs": "REITs help investors learn how property income differs from ordinary company shares.",
    "Risk": "Risk education explains what can go wrong and how evidence changes confidence.",
    "Diversification": "Diversification teaches why spreading exposure can reduce dependence on one company or sector.",
    "Zimbabwe Stock Exchange": "ZSE context helps users understand local listing, liquidity, and currency exposure.",
    "Victoria Falls Stock Exchange": "VFEX context helps users understand USD-denominated listings and exchange rules.",
}


def build_knowledge_graph(subject: Any) -> dict[str, Any]:
    """Return a deterministic concept graph for a company or asset."""
    ticker = normalized_value(subject, "ticker").upper()
    sector = normalized_value(subject, "sector")
    asset_type = normalized_value(subject, "asset_type")
    exchange = normalized_value(subject, "exchange")
    root = normalized_value(subject, "name") or normalized_value(subject, "company_name") or ticker

    topics = _topics_for(sector, asset_type, exchange)
    nodes = unique_ordered([root, *topics, "Risk", "Diversification"])
    edges = _edges_for(root, nodes)

    learn_next = [
        {
            "topic": topic,
            "why_it_matters": _TOPIC_DESCRIPTIONS.get(
                topic,
                f"Learning about {topic.lower()} helps explain how this investment fits into a broader financial picture.",
            ),
            "path": f"/education?topic={_slug(topic)}",
        }
        for topic in topics[:6]
    ]

    return {
        "version": KNOWLEDGE_GRAPH_VERSION,
        "root": root,
        "nodes": nodes,
        "edges": edges,
        "learn_next": learn_next,
    }


@lru_cache(maxsize=256)
def _topics_for_cached(sector: str, asset_type: str, exchange: str) -> tuple[str, ...]:
    topics: list[str] = []
    sector_key = sector.lower()
    asset_key = asset_type.lower()
    exchange_key = exchange.lower()

    for key, values in _SECTOR_TOPICS.items():
        if key in sector_key:
            topics.extend(values)
            break

    topics.extend(_ASSET_TYPE_TOPICS.get(asset_key, []))
    topics.extend(_EXCHANGE_TOPICS.get(exchange_key, []))
    topics.extend(["Risk", "Diversification"])
    return tuple(unique_ordered(topics))


def _topics_for(sector: str, asset_type: str, exchange: str) -> list[str]:
    return list(_topics_for_cached(sector, asset_type, exchange))


def _edges_for(root: str, nodes: list[str]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for node in nodes[1:4]:
        edges.append({"from": root, "to": node, "reason": f"{node} helps explain {root}."})
    for source, targets in _CONCEPT_EDGES.items():
        if source in nodes:
            for target in targets:
                if target in nodes or len(edges) < 10:
                    edges.append({"from": source, "to": target, "reason": f"{target} is a useful next concept after {source}."})
    return edges[:12]


def _slug(topic: str) -> str:
    return topic.lower().replace("&", "and").replace(" ", "-")

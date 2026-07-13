"""Deterministic News Intelligence Engine.

This module classifies and explains financial news without using LLMs,
predictions, sentiment models, or investment advice language.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Iterable

from app.services.intelligence.knowledge_graph import build_knowledge_graph
from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered

NEWS_INTELLIGENCE_VERSION = "1"

_NEWS_RESEARCH_CACHE: dict[str, dict[str, Any]] = {}

_CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Earnings": ("earnings", "profit", "revenue", "results", "trading update", "financial performance"),
    "Dividend": ("dividend", "distribution", "payout", "income distribution"),
    "Expansion": ("expansion", "opens", "capacity", "new branch", "new plant", "growth project"),
    "Acquisition": ("acquisition", "acquire", "merger", "takeover", "stake"),
    "Regulatory": ("regulation", "regulatory", "policy", "compliance", "license", "directive"),
    "Management": ("appoints", "resigns", "chief executive", "ceo", "board", "management"),
    "Product Launch": ("launch", "product", "service", "platform", "offering"),
    "Partnership": ("partnership", "partner", "collaboration", "agreement", "deal"),
    "Litigation": ("litigation", "lawsuit", "court", "legal", "dispute"),
    "Macro Economy": ("inflation", "interest rate", "monetary policy", "gdp", "zimstat", "rbz"),
    "Exchange": ("zse", "vfex", "listing", "delisting", "exchange", "market update"),
    "Commodity": ("gold", "platinum", "commodity", "mining", "mineral"),
    "Currency": ("currency", "exchange rate", "usd", "zwg", "foreign currency"),
    "Market Update": ("market", "indices", "turnover", "trading", "share price"),
}

_CATEGORY_PRIORITY = [
    "Regulatory",
    "Dividend",
    "Earnings",
    "Acquisition",
    "Litigation",
    "Macro Economy",
    "Currency",
    "Commodity",
    "Exchange",
    "Expansion",
    "Management",
    "Product Launch",
    "Partnership",
    "Market Update",
]

_CATEGORY_EDUCATION: dict[str, dict[str, Any]] = {
    "Dividend": {
        "why": "A dividend announcement explains how a company intends to return profits to shareholders.",
        "eli18": "This company may be sharing part of its profits with investors.",
        "learn": ["Dividends", "Income Investing", "Payout Sustainability"],
    },
    "Earnings": {
        "why": "Earnings news helps users understand whether a company's operations are improving, stable, or under pressure.",
        "eli18": "This is like checking a company's report card to see how the business performed.",
        "learn": ["Earnings", "Revenue", "Profitability"],
    },
    "Regulatory": {
        "why": "Regulatory news matters because rules can change costs, risks, and operating conditions for companies.",
        "eli18": "The rules of the game may be changing, so companies may need to adapt.",
        "learn": ["Regulatory Risk", "Policy Risk", "Compliance"],
    },
    "Macro Economy": {
        "why": "Macro news affects the wider economy and can influence consumer spending, interest rates, currencies, and company costs.",
        "eli18": "This is about the bigger economy around companies, not just one business.",
        "learn": ["Inflation", "Interest Rates", "Macroeconomics"],
    },
    "Currency": {
        "why": "Currency news matters because exchange rates can affect imported costs, USD revenues, and local purchasing power.",
        "eli18": "If money values move, company costs and investor returns can feel different.",
        "learn": ["Currency Exposure", "USD Exposure", "Exchange Rates"],
    },
    "Commodity": {
        "why": "Commodity news matters for mining, agriculture, and businesses exposed to global input or export prices.",
        "eli18": "When prices of things like gold or crops move, companies connected to them can be affected.",
        "learn": ["Commodity Prices", "Cyclical Risk", "Foreign Currency Earnings"],
    },
    "Exchange": {
        "why": "Exchange news helps users understand market structure, listing rules, liquidity, and trading access.",
        "eli18": "This is about the marketplace where investments are listed and traded.",
        "learn": ["Zimbabwe Stock Exchange", "Victoria Falls Stock Exchange", "Market Liquidity"],
    },
}

_DEFAULT_EDUCATION = {
    "why": "This article matters because it may add context about companies, sectors, markets, or financial concepts users should understand before investing.",
    "eli18": "This news gives extra background that can help you understand an investment better.",
    "learn": ["Financial News", "Evidence Strength", "Risk"],
}

_OFFICIAL_SOURCES = ("zse", "vfex", "rbz", "zimstat")
_INSTITUTIONAL_SOURCES = ("ih securities", "mmc capital", "old mutual", "abc stockbrokers")
_JOURNALISM_SOURCES = ("financial gazette", "newsday", "herald")


def clear_news_intelligence_cache() -> None:
    """Clear process-local News Intelligence cache."""
    _NEWS_RESEARCH_CACHE.clear()


def build_news_research(article: Any, companies: Iterable[Any] | None = None) -> dict[str, Any]:
    """Build deterministic research for a single news article."""
    companies = list(companies or [])
    cache_key = _cache_key(article, companies)
    if cache_key in _NEWS_RESEARCH_CACHE:
        return _NEWS_RESEARCH_CACHE[cache_key]

    text = _article_text(article)
    category, category_reasons = classify_event(text)
    related_companies = find_related_companies(article, companies, text)
    related_sectors = _related_sectors(article, related_companies)
    related_asset_types = _related_asset_types(article)
    importance = score_importance(category, article, related_companies, related_sectors)
    evidence = build_evidence(article, related_companies)
    education = _education_for(category)
    graph = _news_knowledge_graph(article, category, related_sectors, related_asset_types)
    learn_next = _merge_learning(education["learn"], graph["learn_next"])
    related_topics = unique_ordered([category, *education["learn"], *graph["nodes"][1:7]])

    payload = {
        "article_id": asset_value(article, "id"),
        "title": normalized_value(article, "title"),
        "summary": normalized_value(article, "summary"),
        "event_category": {"label": category, "reasons": category_reasons},
        "importance": importance,
        "evidence": evidence,
        "why_it_matters": education["why"],
        "explain_like_im_18": education["eli18"],
        "related_companies": related_companies,
        "related_sectors": related_sectors,
        "related_asset_types": related_asset_types,
        "related_topics": related_topics,
        "learn_next": learn_next,
        "knowledge_graph": graph,
        "transparency": {
            "methodology": "Rule-based classification uses article keywords, linked companies/assets, source quality, and data completeness.",
            "not_advice": "News Intelligence explains context and learning paths only. It does not predict prices or provide buy/sell advice.",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "engine_version": NEWS_INTELLIGENCE_VERSION,
    }
    _NEWS_RESEARCH_CACHE[cache_key] = payload
    return payload


def classify_event(text: str) -> tuple[str, list[str]]:
    """Classify a news event from deterministic keyword rules."""
    lowered = text.lower()
    matches: list[tuple[int, str, list[str]]] = []
    for category, keywords in _CATEGORY_KEYWORDS.items():
        found = [keyword for keyword in keywords if keyword in lowered]
        if found:
            matches.append((len(found), category, found[:3]))

    if not matches:
        return "Market Update", ["No specific event keyword dominated; classified as a general market update."]

    matches.sort(key=lambda item: (_CATEGORY_PRIORITY.index(item[1]) if item[1] in _CATEGORY_PRIORITY else 999, -item[0]))
    _score, category, found = matches[0]
    return category, [f"Matched keyword: {keyword}" for keyword in found]


def score_importance(category: str, article: Any, related_companies: list[dict[str, Any]], related_sectors: list[str]) -> dict[str, Any]:
    """Return Low, Medium, or High importance with visible reasons."""
    score = 20
    reasons: list[str] = []

    if category in {"Regulatory", "Macro Economy", "Exchange", "Currency"}:
        score += 35
        reasons.append(f"{category} events can affect multiple companies or investor assumptions.")
    elif category in {"Earnings", "Dividend", "Acquisition", "Litigation"}:
        score += 25
        reasons.append(f"{category} events can materially change how users research a company.")
    else:
        score += 10
        reasons.append(f"{category} events provide useful context but may be narrower in scope.")

    if len(related_companies) >= 2:
        score += 20
        reasons.append("Multiple listed companies are connected to the article.")
    elif len(related_companies) == 1:
        score += 10
        reasons.append("One listed company is directly connected to the article.")

    if len(related_sectors) >= 2:
        score += 10
        reasons.append("More than one sector is connected to the event.")

    if _source_quality(article)["tier"] == "Tier 1 - Official":
        score += 10
        reasons.append("The source is treated as an official source.")

    if score >= 70:
        label = "High"
    elif score >= 40:
        label = "Medium"
    else:
        label = "Low"

    return {"label": label, "score": min(score, 100), "reasons": unique_ordered(reasons)}


def build_evidence(article: Any, related_companies: list[dict[str, Any]]) -> dict[str, Any]:
    """Build source quality, completeness, confidence, and evidence reasons."""
    source_quality = _source_quality(article)
    completeness_score, data_used, missing_data = _data_completeness(article, related_companies)
    score = round((source_quality["score"] * 0.55) + (completeness_score * 0.45))

    if score >= 75:
        confidence = "High"
    elif score >= 45:
        confidence = "Medium"
    else:
        confidence = "Low"

    why = [
        f"Source quality is {source_quality['label'].lower()} because {source_quality['reason']}",
        f"Data completeness is {completeness_score}% based on available article fields and linked entities.",
    ]
    if confidence == "Low":
        why.append("Confidence is low because limited structured information is available.")

    return {
        "source_quality": source_quality,
        "data_completeness": completeness_score,
        "confidence": confidence,
        "why_confidence": why,
        "data_used": data_used,
        "missing_data": missing_data,
    }


def find_related_companies(article: Any, companies: Iterable[Any], text: str | None = None) -> list[dict[str, Any]]:
    """Surface companies explicitly linked or mentioned in article text."""
    text = (text or _article_text(article)).lower()
    related: dict[str, dict[str, Any]] = {}

    for company in getattr(article, "companies", []) or []:
        _add_company_relation(related, company, "Directly linked to this news article.")

    for asset in getattr(article, "assets", []) or []:
        company = getattr(asset, "company", None)
        if company is not None:
            _add_company_relation(related, company, f"Related through linked asset {normalized_value(asset, 'ticker').upper()}.")
        else:
            related[normalized_value(asset, "ticker").upper()] = {
                "ticker": normalized_value(asset, "ticker").upper(),
                "name": normalized_value(asset, "company_name") or normalized_value(asset, "ticker").upper(),
                "sector": normalized_value(asset, "sector") or "Unavailable",
                "reason": f"Related because the article is linked to asset {normalized_value(asset, 'ticker').upper()}.",
            }

    for ticker in asset_value(article, "asset_tickers", []) or []:
        ticker_text = str(ticker).upper()
        related.setdefault(
            ticker_text,
            {
                "ticker": ticker_text,
                "name": ticker_text,
                "sector": "Unavailable",
                "reason": "Related because the ticker is attached to this news article.",
            },
        )

    for company in companies:
        ticker = normalized_value(company, "ticker").upper()
        name = normalized_value(company, "name") or normalized_value(company, "company_name")
        sector = normalized_value(company, "sector")
        if not ticker or ticker in related:
            continue
        if ticker.lower() in text or (name and name.lower() in text):
            _add_company_relation(related, company, "Related because the company name or ticker appears in the article.")
        elif sector and sector.lower() in text:
            _add_company_relation(related, company, f"Related because the article mentions the {sector} sector.")

    return list(related.values())[:6]


def _add_company_relation(target: dict[str, dict[str, Any]], company: Any, reason: str) -> None:
    ticker = normalized_value(company, "ticker").upper()
    if not ticker:
        return
    target[ticker] = {
        "ticker": ticker,
        "name": normalized_value(company, "name") or normalized_value(company, "company_name") or ticker,
        "sector": normalized_value(company, "sector") or "Unavailable",
        "reason": reason,
    }


def _source_quality(article: Any) -> dict[str, Any]:
    source = normalized_value(article, "source").lower()
    if any(item in source for item in _OFFICIAL_SOURCES):
        return {"tier": "Tier 1 - Official", "label": "High", "score": 90, "reason": "official exchange, central bank, or statistics sources are prioritized."}
    if any(item in source for item in _INSTITUTIONAL_SOURCES):
        return {"tier": "Tier 2 - Institutional Research", "label": "High", "score": 78, "reason": "institutional research sources usually provide structured market context."}
    if any(item in source for item in _JOURNALISM_SOURCES):
        return {"tier": "Tier 3 - Financial Journalism", "label": "Medium", "score": 62, "reason": "financial journalism is useful but should be cross-checked with primary sources."}
    return {"tier": "Tier 4 - General or Unknown", "label": "Low", "score": 42, "reason": "the source is not yet mapped to a trusted InvestGuide source tier."}


def _data_completeness(article: Any, related_companies: list[dict[str, Any]]) -> tuple[int, list[str], list[str]]:
    checks = {
        "title": bool(normalized_value(article, "title")),
        "summary": bool(normalized_value(article, "summary")),
        "content": bool(normalized_value(article, "content")),
        "source": bool(normalized_value(article, "source")),
        "published_at": bool(asset_value(article, "published_at")),
        "url": bool(normalized_value(article, "url")),
        "related companies": bool(related_companies),
    }
    data_used = [label for label, present in checks.items() if present]
    missing = [label for label, present in checks.items() if not present]
    return round((len(data_used) / len(checks)) * 100), data_used, missing


def _related_sectors(article: Any, related_companies: list[dict[str, Any]]) -> list[str]:
    sectors = [company["sector"] for company in related_companies if company.get("sector") and company["sector"] != "Unavailable"]
    for asset in getattr(article, "assets", []) or []:
        sectors.append(normalized_value(asset, "sector"))
    return unique_ordered(sectors)


def _related_asset_types(article: Any) -> list[str]:
    asset_types = [normalized_value(asset, "asset_type") for asset in getattr(article, "assets", []) or []]
    return unique_ordered(asset_types)


def _education_for(category: str) -> dict[str, Any]:
    return _CATEGORY_EDUCATION.get(category, _DEFAULT_EDUCATION)


def _news_knowledge_graph(article: Any, category: str, sectors: list[str], asset_types: list[str]) -> dict[str, Any]:
    subject = SimpleNamespace(
        ticker=f"NEWS-{asset_value(article, 'id', '0')}",
        name=normalized_value(article, "title") or category,
        company_name=normalized_value(article, "title") or category,
        sector=sectors[0] if sectors else category,
        asset_type=asset_types[0] if asset_types else "news_event",
        exchange=_exchange_from_article(article),
    )
    graph = build_knowledge_graph(subject)
    graph["nodes"] = unique_ordered([category, *graph["nodes"]])
    graph["edges"] = [{"from": normalized_value(article, "title") or "Article", "to": category, "reason": f"This article is classified as {category}."}, *graph["edges"]]
    return graph


def _merge_learning(topics: list[str], graph_topics: list[dict[str, Any]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    for topic in topics:
        key = topic.lower()
        if key not in seen:
            seen.add(key)
            merged.append(
                {
                    "topic": topic,
                    "why_it_matters": f"Learning about {topic.lower()} helps users interpret this type of news.",
                    "path": f"/education?topic={topic.lower().replace(' ', '-')}",
                }
            )
    for item in graph_topics:
        key = str(item.get("topic", "")).lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(item)
    return merged[:6]


def _exchange_from_article(article: Any) -> str:
    source = normalized_value(article, "source").lower()
    text = _article_text(article).lower()
    if "vfex" in source or "vfex" in text:
        return "VFEX"
    if "zse" in source or "zse" in text:
        return "ZSE"
    return ""


def _article_text(article: Any) -> str:
    return " ".join(
        str(value)
        for value in [
            asset_value(article, "title"),
            asset_value(article, "summary"),
            asset_value(article, "content"),
            asset_value(article, "source"),
        ]
        if value
    )


def _cache_key(article: Any, companies: list[Any]) -> str:
    company_part = ",".join(sorted(normalized_value(company, "ticker").upper() for company in companies if normalized_value(company, "ticker")))
    return "|".join(
        [
            str(asset_value(article, "id", "")),
            normalized_value(article, "content_hash"),
            normalized_value(article, "title"),
            str(asset_value(article, "updated_at", "")),
            company_part,
        ]
    )




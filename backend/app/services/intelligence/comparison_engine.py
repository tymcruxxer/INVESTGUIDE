"""Deterministic cross-asset and cross-company comparison engine."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.services.intelligence.evidence_engine import EvidenceEngine
from app.services.intelligence.knowledge_graph import build_knowledge_graph
from app.services.intelligence.opportunity_engine import OpportunityEngine
from app.services.intelligence.risk_engine import RiskEngine
from app.services.intelligence.utils import normalized_value, unique_ordered

COMPARISON_ENGINE_VERSION = "1"


def build_comparison(left: Any, right: Any, subject_type: str) -> dict[str, Any]:
    """Compare two companies or two assets using deterministic structured logic."""
    left_subject = _subject(left)
    right_subject = _subject(right)
    cache_key = _cache_key(left_subject, right_subject, subject_type)
    return dict(_compare_cached(cache_key, tuple(sorted(left_subject.items())), tuple(sorted(right_subject.items())), subject_type))


def clear_comparison_cache() -> None:
    """Clear deterministic comparison cache."""
    _compare_cached.cache_clear()


@lru_cache(maxsize=256)
def _compare_cached(
    _cache_key_value: str,
    left_items: tuple[tuple[str, str], ...],
    right_items: tuple[tuple[str, str], ...],
    subject_type: str,
) -> tuple[tuple[str, Any], ...]:
    left = dict(left_items)
    right = dict(right_items)
    left_opp = OpportunityEngine().assess(left)
    right_opp = OpportunityEngine().assess(right)
    left_risk = RiskEngine().assess(left)
    right_risk = RiskEngine().assess(right)
    left_evidence = EvidenceEngine().assess(left)
    right_evidence = EvidenceEngine().assess(right)

    payload = {
        "version": COMPARISON_ENGINE_VERSION,
        "subject_type": subject_type,
        "left": _summary(left, left_opp, left_risk, left_evidence),
        "right": _summary(right, right_opp, right_risk, right_evidence),
        "summary": _comparison_summary(left, right),
        "business_comparison": _business_comparison(left, right),
        "opportunity_comparison": _opportunity_comparison(left, right, left_opp, right_opp),
        "risk_comparison": _risk_comparison(left_risk, right_risk),
        "evidence_comparison": _evidence_comparison(left_evidence, right_evidence),
        "educational_comparison": _educational_comparison(left, right),
        "suggested_follow_up_questions": _follow_up_questions(left, right),
        "knowledge_paths": {
            "left": build_knowledge_graph(left)["learn_next"][:4],
            "right": build_knowledge_graph(right)["learn_next"][:4],
        },
        "transparency": {
            "methodology": "Deterministic comparison of structured company, asset, sector, exchange, risk, opportunity, and evidence fields.",
            "not_recommendation": "This comparison is educational and does not predict returns or tell users what to buy or sell.",
        },
    }
    return tuple(payload.items())


def _subject(item: Any) -> dict[str, str]:
    assets = getattr(item, "assets", []) or []
    primary_asset = assets[0] if assets else None
    return {
        "ticker": normalized_value(item, "ticker").upper(),
        "name": normalized_value(item, "name") or normalized_value(item, "company_name"),
        "company_name": normalized_value(item, "company_name") or normalized_value(item, "name"),
        "exchange": normalized_value(item, "exchange") or normalized_value(primary_asset, "exchange"),
        "sector": normalized_value(item, "sector") or normalized_value(primary_asset, "sector"),
        "industry": normalized_value(item, "industry") or normalized_value(primary_asset, "industry"),
        "asset_type": normalized_value(item, "asset_type") or normalized_value(primary_asset, "asset_type") or "company",
        "currency": normalized_value(item, "currency") or normalized_value(primary_asset, "currency"),
        "description": normalized_value(item, "description") or normalized_value(primary_asset, "description"),
        "market_cap": normalized_value(item, "market_cap") or normalized_value(primary_asset, "market_cap"),
        "listing_date": normalized_value(item, "listing_date") or normalized_value(primary_asset, "listing_date"),
        "updated_at": normalized_value(item, "updated_at") or normalized_value(primary_asset, "updated_at"),
    }


def _summary(subject: dict[str, str], opportunity: dict[str, Any], risk: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": subject["ticker"],
        "name": subject["name"],
        "sector": subject["sector"] or "Unavailable",
        "industry": subject["industry"] or "Unavailable",
        "exchange": subject["exchange"] or "Unavailable",
        "asset_type": subject["asset_type"] or "Unavailable",
        "opportunity_label": opportunity["label"],
        "risk_level": risk["risk_level"],
        "evidence_strength": evidence["strength"],
    }


def _comparison_summary(left: dict[str, str], right: dict[str, str]) -> str:
    if left.get("sector") == right.get("sector"):
        return f"{left['name']} and {right['name']} operate in the same broad sector, so the useful comparison is their business model, evidence quality, and risk drivers."
    return f"{left['name']} and {right['name']} operate in different sectors, so the comparison helps separate business exposure, risk drivers, and learning paths."


def _business_comparison(left: dict[str, str], right: dict[str, str]) -> dict[str, Any]:
    rows = []
    for label, field in [
        ("Industry", "industry"),
        ("Sector", "sector"),
        ("Primary business", "description"),
        ("Exchange", "exchange"),
        ("Market structure", "asset_type"),
    ]:
        rows.append({
            "label": label,
            "left": left.get(field) or "Unavailable",
            "right": right.get(field) or "Unavailable",
            "insight": _difference_insight(label, left.get(field), right.get(field)),
        })
    return {"summary": "Business comparison focuses on what each entity does and where it is listed.", "rows": rows}


def _opportunity_comparison(left: dict[str, str], right: dict[str, str], left_opp: dict[str, Any], right_opp: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": "Opportunity is framed as research context, not a return forecast.",
        "left": {"label": left_opp["label"], "score": left_opp["score"], "reasons": left_opp["reasons"][:3]},
        "right": {"label": right_opp["label"], "score": right_opp["score"], "reasons": right_opp["reasons"][:3]},
        "differences": unique_ordered([
            f"{left['name']} is connected to {left.get('sector') or 'its sector'} exposure.",
            f"{right['name']} is connected to {right.get('sector') or 'its sector'} exposure.",
            "Income, growth, maturity, and sector outlook should be evaluated with evidence rather than assumptions.",
        ]),
    }


def _risk_comparison(left_risk: dict[str, Any], right_risk: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": "Risk comparison highlights drivers to investigate before making any decision.",
        "left": {"risk_level": left_risk["risk_level"], "score": left_risk["risk_score"], "drivers": left_risk["reasons"][:3]},
        "right": {"risk_level": right_risk["risk_level"], "score": right_risk["risk_score"], "drivers": right_risk["reasons"][:3]},
        "things_to_watch": unique_ordered(left_risk["things_to_watch"][:3] + right_risk["things_to_watch"][:3]),
    }


def _evidence_comparison(left_evidence: dict[str, Any], right_evidence: dict[str, Any]) -> dict[str, Any]:
    left_score = int(left_evidence["score"])
    right_score = int(right_evidence["score"])
    stronger = "left" if left_score > right_score else "right" if right_score > left_score else "similar"
    return {
        "summary": "Evidence strength indicates how much structured information is available to support the comparison.",
        "stronger_evidence": stronger,
        "left": {"strength": left_evidence["strength"], "score": left_score, "data_used": left_evidence["data_used"]},
        "right": {"strength": right_evidence["strength"], "score": right_score, "data_used": right_evidence["data_used"]},
        "why": _evidence_why(stronger),
    }


def _educational_comparison(left: dict[str, str], right: dict[str, str]) -> dict[str, Any]:
    return {
        "summary": f"Compare {left['name']} and {right['name']} by asking what each business depends on to earn money, what can interrupt those earnings, and how much evidence is available.",
        "plain_english": [
            "Same-sector comparisons usually teach business quality and execution differences.",
            "Different-sector comparisons teach diversification and exposure differences.",
            "Evidence quality matters because limited data should lower confidence.",
        ],
    }


def _follow_up_questions(left: dict[str, str], right: dict[str, str]) -> list[str]:
    return unique_ordered([
        f"Compare {left['name']} with another {left.get('sector') or 'sector'} company",
        f"Compare {right['name']} with another {right.get('sector') or 'sector'} company",
        f"Learn about {left.get('sector') or 'sector exposure'}",
        "Explain diversification",
        "Show recent news",
    ])[:5]


def _difference_insight(label: str, left: str | None, right: str | None) -> str:
    if (left or "").strip().lower() == (right or "").strip().lower():
        return f"Both share the same {label.lower()}, so compare details beyond the label."
    return f"Different {label.lower()} values mean the risk and learning context may differ."


def _evidence_why(stronger: str) -> str:
    if stronger == "similar":
        return "Both sides have similar structured evidence coverage in the current database."
    if stronger == "left":
        return "The left side currently has more structured data points available to the deterministic engine."
    return "The right side currently has more structured data points available to the deterministic engine."


def _cache_key(left: dict[str, str], right: dict[str, str], subject_type: str) -> str:
    return "|".join([subject_type, left.get("ticker", ""), right.get("ticker", ""), left.get("updated_at", ""), right.get("updated_at", "")])

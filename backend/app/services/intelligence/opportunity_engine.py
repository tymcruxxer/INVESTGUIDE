"""Deterministic opportunity assessment engine."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.scoring import score_from_factors
from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered


class OpportunityEngine:
    """Translate structured issuer facts into opportunity context."""

    def assess(self, subject: Any) -> dict[str, Any]:
        """Return non-prescriptive opportunity context."""
        sector = normalized_value(subject, "sector").lower()
        asset_type = normalized_value(subject, "asset_type").lower()
        exchange = normalized_value(subject, "exchange").upper()
        currency = normalized_value(subject, "currency").upper()
        description = normalized_value(subject, "description").lower()

        reasons: list[str] = []
        evidence: list[str] = []
        cautions = 0

        if sector in {"consumer staples", "financial services"}:
            reasons.append("Operates in a sector with recurring household or business demand.")
            evidence.append(f"Sector: {asset_value(subject, 'sector')}")
        if asset_type == "reit":
            reasons.append("REIT structure can support income-focused research once distribution data is available.")
            evidence.append("Asset type: REIT")
        if currency == "usd" or exchange == "vfex":
            reasons.append("Foreign-currency exposure may improve comparability for regional investors.")
            evidence.append(f"Currency/exchange: {asset_value(subject, 'currency')} / {asset_value(subject, 'exchange')}")
        if description and any(term in description for term in ["leading", "largest", "established", "listed"]):
            reasons.append("Company description indicates an established listed business.")
            evidence.append("Structured company description")
        if not asset_value(subject, "market_cap"):
            cautions += 1
        if not asset_value(subject, "listing_date"):
            cautions += 1

        if not reasons:
            reasons.append("Structured data is available, but not enough to identify a clear opportunity pattern yet.")

        score = score_from_factors(52, len(reasons), cautions)
        label = self._label(score)
        return {
            "label": label,
            "score": score,
            "summary": (
                f"{label}. This is a structured research view based on company and asset facts, "
                "not a prediction or recommendation."
            ),
            "reasons": unique_ordered(reasons),
            "supporting_evidence": unique_ordered(evidence) or ["Basic issuer and market metadata"],
        }

    @staticmethod
    def _label(score: int) -> str:
        if score >= 72:
            return "Compelling Research Candidate"
        if score >= 58:
            return "Interesting Research Candidate"
        if score >= 44:
            return "Watchlist Research Candidate"
        return "Early Research Candidate"

"""Deterministic strength extraction for asset intelligence assessments."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered


class InvestmentAssessmentEngine:
    """Generate non-advisory opportunity assessment and key strengths."""

    def overall_assessment(self, asset: Any, *, evidence_strength: str, watch_count: int) -> str:
        """Return an assessment label without buy/sell language."""
        asset_type = normalized_value(asset, "asset_type").lower()
        sector = normalized_value(asset, "sector").lower()
        exchange = normalized_value(asset, "exchange").upper()

        if evidence_strength == "Low":
            return "Neutral"
        if watch_count >= 6 and evidence_strength in {"Medium", "High"}:
            return "Cautious"
        if asset_type in {"bond", "money_market"}:
            return "Moderately Attractive" if evidence_strength in {"Medium", "High", "Very High"} else "Neutral"
        if asset_type == "reit":
            return "Moderately Attractive" if evidence_strength == "Medium" else "Attractive"
        if exchange == "VFEX" or "mining" in sector or "basic" in sector:
            return "Neutral" if evidence_strength == "Medium" else "Moderately Attractive"
        if "consumer" in sector or "telecommunications" in sector:
            return "Moderately Attractive" if evidence_strength == "Medium" else "Attractive"
        return "Moderately Attractive" if evidence_strength in {"High", "Very High"} else "Neutral"

    def investment_horizon(self, asset: Any) -> str:
        """Return deterministic horizon suitability."""
        asset_type = normalized_value(asset, "asset_type").lower()
        sector = normalized_value(asset, "sector").lower()
        exchange = normalized_value(asset, "exchange").upper()

        if asset_type in {"bond", "money_market"}:
            return "Short-term"
        if asset_type == "reit":
            return "Income-focused"
        if exchange == "VFEX" or "mining" in sector or "basic" in sector:
            return "Growth-focused"
        return "Long-term"

    def key_strengths(self, asset: Any) -> list[str]:
        """Generate key strengths from structured asset fields only."""
        asset_type = normalized_value(asset, "asset_type").lower()
        sector = normalized_value(asset, "sector").lower()
        industry = normalized_value(asset, "industry").lower()
        currency = normalized_value(asset, "currency").upper()
        exchange = normalized_value(asset, "exchange").upper()
        strengths: list[str] = []

        if asset_type == "reit":
            strengths.append("Income-producing property exposure")
        elif asset_type in {"bond", "money_market"}:
            strengths.append("Capital preservation profile")
        elif asset_type == "equity":
            strengths.append("Listed equity exposure with public market visibility")

        if "consumer" in sector or "beverage" in industry or "food" in industry:
            strengths.append("Defensive consumer demand theme")
        if "telecommunications" in sector or "telecommunications" in industry:
            strengths.append("Essential communications sector exposure")
        if "real estate" in sector or "reit" in industry:
            strengths.append("Property-backed income theme")
        if "mining" in sector or "basic" in sector or "gold" in industry:
            strengths.append("Commodity and foreign-currency earnings exposure")
        if "financial" in sector or "bank" in industry:
            strengths.append("Financial sector participation")
        if "government" in sector:
            strengths.append("Government-backed instrument profile")
        if currency == "USD" or exchange == "VFEX":
            strengths.append("Foreign-currency market exposure")
        if asset_value(asset, "market_cap") is not None:
            strengths.append("Market capitalization data is available for sizing context")
        if normalized_value(asset, "description"):
            strengths.append("Public company profile is available")

        if not strengths:
            strengths.append("Basic asset profile is available for initial research")

        return unique_ordered(strengths)[:5]
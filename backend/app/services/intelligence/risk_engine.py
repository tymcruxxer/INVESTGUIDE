"""Risk and monitoring engine for deterministic asset assessments."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.scoring import clamp_score
from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered


class RiskEngine:
    """Generate non-predictive risk context from structured asset data."""

    def things_to_watch(self, asset: Any) -> list[str]:
        """Return monitoring factors for an asset."""
        asset_type = normalized_value(asset, "asset_type").lower()
        sector = normalized_value(asset, "sector").lower()
        industry = normalized_value(asset, "industry").lower()
        exchange = normalized_value(asset, "exchange").upper()
        currency = normalized_value(asset, "currency").upper()
        watches = ["Liquidity", "Inflation", "Currency policy"]

        if asset_type == "reit" or "real estate" in sector:
            watches.extend(["Interest rates", "Property occupancy", "Distribution updates"])
        elif asset_type in {"bond", "money_market"}:
            watches.extend(["Interest rates", "Issuer repayment risk", "Reinvestment risk"])
        elif asset_type == "equity":
            watches.extend(["Earnings updates", "Low trading volume"])

        if exchange == "VFEX" or currency == "USD":
            watches.append("Foreign-currency rules")
        if "mining" in sector or "basic" in sector or "gold" in industry:
            watches.extend(["Commodity prices", "Production updates"])
        if "financial" in sector or "bank" in industry:
            watches.extend(["Credit conditions", "Regulatory changes"])
        if "telecommunications" in sector:
            watches.extend(["Regulatory changes", "Infrastructure costs"])
        if "consumer" in sector:
            watches.extend(["Consumer demand", "Input costs"])
        if not sector:
            watches.append("Limited sector information")

        return unique_ordered(watches)[:7]

    def assess(self, asset: Any) -> dict[str, Any]:
        """Return a structured, non-predictive risk assessment."""
        watches = self.things_to_watch(asset)
        asset_type = normalized_value(asset, "asset_type").lower()
        sector = normalized_value(asset, "sector").lower()
        exchange = normalized_value(asset, "exchange").upper()
        has_market_cap = asset_value(asset, "market_cap") not in (None, "", [])
        has_listing_date = asset_value(asset, "listing_date") not in (None, "", [])

        score = 42
        reasons = ["Zimbabwe market conditions can affect liquidity, inflation exposure, and currency assumptions."]
        evidence = ["Risk factors generated from structured asset metadata."]

        if asset_type in {"bond", "money_market"}:
            score -= 8
            reasons.append("Fixed-income style instruments usually depend more on issuer and interest-rate risk than business-growth risk.")
            evidence.append(f"Asset type: {asset_value(asset, 'asset_type')}")
        if asset_type == "reit":
            score += 8
            reasons.append("REITs require monitoring of interest rates, occupancy, and distribution sustainability.")
            evidence.append("Asset type: REIT")
        if "mining" in sector:
            score += 12
            reasons.append("Mining exposure can be sensitive to commodity prices and production updates.")
            evidence.append(f"Sector: {asset_value(asset, 'sector')}")
        if exchange == "VFEX":
            score += 5
            reasons.append("VFEX and foreign-currency exposure can add policy and convertibility considerations.")
            evidence.append("Exchange: VFEX")
        if not has_market_cap:
            score += 7
            reasons.append("Market-cap data is missing, reducing the ability to size the issuer.")
        if not has_listing_date:
            score += 5
            reasons.append("Listing history is missing, limiting context about public-market track record.")

        score = clamp_score(score)
        risk_level = self._risk_level(score)
        return {
            "overall_risk": risk_level,
            "risk_level": risk_level,
            "risk_score": score,
            "summary": f"{risk_level} risk based on structured metadata and known market monitoring factors.",
            "reasons": unique_ordered(reasons),
            "things_to_watch": watches,
            "supporting_evidence": unique_ordered(evidence),
        }

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 72:
            return "High"
        if score >= 58:
            return "Elevated"
        if score >= 38:
            return "Moderate"
        return "Low"
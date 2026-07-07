"""Risk and monitoring engine for deterministic asset assessments."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.utils import normalized_value, unique_ordered


class RiskEngine:
    """Generate non-predictive things-to-watch from structured asset data."""

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
"""Evidence-strength engine for deterministic asset assessments."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.utils import asset_value


class StrengthEngine:
    """Assess how much structured data is available for an asset."""

    REQUIRED_FIELDS = (
        "ticker",
        "company_name",
        "exchange",
        "sector",
        "industry",
        "asset_type",
        "currency",
        "description",
        "market_cap",
        "listing_date",
    )

    def calculate_evidence_strength(self, asset: Any) -> str:
        """Return Low, Medium, High, or Very High based on data completeness."""
        populated = sum(1 for field in self.REQUIRED_FIELDS if asset_value(asset, field) not in (None, ""))
        if populated <= 4:
            return "Low"
        if populated <= 7:
            return "Medium"
        if populated <= 9:
            return "High"
        return "Very High"

    def reason(self, evidence_strength: str) -> str:
        """Explain why the evidence strength was assigned."""
        if evidence_strength == "Low":
            return "Limited publicly available financial information is currently available."
        if evidence_strength == "Medium":
            return "Core profile information is available, but deeper financial history is still missing."
        if evidence_strength == "High":
            return "Most core profile fields are available, but some historical data is still missing."
        return "The asset profile has broad structured coverage for this stage of the platform."
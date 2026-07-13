"""Evidence-strength engine for research transparency."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.models import EVIDENCE_LABELS
from app.services.intelligence.scoring import confidence_label
from app.services.intelligence.strength_engine import StrengthEngine
from app.services.intelligence.utils import asset_value, unique_ordered


class EvidenceEngine:
    """Measure how much structured evidence supports the research output."""

    REQUIRED_FIELDS = {
        "company_name": "company name",
        "ticker": "ticker",
        "exchange": "exchange",
        "sector": "sector",
        "industry": "industry",
        "asset_type": "asset type",
        "currency": "currency",
        "description": "description",
        "market_cap": "market cap",
        "listing_date": "listing date",
    }

    def assess(self, subject: Any) -> dict[str, Any]:
        """Return evidence strength and missing inputs."""
        base_strength = StrengthEngine().calculate_evidence_strength(subject)
        data_used = [
            label for field, label in self.REQUIRED_FIELDS.items() if asset_value(subject, field) not in (None, "", [])
        ]
        missing = [
            label for field, label in self.REQUIRED_FIELDS.items() if asset_value(subject, field) in (None, "", [])
        ]
        score = max(20, min(95, 20 + len(data_used) * 8 - len(missing) * 2))
        mapped_strength = EVIDENCE_LABELS.get(base_strength, confidence_label(score))
        if len(data_used) <= 3:
            mapped_strength = "Experimental"

        return {
            "strength": mapped_strength,
            "score": score,
            "summary": f"Evidence strength is {mapped_strength.lower()} because {len(data_used)} structured fields were available.",
            "reasons": [
                f"Existing assessment evidence level: {base_strength}",
                f"Structured fields used: {len(data_used)}",
                f"Missing fields: {len(missing)}",
            ],
            "data_used": unique_ordered(data_used),
            "missing_data": unique_ordered(missing),
        }

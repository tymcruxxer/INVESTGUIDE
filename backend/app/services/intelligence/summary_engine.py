"""Overall research summary engine."""

from __future__ import annotations

from typing import Any


class SummaryEngine:
    """Combine deterministic research sections into a concise overview."""

    def summarize(
        self,
        opportunity: dict[str, Any],
        risk: dict[str, Any],
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """Return the overall research assessment."""
        label = self._label(opportunity["score"], risk["risk_score"], evidence["score"])
        return {
            "label": label,
            "summary": (
                f"{label}. Opportunity score is {opportunity['score']}/100, "
                f"risk score is {risk['risk_score']}/100, and evidence strength is {evidence['strength']}."
            ),
            "reasons": [
                opportunity["summary"],
                risk["summary"],
                evidence["summary"],
            ],
        }

    @staticmethod
    def _label(opportunity_score: int, risk_score: int, evidence_score: int) -> str:
        if evidence_score < 40:
            return "Research View: Evidence Limited"
        if risk_score >= 72:
            return "Research View: Higher Risk"
        if opportunity_score >= 68 and risk_score < 65:
            return "Research View: Constructive"
        if opportunity_score >= 50:
            return "Research View: Balanced"
        return "Research View: Monitor"

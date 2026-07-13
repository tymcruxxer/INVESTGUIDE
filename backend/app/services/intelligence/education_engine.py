"""Educational explanation engine for deterministic research."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.utils import asset_value, normalized_value


class EducationEngine:
    """Create beginner-safe explanations from structured facts."""

    def explain(self, subject: Any, opportunity_label: str, risk_level: str) -> dict[str, Any]:
        """Return educational context without making predictions."""
        name = asset_value(subject, "company_name") or asset_value(subject, "name") or asset_value(subject, "ticker")
        sector = asset_value(subject, "sector") or "its sector"
        asset_type = asset_value(subject, "asset_type") or "listed investment"
        return {
            "summary": (
                f"{name} is being reviewed as a {asset_type} in {sector}. "
                f"The current research view is '{opportunity_label}' with {risk_level.lower()} risk."
            ),
            "key_concepts": self._concepts(subject),
            "why_it_matters": (
                "This matters because investors should understand the business, the available evidence, "
                "and the main risks before comparing it with other options."
            ),
        }

    def explain_like_im_18(self, subject: Any, risk_level: str) -> dict[str, str]:
        """Return a simple explanation suitable for beginner investors."""
        name = asset_value(subject, "company_name") or asset_value(subject, "name") or asset_value(subject, "ticker")
        sector = asset_value(subject, "sector") or "business area"
        return {
            "summary": (
                f"Think of {name} as a business you can study before deciding whether it belongs in your plan. "
                f"It operates in {sector}, so its performance depends on how that part of the economy is doing."
            ),
            "example": (
                f"A {risk_level.lower()} risk label means you should check what could go wrong, "
                "not that the investment is good or bad."
            ),
        }

    @staticmethod
    def _concepts(subject: Any) -> list[str]:
        concepts = ["business model", "risk", "evidence quality"]
        asset_type = normalized_value(subject, "asset_type").lower()
        if asset_type == "reit":
            concepts.append("income distributions")
        if normalized_value(subject, "currency").upper() == "USD":
            concepts.append("currency exposure")
        return concepts

"""Suggested research-question engine."""

from __future__ import annotations

from typing import Any

from app.services.intelligence.utils import asset_value, normalized_value, unique_ordered


class QuestionEngine:
    """Generate deterministic next research questions."""

    def suggest(self, subject: Any) -> list[str]:
        """Return beginner-safe questions for further research."""
        name = asset_value(subject, "company_name") or asset_value(subject, "name") or asset_value(subject, "ticker")
        sector = asset_value(subject, "sector") or "this sector"
        questions = [
            f"What does {name} do to earn revenue?",
            f"What risks affect companies in {sector}?",
            "How much evidence is available compared with similar investments?",
            "What would change the research view in future updates?",
        ]
        if normalized_value(subject, "asset_type").lower() == "reit":
            questions.append("How reliable are the future distribution payments?")
        if normalized_value(subject, "currency").upper() == "USD":
            questions.append("How does foreign-currency exposure affect this investment?")
        return unique_ordered(questions)

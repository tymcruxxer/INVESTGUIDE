"""Quality score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class QualityScoreAnalytics(BaseAnalytics):
    """Purpose-only quality score module."""

    metric_name = "quality_score"
    purpose = "Assess future business quality, resilience, and governance signals."
    required_inputs = ("asset",)
    optional_inputs = ("financial_statements", "news")
    methodology = "Future methodology will evaluate earnings quality, balance sheet strength, governance, consistency, and sector resilience."
    future_notes = "Requires financial statements, corporate actions, and trusted company research before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
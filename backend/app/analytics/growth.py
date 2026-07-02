"""Growth score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class GrowthScoreAnalytics(BaseAnalytics):
    """Purpose-only growth score module."""

    metric_name = "growth_score"
    purpose = "Assess future growth signals for assets and sectors."
    required_inputs = ("asset",)
    optional_inputs = ("financial_statements", "historical_prices", "macro_data", "news")
    methodology = "Future methodology will evaluate revenue trends, earnings trends, reinvestment, sector momentum, and macro tailwinds."
    future_notes = "Requires normalized statement history and market data before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
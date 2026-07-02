"""Valuation score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class ValueScoreAnalytics(BaseAnalytics):
    """Purpose-only valuation score module."""

    metric_name = "value_score"
    purpose = "Assess future relative valuation context without issuing buy/sell advice."
    required_inputs = ("asset",)
    optional_inputs = ("financial_statements", "historical_prices", "macro_data")
    methodology = "Future methodology will evaluate valuation ratios, asset value, earnings, dividend context, peer comparison, and macro adjustments."
    future_notes = "Requires market prices, statement data, and peer groups before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
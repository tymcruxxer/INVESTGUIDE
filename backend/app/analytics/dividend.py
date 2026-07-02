"""Dividend score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class DividendScoreAnalytics(BaseAnalytics):
    """Purpose-only dividend score module."""

    metric_name = "dividend_score"
    purpose = "Assess future dividend or REIT distribution reliability."
    required_inputs = ("asset",)
    optional_inputs = ("financial_statements", "historical_prices", "macro_data")
    methodology = "Future methodology will evaluate dividend history, payout stability, yield context, cash flow coverage, and REIT distribution quality."
    future_notes = "Requires dividend/distribution history and sector benchmarks before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
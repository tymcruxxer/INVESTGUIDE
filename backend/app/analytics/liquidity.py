"""Liquidity score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class LiquidityScoreAnalytics(BaseAnalytics):
    """Purpose-only liquidity score module."""

    metric_name = "liquidity_score"
    purpose = "Assess future trading liquidity and exit-risk context."
    required_inputs = ("asset",)
    optional_inputs = ("historical_prices", "macro_data")
    methodology = "Future methodology will evaluate turnover, trading frequency, spread proxies, volume consistency, and market depth where available."
    future_notes = "Requires reliable historical trading data before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
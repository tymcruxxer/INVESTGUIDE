"""Risk score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class RiskScoreAnalytics(BaseAnalytics):
    """Purpose-only risk score module."""

    metric_name = "risk_score"
    purpose = "Assess future downside, volatility, liquidity, and macro risk drivers."
    required_inputs = ("asset",)
    optional_inputs = ("historical_prices", "macro_data", "news", "financial_statements")
    methodology = "Future methodology will evaluate volatility, drawdowns, liquidity, concentration, balance sheet risk, currency exposure, and macro sensitivity."
    future_notes = "Requires historical prices, financial statements, and macro series before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
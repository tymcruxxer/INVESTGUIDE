"""Macro score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class MacroScoreAnalytics(BaseAnalytics):
    """Purpose-only macro score module."""

    metric_name = "macro_score"
    purpose = "Assess future macro tailwinds and headwinds for assets and sectors."
    required_inputs = ("asset",)
    optional_inputs = ("macro_data", "news")
    methodology = "Future methodology will evaluate inflation, exchange rates, interest rates, commodity exposure, policy context, and currency denomination."
    future_notes = "Requires trusted RBZ, ZIMSTAT, commodity, and exchange-rate data before real scoring."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
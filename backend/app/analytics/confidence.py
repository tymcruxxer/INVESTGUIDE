"""Confidence score analytics architecture."""

from __future__ import annotations

from app.analytics.base import BaseAnalytics


class ConfidenceScoreAnalytics(BaseAnalytics):
    """Purpose-only confidence score module."""

    metric_name = "confidence_score"
    purpose = "Tell future AI and frontend modules how reliable an analytics result is likely to be."
    required_inputs = ("asset",)
    optional_inputs = ("historical_prices", "news", "macro_data", "financial_statements")
    methodology = "Future methodology will evaluate data completeness, recency, source trust, agreement between inputs, and missing critical records."
    future_notes = "This score should guide AI caveats and frontend confidence labels after real analytics exist."

    def planned_inputs(self) -> tuple[str, ...]:
        return self.required_inputs + self.optional_inputs
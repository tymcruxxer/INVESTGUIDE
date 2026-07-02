"""Abstract base class for all analytics modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.analytics.context import AnalyticsContext
from app.analytics.explanation import AnalyticsExplanation
from app.analytics.result import AnalyticsResult
from app.analytics.version import ENGINE_VERSION, METHODOLOGY_VERSION


@dataclass(slots=True)
class AnalyticsMetadata:
    """Describes an analytics module without performing a calculation."""

    metric_name: str
    purpose: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    methodology: str
    future_notes: str
    version: str
    methodology_version: str


class BaseAnalytics(ABC):
    """Base contract every analytics module must implement."""

    metric_name = "base_metric"
    purpose = "Base analytics contract"
    required_inputs: tuple[str, ...] = ("asset",)
    optional_inputs: tuple[str, ...] = ()
    methodology = "Base analytics methodology contract"
    future_notes = "Subclasses define concrete analytics architecture."
    version = ENGINE_VERSION
    methodology_version = METHODOLOGY_VERSION

    def validate(self, context: AnalyticsContext) -> list[str]:
        """Validate context and return non-fatal warnings.

        Foundation modules are purpose-only in Sprint 026, so missing optional
        future datasets are warnings rather than hard failures.
        """
        warnings: list[str] = []
        missing = context.missing_inputs(self.required_inputs)
        if missing:
            warnings.append(f"Missing required future inputs: {', '.join(missing)}")
        missing_optional = context.missing_inputs(self.optional_inputs)
        if missing_optional:
            warnings.append(f"Missing optional future inputs: {', '.join(missing_optional)}")
        warnings.append("Calculation not implemented in Sprint 026 analytics foundation")
        return warnings

    def calculate(self, context: AnalyticsContext) -> AnalyticsResult:
        """Return a structured purpose-only result for this metric."""
        warnings = self.validate(context)
        return AnalyticsResult(
            metric_name=self.metric_name,
            value=None,
            confidence=0.0,
            methodology=self.methodology,
            inputs_used=tuple(context.available_inputs()),
            warnings=tuple(warnings),
            version=self.version,
        )

    def metadata(self) -> AnalyticsMetadata:
        """Return architecture metadata for registries, docs, and AI context."""
        return AnalyticsMetadata(
            metric_name=self.metric_name,
            purpose=self.purpose,
            required_inputs=self.required_inputs,
            optional_inputs=self.optional_inputs,
            methodology=self.methodology,
            future_notes=self.future_notes,
            version=self.version,
            methodology_version=self.methodology_version,
        )

    def explanation(self, result: AnalyticsResult | None = None) -> AnalyticsExplanation:
        """Return deterministic explanation text for a result or module purpose."""
        missing_inputs = self.required_inputs if result is None else ()
        return AnalyticsExplanation(
            metric_name=self.metric_name,
            summary=self.purpose,
            details=(self.methodology, self.future_notes),
            confidence_label="Not available" if result is None else "Not available",
            missing_inputs=missing_inputs,
        )

    @abstractmethod
    def planned_inputs(self) -> tuple[str, ...]:
        """Return all inputs this metric is expected to use when implemented."""
"""Central Analytics Engine for InvestGuide financial intelligence."""

from __future__ import annotations

from typing import Any

from app.analytics.context import AnalyticsContext
from app.analytics.registry import AnalyticsRegistry
from app.analytics.version import ENGINE_VERSION, METHODOLOGY_VERSION


class AnalyticsEngine:
    """Coordinates analytics execution through a single registry."""

    ENGINE_VERSION = ENGINE_VERSION
    METHODOLOGY_VERSION = METHODOLOGY_VERSION

    def __init__(self, registry: AnalyticsRegistry | None = None, *, auto_register: bool = True) -> None:
        self.registry = registry or AnalyticsRegistry(auto_register=auto_register)

    def calculate(self, metric_name: str, context: AnalyticsContext) -> dict[str, Any]:
        """Calculate one metric and return serialized output."""
        return self.registry.calculate(metric_name, context).to_dict()

    def calculate_all(self, context: AnalyticsContext) -> dict[str, Any]:
        """Run all registered analytics modules and aggregate results."""
        results = self.registry.calculate_all(context)
        serialized = [result.to_dict() for result in results]
        warnings: list[str] = []
        for result in results:
            warnings.extend(str(warning) for warning in result.warnings)
        return {
            "engine_version": self.ENGINE_VERSION,
            "methodology_version": self.METHODOLOGY_VERSION,
            "context": {
                "asset_identifier": context.asset_identifier(),
                "inputs_available": context.available_inputs(),
            },
            "summary": {
                "total": len(results),
                "completed": len(serialized),
                "warnings": len(warnings),
            },
            "results": serialized,
            "warnings": warnings,
        }

    def analyze(self, context: AnalyticsContext) -> dict[str, Any]:
        """Alias for calculate_all for caller readability."""
        return self.calculate_all(context)

    def metadata(self) -> dict[str, Any]:
        """Return engine and registered metric metadata."""
        return {
            "engine_version": self.ENGINE_VERSION,
            "methodology_version": self.METHODOLOGY_VERSION,
            "registered_metrics": self.registry.metric_names,
            "metrics": self.registry.metadata(),
        }
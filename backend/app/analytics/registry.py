"""Analytics registry for centralized metric execution."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict

from app.analytics.base import BaseAnalytics
from app.analytics.context import AnalyticsContext
from app.analytics.exceptions import UnknownMetricError, ValidationError
from app.analytics.result import AnalyticsResult
from app.analytics.scores import DEFAULT_ANALYTICS


class AnalyticsRegistry:
    """Registry of analytics modules available to the engine."""

    def __init__(self, auto_register: bool = False) -> None:
        self._metrics: dict[str, BaseAnalytics] = {}
        if auto_register:
            for metric_class in DEFAULT_ANALYTICS:
                self.register(metric_class.metric_name, metric_class)

    @property
    def metric_names(self) -> tuple[str, ...]:
        """Return registered metric names in registration order."""
        return tuple(self._metrics.keys())

    def register(self, metric_name: str, metric: type[BaseAnalytics] | BaseAnalytics) -> None:
        """Register an analytics module class or instance."""
        if not metric_name:
            raise ValidationError("metric_name is required")
        instance = metric() if isinstance(metric, type) else metric
        if not isinstance(instance, BaseAnalytics):
            raise ValidationError("metric must be a BaseAnalytics instance or subclass")
        self._metrics[metric_name] = instance

    def unregister(self, metric_name: str) -> None:
        """Unregister a metric by name."""
        if metric_name not in self._metrics:
            raise UnknownMetricError(f"Metric '{metric_name}' is not registered")
        del self._metrics[metric_name]

    def get(self, metric_name: str) -> BaseAnalytics:
        """Return a registered metric instance."""
        try:
            return self._metrics[metric_name]
        except KeyError as exc:
            raise UnknownMetricError(f"Metric '{metric_name}' is not registered") from exc

    def calculate(self, metric_name: str, context: AnalyticsContext) -> AnalyticsResult:
        """Calculate one registered metric."""
        return self.get(metric_name).calculate(context)

    def calculate_all(self, context: AnalyticsContext, metrics: Iterable[str] | None = None) -> list[AnalyticsResult]:
        """Calculate all registered metrics or a selected subset."""
        metric_names = tuple(metrics) if metrics is not None else self.metric_names
        return [self.calculate(metric_name, context) for metric_name in metric_names]

    def metadata(self) -> list[dict[str, object]]:
        """Return registry metadata for documentation/API consumers."""
        return [asdict(metric.metadata()) for metric in self._metrics.values()]
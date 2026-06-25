"""Scraper execution metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class ScraperMetrics:
    """Mutable metrics tracked per scraper source."""

    successful_runs: int = 0
    failed_runs: int = 0
    execution_time: float = 0.0
    retry_count: int = 0
    last_run: datetime | None = None
    articles_found: int = 0
    articles_ingested: int = 0

    def record_success(self, execution_time: float, articles_found: int = 0, articles_ingested: int = 0) -> None:
        """Record a successful scraper run."""
        self.successful_runs += 1
        self.execution_time = execution_time
        self.articles_found += articles_found
        self.articles_ingested += articles_ingested
        self.last_run = datetime.now(UTC)

    def record_failure(self, execution_time: float = 0.0) -> None:
        """Record a failed scraper run."""
        self.failed_runs += 1
        self.execution_time = execution_time
        self.last_run = datetime.now(UTC)

    def record_retry(self, count: int = 1) -> None:
        """Record retry attempts."""
        self.retry_count += count


class MetricsCollector:
    """In-memory metrics registry keyed by source id."""

    def __init__(self) -> None:
        self._metrics: dict[str, ScraperMetrics] = {}

    def for_source(self, source_id: str) -> ScraperMetrics:
        """Return metrics for a source, creating them when missing."""
        if source_id not in self._metrics:
            self._metrics[source_id] = ScraperMetrics()
        return self._metrics[source_id]

    def snapshot(self) -> dict[str, ScraperMetrics]:
        """Return a copy of all currently tracked metrics."""
        return dict(self._metrics)
"""Dependency container for scraper infrastructure."""

from __future__ import annotations

from dataclasses import dataclass

from scrapers.core.http_client import HttpClient
from scrapers.core.logger import ScraperLogger
from scrapers.core.metrics import MetricsCollector, ScraperMetrics
from scrapers.core.rate_limiter import RateLimiter
from scrapers.core.retry_policy import RetryPolicy
from scrapers.core.robots import RobotsPolicy
from scrapers.core.source_config import SourceConfig
from scrapers.core.source_registry import SourceDefinition
from scrapers.core.user_agent import UserAgentManager


@dataclass(frozen=True)
class ScraperContext:
    """Shared dependency container passed to scraper instances."""

    source_id: str
    config: SourceConfig
    http_client: HttpClient
    retry_policy: RetryPolicy
    rate_limiter: RateLimiter
    metrics_collector: MetricsCollector
    metrics: ScraperMetrics
    logger: ScraperLogger
    user_agent_manager: UserAgentManager
    robots_policy: RobotsPolicy
    source_definition: SourceDefinition | None = None
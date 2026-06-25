"""Factory for constructing complete scraper contexts."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from scrapers.core.context import ScraperContext
from scrapers.core.http_client import HttpClient, Transport, urllib_transport
from scrapers.core.logger import ScraperLogger
from scrapers.core.metrics import MetricsCollector
from scrapers.core.rate_limiter import RateLimiter
from scrapers.core.retry_policy import RetryPolicy
from scrapers.core.robots import RobotsPolicy
from scrapers.core.source_config import SourceConfig
from scrapers.core.source_registry import SourceDefinition, SourceRegistry, default_source_registry
from scrapers.core.user_agent import UserAgentManager


class ScraperContextFactory:
    """Build fully wired scraper dependency contexts."""

    def __init__(
        self,
        registry: SourceRegistry | None = None,
        env: Mapping[str, str] | None = None,
        transport: Transport | None = None,
        metrics_collector: MetricsCollector | None = None,
        robots_policy: RobotsPolicy | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.registry = registry or default_source_registry()
        self.env = env
        self.transport = transport
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.robots_policy = robots_policy or RobotsPolicy()
        self.logger = logger

    def build(self, source: str | SourceDefinition) -> ScraperContext:
        """Construct a ready-to-use context for a source id, display name, or definition."""
        source_definition = source if isinstance(source, SourceDefinition) else self._resolve_source(source)
        source_id = source_definition.id if source_definition is not None else self._normalize_source_id(str(source))
        config = SourceConfig.from_env(source_id, self.env)
        retry_policy = RetryPolicy(max_retries=config.retry_count, backoff_factor=config.retry_backoff)
        user_agent_manager = UserAgentManager(config.user_agent)
        http_client = HttpClient(
            config=config,
            retry_policy=retry_policy,
            transport=self.transport or urllib_transport,
        )
        rate_limiter = RateLimiter(
            minimum_interval=config.request_interval,
            requests_per_minute=config.rate_limit,
        )
        scraper_logger = ScraperLogger(self.logger or logging.getLogger(f"investguide.scrapers.{source_id}"))
        if source_definition is not None:
            self.robots_policy.register(
                source_id=source_definition.id,
                homepage=source_definition.homepage,
                robots_url=source_definition.robots_url,
            )
        metrics = self.metrics_collector.for_source(source_id)
        return ScraperContext(
            source_id=source_id,
            source_definition=source_definition,
            config=config,
            http_client=http_client,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            metrics_collector=self.metrics_collector,
            metrics=metrics,
            logger=scraper_logger,
            user_agent_manager=user_agent_manager,
            robots_policy=self.robots_policy,
        )

    def _resolve_source(self, value: str) -> SourceDefinition | None:
        return self.registry.get(value) or self.registry.get_by_display_name(value)

    @staticmethod
    def _normalize_source_id(value: str) -> str:
        return "-".join(value.strip().lower().replace("_", "-").split())
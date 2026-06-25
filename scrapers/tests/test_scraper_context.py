"""Scraper context dependency injection tests."""

from __future__ import annotations

from scrapers.core.context import ScraperContext
from scrapers.core.context_factory import ScraperContextFactory
from scrapers.core.http_client import HttpRequest, HttpResponse
from scrapers.core.metrics import MetricsCollector
from scrapers.core.robots import RobotsPolicy
from scrapers.news.financial_gazette import FinancialGazetteScraper
from scrapers.zse.announcements_scraper import ZSEAnnouncementsScraper


def test_context_factory_builds_complete_registered_source_context() -> None:
    """Factory wires all shared infrastructure into a ScraperContext."""
    context = ScraperContextFactory().build("zse")

    assert isinstance(context, ScraperContext)
    assert context.source_id == "zse"
    assert context.source_definition is not None
    assert context.source_definition.display_name == "ZSE"
    assert context.http_client.config is context.config
    assert context.http_client.retry_policy is context.retry_policy
    assert context.metrics_collector.for_source("zse") is context.metrics
    assert context.robots_policy.get("zse") is not None
    assert context.user_agent_manager.get() == context.config.user_agent


def test_context_factory_loads_source_specific_configuration() -> None:
    """Factory passes source-specific environment values into SourceConfig."""
    context = ScraperContextFactory(
        env={
            "SCRAPER_ZSE_TIMEOUT": "4.5",
            "SCRAPER_ZSE_RETRY_COUNT": "5",
            "SCRAPER_ZSE_RETRY_BACKOFF": "1.25",
            "SCRAPER_ZSE_RATE_LIMIT": "12",
            "SCRAPER_ZSE_REQUEST_INTERVAL": "3",
            "SCRAPER_ZSE_USER_AGENT": "ContextTest/1.0",
            "SCRAPER_ZSE_ENABLED": "false",
        }
    ).build("zse")

    assert context.config.timeout == 4.5
    assert context.config.retry_count == 5
    assert context.retry_policy.max_retries == 5
    assert context.retry_policy.backoff_factor == 1.25
    assert context.config.rate_limit == 12
    assert context.config.request_interval == 3
    assert context.config.user_agent == "ContextTest/1.0"
    assert context.config.enabled is False


def test_context_factory_supports_fake_transport_without_network() -> None:
    """Injected transport keeps HTTP behavior offline and attached to the context."""
    requests: list[HttpRequest] = []

    def fake_transport(request: HttpRequest) -> HttpResponse:
        requests.append(request)
        return HttpResponse(status_code=200, text="ok", url=request.url)

    context = ScraperContextFactory(transport=fake_transport).build("Financial Gazette")
    response = context.http_client.get("https://example.test/offline")

    assert response.text == "ok"
    assert requests[0].headers["User-Agent"] == context.config.user_agent
    assert context.source_definition is not None
    assert context.source_definition.id == "financial-gazette"


def test_placeholder_scrapers_accept_explicit_context() -> None:
    """Existing placeholder scrapers receive one context object and keep behavior unchanged."""
    collector = MetricsCollector()
    robots = RobotsPolicy()
    context = ScraperContextFactory(metrics_collector=collector, robots_policy=robots).build("financial-gazette")

    scraper = FinancialGazetteScraper(context=context)
    result = scraper.run()

    assert scraper.context is context
    assert scraper.context.metrics_collector is collector
    assert scraper.context.robots_policy is robots
    assert result.success is True
    assert len(result.articles) == 1
    assert result.articles[0].source == FinancialGazetteScraper.source_name


def test_placeholder_scrapers_still_get_default_context_when_omitted() -> None:
    """Fixture call sites can omit context while BaseScraper creates an offline default."""
    scraper = ZSEAnnouncementsScraper()

    assert isinstance(scraper.context, ScraperContext)
    assert scraper.context.source_id == "zimbabwe-stock-exchange-announcements"
    assert scraper.run().success is True
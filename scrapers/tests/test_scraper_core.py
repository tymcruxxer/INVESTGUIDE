"""Scraper core infrastructure tests."""

from __future__ import annotations

import logging
from urllib.error import URLError

import pytest

from scrapers.core.http_client import HttpClient, HttpRequest, HttpResponse
from scrapers.core.logger import ScraperLogger
from scrapers.core.metrics import MetricsCollector
from scrapers.core.rate_limiter import RateLimiter
from scrapers.core.retry_policy import RetryPolicy
from scrapers.core.robots import RobotsPolicy
from scrapers.core.source_config import SourceConfig
from scrapers.core.source_registry import SourceCategory, SourceDefinition, SourceRegistry, default_source_registry
from scrapers.core.user_agent import DEFAULT_USER_AGENT, UserAgentManager, UserAgentProfile
from scrapers.pipeline.source_trust import SourceTier


def test_default_source_registry_contains_expected_metadata() -> None:
    """Default registry exposes all planned Sprint 012 metadata sources."""
    registry = default_source_registry()

    assert len(registry.all()) == 11
    assert registry.get("zse") is not None
    assert registry.get_by_display_name("Financial Gazette") is not None
    assert len(registry.by_category(SourceCategory.OFFICIAL)) == 4
    assert len(registry.by_category(SourceCategory.INSTITUTIONAL)) == 4
    assert len(registry.by_category(SourceCategory.FINANCIAL_JOURNALISM)) == 3
    assert [source.id for source in registry.by_priority(30)] == ["zse", "vfex", "rbz"]
    registry.validate_unique()


def test_source_registry_enable_disable_and_duplicate_validation() -> None:
    """Registry can disable sources and rejects duplicate ids/names."""
    source = SourceDefinition(
        id="sample",
        display_name="Sample Source",
        category=SourceCategory.OFFICIAL,
        priority=1,
        enabled=True,
        trust_tier=SourceTier.TIER_1_OFFICIAL,
        homepage="https://example.test",
        robots_url="https://example.test/robots.txt",
        scraper_class=None,
    )
    registry = SourceRegistry([source])

    assert registry.disable("sample").enabled is False
    assert registry.all(include_disabled=False) == []
    assert registry.enable("sample").enabled is True
    with pytest.raises(ValueError):
        registry.register(source)


def test_source_config_loads_defaults_and_source_env_overrides() -> None:
    """Source config supports default and source-specific environment variables."""
    config = SourceConfig.from_env(
        "financial-gazette",
        {
            "SCRAPER_DEFAULT_TIMEOUT": "12",
            "SCRAPER_DEFAULT_RETRY_COUNT": "2",
            "SCRAPER_FINANCIAL_GAZETTE_TIMEOUT": "7.5",
            "SCRAPER_FINANCIAL_GAZETTE_ENABLED": "false",
            "SCRAPER_FINANCIAL_GAZETTE_USER_AGENT": "TestAgent/1.0",
        },
    )

    assert config.timeout == 7.5
    assert config.retry_count == 2
    assert config.enabled is False
    assert config.user_agent == "TestAgent/1.0"


def test_retry_policy_uses_exponential_backoff_for_exceptions_and_statuses() -> None:
    """Retry policy retries configured exceptions and status codes."""
    policy = RetryPolicy(max_retries=2, backoff_factor=0.25)
    sleeps: list[float] = []
    attempts = {"count": 0}

    def flaky_operation() -> HttpResponse:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise URLError("temporary")
        if attempts["count"] == 2:
            return HttpResponse(status_code=503, text="busy", url="https://example.test")
        return HttpResponse(status_code=200, text="ok", url="https://example.test")

    response = policy.run(flaky_operation, sleep=sleeps.append)

    assert response.status_code == 200
    assert sleeps == [0.25, 0.5]
    assert attempts["count"] == 3


def test_rate_limiter_applies_interval_rpm_and_cooldown() -> None:
    """Rate limiter calculates waits without using real sleeping in tests."""
    now = {"value": 0.0}
    waits: list[float] = []

    def clock() -> float:
        return now["value"]

    def sleep(seconds: float) -> None:
        waits.append(round(seconds, 3))
        now["value"] += seconds

    limiter = RateLimiter(minimum_interval=2.0, requests_per_minute=2, clock=clock, sleep=sleep)
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    limiter.cooldown(5.0)
    limiter.acquire()

    assert waits[0] == 2.0
    assert 58.0 in waits
    assert 5.0 in waits


def test_http_client_uses_fake_transport_and_never_requires_network(monkeypatch) -> None:
    """HTTP abstraction is testable offline through an injected transport."""
    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("network should not be called")

    monkeypatch.setattr("scrapers.core.http_client.request.urlopen", forbidden_urlopen)
    captured: list[HttpRequest] = []

    def fake_transport(request_: HttpRequest) -> HttpResponse:
        captured.append(request_)
        return HttpResponse(status_code=200, text="fixture", url=request_.url)

    config = SourceConfig(timeout=3, user_agent="OfflineTest/1.0")
    client = HttpClient(config=config, transport=fake_transport)

    response = client.get("https://example.test/resource", headers={"X-Test": "yes"})

    assert response.text == "fixture"
    assert captured[0].method == "GET"
    assert captured[0].timeout == 3
    assert captured[0].headers["User-Agent"] == "OfflineTest/1.0"
    assert captured[0].headers["X-Test"] == "yes"


def test_user_agent_profiles_return_expected_defaults() -> None:
    """User agent manager provides bot, browser, mobile, and API profiles."""
    manager = UserAgentManager()

    assert manager.get() == DEFAULT_USER_AGENT
    assert "Mozilla/5.0" in manager.get(UserAgentProfile.DESKTOP)
    assert "Mobile" in manager.get(UserAgentProfile.MOBILE)
    assert manager.get(UserAgentProfile.API) == "InvestGuideAPIClient/0.1"


def test_robots_policy_stores_metadata_without_fetching() -> None:
    """Robots policy stores URLs and keeps permission checks as future hooks."""
    policy = RobotsPolicy()
    rule = policy.register("zse", "https://www.zse.co.zw")

    assert rule.robots_url == "https://www.zse.co.zw/robots.txt"
    assert policy.get("zse") == rule
    assert policy.can_fetch("zse", "https://www.zse.co.zw/news", DEFAULT_USER_AGENT) is None


def test_metrics_collector_tracks_runs_retries_and_articles() -> None:
    """Metrics collector accumulates source run counters."""
    collector = MetricsCollector()
    metrics = collector.for_source("zse")

    metrics.record_success(execution_time=1.25, articles_found=3, articles_ingested=2)
    metrics.record_retry(2)
    metrics.record_failure(execution_time=0.5)

    assert metrics.successful_runs == 1
    assert metrics.failed_runs == 1
    assert metrics.retry_count == 2
    assert metrics.articles_found == 3
    assert metrics.articles_ingested == 2
    assert collector.snapshot()["zse"] is metrics


def test_scraper_logger_logs_lifecycle_and_redacts_secrets(caplog) -> None:
    """Scraper logger emits lifecycle messages without leaking obvious secrets."""
    logger = logging.getLogger("tests.scraper_logger")
    scraper_logger = ScraperLogger(logger)

    with caplog.at_level(logging.INFO, logger="tests.scraper_logger"):
        scraper_logger.scraper_started("ZSE")
        scraper_logger.scraper_completed("ZSE", execution_time=1.2, article_count=4)
        scraper_logger.scraper_failed("ZSE", execution_time=0.1, error="token=secret-value failed")
        scraper_logger.retry_attempt("ZSE", attempt=1, delay=0.5)

    messages = [record.message for record in caplog.records]
    assert "scraper started" in messages
    assert "scraper completed" in messages
    assert "scraper failed" in messages
    assert "scraper retry" in messages
    failure_records = [record for record in caplog.records if record.message == "scraper failed"]
    assert failure_records[0].error == "token=[REDACTED] failed"
"""Offline tests for the opt-in live ZSE announcements scraper."""

from __future__ import annotations

from pathlib import Path

from scrapers.core.context_factory import ScraperContextFactory
from scrapers.core.http_client import HttpRequest, HttpResponse
from scrapers.pipeline.asset_linker import AssetMetadata, link_assets
from scrapers.pipeline.ingestion_contract import build_ingestion_payload
from scrapers.pipeline.normalizer import normalize_article
from scrapers.zse.live_announcements_scraper import DEFAULT_ZSE_ANNOUNCEMENTS_URL, ZSELiveAnnouncementsScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "zse_announcements_sample.html"

def test_live_disabled_by_default_does_not_call_transport() -> None:
    requests: list[HttpRequest] = []

    def fake_transport(request: HttpRequest) -> HttpResponse:
        requests.append(request)
        return HttpResponse(status_code=200, text="unexpected", url=request.url)

    context = ScraperContextFactory(transport=fake_transport).build("zse")
    result = ZSELiveAnnouncementsScraper(context=context).run()

    assert context.config.live_enabled is False
    assert result.success is True
    assert result.articles == []
    assert requests == []

def test_parser_extracts_fixture_articles_without_network() -> None:
    articles = ZSELiveAnnouncementsScraper().parse(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert len(articles) == 3
    assert articles[0].source == "ZSE"
    assert articles[0].title == "Delta Corporation Limited Dividend Notice"
    assert articles[0].url == "https://www.zse.co.zw/2026/06/20/delta-corporation-limited-dividend-notice/"
    assert articles[0].published_at.isoformat() == "2026-06-20T07:30:00+00:00"
    assert articles[1].published_at.isoformat() == "2026-06-18T00:00:00+00:00"
    assert articles[2].published_at.tzinfo is not None

def test_live_enabled_uses_context_http_client_and_rate_limiter() -> None:
    calls: list[str] = []
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    def fake_transport(request: HttpRequest) -> HttpResponse:
        calls.append(request.url)
        return HttpResponse(status_code=200, text=fixture_html, url=request.url)

    context = ScraperContextFactory(env={"SCRAPER_LIVE_ENABLED": "true"}, transport=fake_transport).build("zse")
    context.rate_limiter.acquire = lambda: calls.append("rate-limit")  # type: ignore[method-assign]

    result = ZSELiveAnnouncementsScraper(context=context).run()

    assert result.success is True
    assert len(result.articles) == 3
    assert calls == ["rate-limit", DEFAULT_ZSE_ANNOUNCEMENTS_URL]

def test_live_failures_are_reported_and_measured() -> None:
    def fake_transport(request: HttpRequest) -> HttpResponse:
        return HttpResponse(status_code=503, text="unavailable", url=request.url)

    context = ScraperContextFactory(env={"SCRAPER_LIVE_ENABLED": "true"}, transport=fake_transport).build("zse")
    context.rate_limiter.acquire = lambda: None  # type: ignore[method-assign]

    result = ZSELiveAnnouncementsScraper(context=context).run()

    assert result.success is False
    assert result.articles == []
    assert "503" in result.errors[0]
    assert context.metrics.failed_runs == 1

def test_zse_articles_are_ingestion_pipeline_compatible() -> None:
    article = ZSELiveAnnouncementsScraper().parse(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
    normalized = normalize_article(article)
    payload = build_ingestion_payload(normalized)

    assert payload.source == "ZSE"
    assert payload.asset_tickers == ["DELTA"]
    assert payload.content_hash is not None
    assert len(payload.content_hash) == 64




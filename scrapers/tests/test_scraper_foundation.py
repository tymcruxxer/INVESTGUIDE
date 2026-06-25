"""Scraper foundation tests."""

from __future__ import annotations

from datetime import UTC, datetime
import socket

from scrapers.base_scraper import BaseScraper, ScrapedArticle
from scrapers.news.financial_gazette import FinancialGazetteScraper
from scrapers.news.herald_business import HeraldBusinessScraper
from scrapers.news.newsday_business import NewsDayBusinessScraper
from scrapers.pipeline.asset_linker import link_assets
from scrapers.pipeline.deduplicator import DeduplicationIndex, content_hash, deduplicate_articles
from scrapers.pipeline.ingestion_contract import build_ingestion_payload
from scrapers.pipeline.normalizer import normalize_article
from scrapers.rbz.macro_scraper import RBZMacroScraper
from scrapers.research.ih_securities import IHSecuritiesScraper
from scrapers.research.mmc_capital import MMCCapitalScraper
from scrapers.vfex.market_scraper import VFEXMarketScraper
from scrapers.zse.announcements_scraper import ZSEAnnouncementsScraper


class ExplodingScraper(BaseScraper):
    """Test scraper that exercises BaseScraper error handling."""

    source_name = "Exploding Source"
    source_url = "fixture://exploding"

    def fetch(self):
        raise RuntimeError("fixture failure")

    def parse(self, raw_content):
        return []


def test_base_scraper_run_returns_error_result() -> None:
    """BaseScraper.run captures source errors in ScraperResult."""
    result = ExplodingScraper().run()

    assert result.success is False
    assert result.source_name == "Exploding Source"
    assert result.errors == ["fixture failure"]


def test_placeholder_scrapers_return_fixture_articles_without_network(monkeypatch) -> None:
    """All Sprint 009 placeholders return local fixtures and make no socket calls."""

    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are not allowed in Sprint 009")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    scraper_classes = [
        FinancialGazetteScraper,
        NewsDayBusinessScraper,
        HeraldBusinessScraper,
        ZSEAnnouncementsScraper,
        VFEXMarketScraper,
        RBZMacroScraper,
        IHSecuritiesScraper,
        MMCCapitalScraper,
    ]

    for scraper_class in scraper_classes:
        result = scraper_class().run()
        assert result.success is True
        assert len(result.articles) == 1
        assert result.articles[0].source == scraper_class.source_name
        assert result.articles[0].url is not None
        assert result.articles[0].url.startswith("fixture://")


def test_normalizer_cleans_text_and_dates() -> None:
    """Normalizer standardizes text, URL, language, and datetime fields."""
    article = normalize_article(
        {
            "title": "  Sample   Title  ",
            "summary": "  Two   spaces ",
            "content": None,
            "source": "  Source  ",
            "url": " fixture://article ",
            "published_at": "2026-06-25T08:00:00Z",
            "language": " EN ",
        }
    )

    assert article.title == "Sample Title"
    assert article.summary == "Two spaces"
    assert article.source == "Source"
    assert article.url == "fixture://article"
    assert article.language == "en"
    assert article.published_at.tzinfo is not None


def test_deduplicator_detects_url_title_and_content_duplicates() -> None:
    """Deduplication checks URL, normalized title, and content hash."""
    published_at = datetime(2026, 6, 25, tzinfo=UTC)
    first = ScrapedArticle(
        title="Delta Corporation Market Update",
        source="Fixture",
        published_at=published_at,
        content="Delta Corporation content.",
        url="fixture://delta",
    )
    same_url = ScrapedArticle(
        title="Different title",
        source="Fixture",
        published_at=published_at,
        content="Different content.",
        url="fixture://delta",
    )
    same_title = ScrapedArticle(
        title="delta corporation market update",
        source="Fixture",
        published_at=published_at,
        content="Another content.",
        url="fixture://other",
    )
    same_hash = ScrapedArticle(
        title="Delta Corporation Market Update",
        source="Fixture",
        published_at=published_at,
        content="Delta Corporation content.",
        url="fixture://hash",
    )

    index = DeduplicationIndex.empty()
    index.add(first)

    assert index.is_duplicate(same_url) is True
    assert index.is_duplicate(same_title) is True
    assert index.is_duplicate(same_hash) is True
    assert content_hash(first) == content_hash(same_hash)
    assert deduplicate_articles([first, same_url, same_title, same_hash]) == [first]


def test_asset_linker_uses_explicit_company_matches_only() -> None:
    """Asset linker maps company names and avoids broad exchange-level mapping."""
    text = "Delta Corporation and Econet Wireless were mentioned in a VFEX market context."

    assert link_assets(text) == ["DELTA", "ECO"]
    assert link_assets("VFEX market activity was discussed without company names.") == []
    assert link_assets("Tigere REIT income themes were discussed.") == ["TIGERE"]


def test_ingestion_payload_matches_backend_news_create_contract() -> None:
    """Ingestion contract produces backend-compatible NewsCreate fields."""
    article = ScrapedArticle(
        title="Sample Delta article",
        summary="Delta Corporation was mentioned.",
        content="Fixture content only.",
        source="Fixture Source",
        published_at=datetime(2026, 6, 25, tzinfo=UTC),
        url="fixture://delta",
    )

    payload = build_ingestion_payload(article)
    news_create = payload.to_news_create_dict()

    assert payload.content_hash is not None
    assert news_create["title"] == "Sample Delta article"
    assert news_create["source"] == "Fixture Source"
    assert news_create["asset_tickers"] == ["DELTA"]
    assert "content_hash" not in news_create
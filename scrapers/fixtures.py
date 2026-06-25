"""Fixture helpers for placeholder scrapers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from scrapers.base_scraper import BaseScraper, ScrapedArticle
from scrapers.pipeline.normalizer import normalize_articles


def sample_article(
    *,
    title: str,
    source: str,
    url: str,
    summary: str,
    content: str,
    published_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a local sample article dictionary."""
    return {
        "title": title,
        "source": source,
        "url": url,
        "summary": summary,
        "content": content,
        "published_at": published_at or datetime(2026, 6, 25, 8, 0, tzinfo=UTC),
        "language": "en",
    }


class FixtureScraper(BaseScraper):
    """Base class for fixture-only placeholder scrapers."""

    fixture_articles: list[dict[str, Any]] = []

    def fetch(self) -> list[dict[str, Any]]:
        """Return in-repository fixture articles only."""
        return list(self.fixture_articles)

    def parse(self, raw_content: list[dict[str, Any]]) -> list[ScrapedArticle]:
        """Normalize fixture dictionaries into scraped articles."""
        return normalize_articles(raw_content)
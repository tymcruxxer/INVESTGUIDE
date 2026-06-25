"""Article normalization helpers for scraper outputs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from scrapers.base_scraper import ScrapedArticle


def clean_text(value: str | None) -> str | None:
    """Collapse whitespace and trim text fields."""
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned or None


def normalize_url(value: str | None) -> str | None:
    """Trim URL values and keep empty values as null."""
    return clean_text(value)


def normalize_language(value: str | None) -> str:
    """Normalize language values for backend news payloads."""
    cleaned = clean_text(value)
    return (cleaned or "en").lower()


def normalize_published_at(value: datetime | str | None) -> datetime:
    """Normalize publication date values to timezone-aware datetimes."""
    if value is None:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize_article(article: ScrapedArticle | dict[str, Any]) -> ScrapedArticle:
    """Normalize one scraped article into the canonical scraper shape."""
    data = article.__dict__ if isinstance(article, ScrapedArticle) else dict(article)
    return ScrapedArticle(
        title=clean_text(data.get("title")) or "Untitled article",
        summary=clean_text(data.get("summary")),
        content=clean_text(data.get("content")),
        source=clean_text(data.get("source")) or "Unknown Source",
        url=normalize_url(data.get("url")),
        author=clean_text(data.get("author")),
        image_url=normalize_url(data.get("image_url")),
        published_at=normalize_published_at(data.get("published_at")),
        language=normalize_language(data.get("language")),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_articles(articles: list[ScrapedArticle | dict[str, Any]]) -> list[ScrapedArticle]:
    """Normalize a list of scraped articles."""
    return [normalize_article(article) for article in articles]
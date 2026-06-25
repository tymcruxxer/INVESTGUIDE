"""Ingestion payload contract for backend-compatible news articles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from scrapers.base_scraper import ScrapedArticle
from scrapers.pipeline.asset_linker import link_assets
from scrapers.pipeline.deduplicator import content_hash


@dataclass(frozen=True)
class NormalizedArticlePayload:
    """Payload compatible with backend `NewsCreate` semantics."""

    title: str
    source: str
    published_at: datetime
    summary: str | None = None
    content: str | None = None
    url: str | None = None
    image_url: str | None = None
    author: str | None = None
    language: str = "en"
    asset_tickers: list[str] = field(default_factory=list)
    sentiment: Decimal | None = None
    relevance_score: Decimal | None = None
    credibility_score: Decimal | None = None
    content_hash: str | None = None

    def to_news_create_dict(self) -> dict[str, object]:
        """Return a dict compatible with backend NewsCreate fields."""
        return {
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "source": self.source,
            "author": self.author,
            "published_at": self.published_at,
            "url": self.url,
            "image_url": self.image_url,
            "language": self.language,
            "sentiment": self.sentiment,
            "relevance_score": self.relevance_score,
            "credibility_score": self.credibility_score,
            "asset_tickers": self.asset_tickers,
        }


def build_ingestion_payload(article: ScrapedArticle) -> NormalizedArticlePayload:
    """Build a normalized ingestion payload from a scraped article."""
    text = " ".join(part for part in (article.title, article.summary, article.content) if part)
    return NormalizedArticlePayload(
        title=article.title,
        summary=article.summary,
        content=article.content,
        source=article.source,
        author=article.author,
        published_at=article.published_at,
        url=article.url,
        image_url=article.image_url,
        language=article.language,
        asset_tickers=link_assets(text),
        content_hash=content_hash(article),
    )
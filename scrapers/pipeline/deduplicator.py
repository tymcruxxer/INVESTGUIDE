"""Deduplication helpers for scraper outputs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from scrapers.base_scraper import ScrapedArticle

_WORD_RE = re.compile(r"[^a-z0-9]+")


def normalize_title(title: str) -> str:
    """Normalize article titles for duplicate comparison."""
    return _WORD_RE.sub(" ", title.lower()).strip()


def content_hash(article: ScrapedArticle) -> str:
    """Return a deterministic hash for article title and content."""
    content = "\n".join(
        part for part in (normalize_title(article.title), article.content or article.summary or "") if part
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@dataclass
class DeduplicationIndex:
    """In-memory duplicate detector for one ingestion batch."""

    urls: set[str]
    titles: set[str]
    hashes: set[str]

    @classmethod
    def empty(cls) -> "DeduplicationIndex":
        """Create an empty deduplication index."""
        return cls(urls=set(), titles=set(), hashes=set())

    def add(self, article: ScrapedArticle) -> None:
        """Record an article identity in the index."""
        if article.url:
            self.urls.add(article.url.strip().lower())
        self.titles.add(normalize_title(article.title))
        self.hashes.add(content_hash(article))

    def is_duplicate(self, article: ScrapedArticle) -> bool:
        """Return true when URL, normalized title, or content hash already exists."""
        normalized_url = article.url.strip().lower() if article.url else None
        if normalized_url and normalized_url in self.urls:
            return True
        if normalize_title(article.title) in self.titles:
            return True
        return content_hash(article) in self.hashes


def deduplicate_articles(articles: list[ScrapedArticle]) -> list[ScrapedArticle]:
    """Remove duplicates from a batch while preserving first occurrence order."""
    index = DeduplicationIndex.empty()
    unique_articles: list[ScrapedArticle] = []
    for article in articles:
        if index.is_duplicate(article):
            continue
        index.add(article)
        unique_articles.append(article)
    return unique_articles
"""Base scraper contracts for InvestGuide ingestion sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from scrapers.core.context import ScraperContext


@dataclass(frozen=True)
class ScrapedArticle:
    """Raw article-like payload produced by a source scraper."""

    title: str
    source: str
    published_at: datetime
    summary: str | None = None
    content: str | None = None
    url: str | None = None
    author: str | None = None
    image_url: str | None = None
    language: str = "en"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScraperResult:
    """Result returned by a scraper run."""

    source_name: str
    source_url: str
    articles: list[ScrapedArticle] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def success(self) -> bool:
        """Return true when the run completed without scraper errors."""
        return not self.errors


class BaseScraper(ABC):
    """Base interface for source-specific scrapers.

    Scrapers receive one ``ScraperContext`` dependency container. Fixture
    scrapers may omit the context and receive a default offline context.
    """

    source_name: str
    source_url: str

    def __init__(self, context: ScraperContext | None = None) -> None:
        if context is None:
            from scrapers.core.context_factory import ScraperContextFactory

            context = ScraperContextFactory().build(self.source_name)
        self.context = context
        self.logger = self.context.logger.logger

    @abstractmethod
    def fetch(self) -> Any:
        """Fetch raw source content.

        Placeholder implementations return in-repository fixtures only.
        """

    @abstractmethod
    def parse(self, raw_content: Any) -> list[ScrapedArticle]:
        """Parse raw source content into scraped articles."""

    def run(self) -> ScraperResult:
        """Execute fetch and parse with structured error handling."""
        self.context.logger.scraper_started(self.source_name)
        try:
            raw_content = self.fetch()
            articles = self.parse(raw_content)
        except Exception as exc:  # pragma: no cover - exact exception varies by scraper
            self.context.logger.scraper_failed(self.source_name, execution_time=0.0, error=str(exc))
            return ScraperResult(
                source_name=self.source_name,
                source_url=self.source_url,
                errors=[str(exc)],
            )

        self.context.logger.scraper_completed(
            self.source_name,
            execution_time=0.0,
            article_count=len(articles),
        )
        return ScraperResult(
            source_name=self.source_name,
            source_url=self.source_url,
            articles=articles,
        )
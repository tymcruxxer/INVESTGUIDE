"""Opt-in live ZSE announcements scraper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin

from scrapers.base_scraper import BaseScraper, ScrapedArticle, ScraperResult
from scrapers.core.context import ScraperContext
from scrapers.core.context_factory import ScraperContextFactory

DEFAULT_ZSE_ANNOUNCEMENTS_URL = "https://www.zse.co.zw/category/announcements/"
ZSE_SOURCE_NAME = "ZSE"


@dataclass(frozen=True)
class ParsedAnnouncementLink:
    """Announcement link extracted from ZSE HTML."""

    title: str
    url: str
    published_at: datetime | None = None


class ZSEAnnouncementsHTMLParser(HTMLParser):
    """Small HTML parser for ZSE announcement/article links."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[ParsedAnnouncementLink] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []
        self._pending_datetime: datetime | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value for name, value in attrs if value is not None}
        if tag.lower() == "time":
            parsed = self._parse_datetime(attr_map.get("datetime") or "")
            if parsed is not None:
                self._pending_datetime = parsed
        if tag.lower() == "a" and attr_map.get("href"):
            self._current_href = urljoin(self.base_url, attr_map["href"])
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        title = " ".join(" ".join(self._current_text).split())
        if title and self._looks_like_announcement(self._current_href, title):
            self.links.append(
                ParsedAnnouncementLink(
                    title=title,
                    url=self._current_href,
                    published_at=self._pending_datetime,
                )
            )
        self._current_href = None
        self._current_text = []

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        if not value:
            return None
        normalized = value.replace("Z", "+00:00")
        if "T" not in normalized and len(normalized) == 10:
            normalized = f"{normalized}T00:00:00+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _looks_like_announcement(url: str, title: str) -> bool:
        text = f"{url} {title}".lower()
        excluded = {"login", "register", "privacy", "terms", "facebook", "twitter", "linkedin"}
        if any(item in text for item in excluded):
            return False
        keywords = ("announcement", "notice", "cautionary", "dividend", "results", "circular", "trading update")
        return any(keyword in text for keyword in keywords)


class ZSELiveAnnouncementsScraper(BaseScraper):
    """Opt-in live scraper for ZSE announcement links."""

    source_name = ZSE_SOURCE_NAME
    source_url = DEFAULT_ZSE_ANNOUNCEMENTS_URL

    def __init__(self, context: ScraperContext | None = None, announcements_url: str = DEFAULT_ZSE_ANNOUNCEMENTS_URL) -> None:
        super().__init__(context or ScraperContextFactory().build("zse"))
        self.announcements_url = announcements_url
        self.source_url = announcements_url

    def fetch(self) -> str:
        """Fetch ZSE announcements HTML only when live scraping is explicitly enabled."""
        if not self.context.config.live_enabled:
            self.context.logger.logger.info("live scraping disabled", extra={"source_name": self.source_name})
            return ""
        self.context.rate_limiter.acquire()
        response = self.context.http_client.get(self.announcements_url)
        if response.status_code >= 400:
            raise RuntimeError(f"ZSE announcements request failed with status {response.status_code}")
        return response.text

    def parse(self, raw_content: str) -> list[ScrapedArticle]:
        """Parse ZSE announcement links into ScrapedArticle objects."""
        if not raw_content:
            return []
        parser = ZSEAnnouncementsHTMLParser(self.announcements_url)
        parser.feed(raw_content)
        articles: list[ScrapedArticle] = []
        for link in parser.links:
            articles.append(
                ScrapedArticle(
                    title=link.title,
                    source=ZSE_SOURCE_NAME,
                    published_at=link.published_at or datetime.now(UTC),
                    url=link.url,
                    summary=None,
                    content=None,
                    metadata={"source_type": "zse_announcement"},
                )
            )
        return articles

    def run(self) -> ScraperResult:
        """Run scraper and record source metrics."""
        result = super().run()
        if result.success:
            self.context.metrics.record_success(execution_time=0.0, articles_found=len(result.articles))
        else:
            self.context.metrics.record_failure(execution_time=0.0)
        return result


def main() -> None:
    """Optional manual entrypoint for explicitly enabled live scraping."""
    scraper = ZSELiveAnnouncementsScraper()
    result = scraper.run()
    print(f"ZSE announcements scraped: {len(result.articles)}; errors={len(result.errors)}")


if __name__ == "__main__":
    main()

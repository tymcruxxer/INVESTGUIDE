"""ZSE announcements placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class ZSEAnnouncementsScraper(FixtureScraper):
    """Fixture-only ZSE announcements scraper placeholder."""

    source_name = "Zimbabwe Stock Exchange Announcements"
    source_url = "https://www.zse.co.zw/"
    fixture_articles = [
        sample_article(
            title="Sample: ZSE announcement placeholder for Innscor Africa",
            source=source_name,
            url="fixture://zse/innscor-announcement-placeholder",
            summary="Local fixture for future ZSE announcement ingestion.",
            content="This fixture mentions Innscor Africa for asset-linking tests only.",
        )
    ]
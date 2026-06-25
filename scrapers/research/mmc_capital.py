"""MMC Capital research placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class MMCCapitalScraper(FixtureScraper):
    """Fixture-only MMC Capital research scraper placeholder."""

    source_name = "MMC Capital"
    source_url = "https://www.mmccapital.co.zw/"
    fixture_articles = [
        sample_article(
            title="Sample: MMC Capital mining placeholder for Padenga Holdings",
            source=source_name,
            url="fixture://mmc-capital/padenga-research-placeholder",
            summary="Local fixture for future MMC Capital research ingestion.",
            content="This fixture mentions Padenga Holdings and mining themes for tests only.",
        )
    ]
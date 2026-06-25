"""IH Securities research placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class IHSecuritiesScraper(FixtureScraper):
    """Fixture-only IH Securities research scraper placeholder."""

    source_name = "IH Securities"
    source_url = "https://ih-group.com/"
    fixture_articles = [
        sample_article(
            title="Sample: IH Securities research placeholder for CBZ Holdings",
            source=source_name,
            url="fixture://ih-securities/cbz-research-placeholder",
            summary="Local fixture for future institutional research ingestion.",
            content="This fixture mentions CBZ Holdings for asset-linking tests only.",
        )
    ]
"""VFEX market placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class VFEXMarketScraper(FixtureScraper):
    """Fixture-only VFEX market scraper placeholder."""

    source_name = "Victoria Falls Stock Exchange"
    source_url = "https://www.vfex.exchange/"
    fixture_articles = [
        sample_article(
            title="Sample: VFEX market placeholder for Caledonia Mining",
            source=source_name,
            url="fixture://vfex/caledonia-market-placeholder",
            summary="Local fixture for future VFEX market ingestion.",
            content="This fixture mentions Caledonia Mining and VFEX without mapping VFEX to all assets.",
        )
    ]
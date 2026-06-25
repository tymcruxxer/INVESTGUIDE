"""Herald Business placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class HeraldBusinessScraper(FixtureScraper):
    """Fixture-only Herald Business scraper placeholder."""

    source_name = "Herald Business"
    source_url = "https://www.herald.co.zw/category/business/"
    fixture_articles = [
        sample_article(
            title="Sample: Herald Business REIT placeholder for Tigere REIT",
            source=source_name,
            url="fixture://herald-business/tigere-reit-placeholder",
            summary="Local fixture for future Herald Business ingestion.",
            content="This fixture mentions Tigere REIT for asset-linking tests only.",
        )
    ]
"""NewsDay Business placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class NewsDayBusinessScraper(FixtureScraper):
    """Fixture-only NewsDay Business scraper placeholder."""

    source_name = "NewsDay Business"
    source_url = "https://www.newsday.co.zw/business/"
    fixture_articles = [
        sample_article(
            title="Sample: NewsDay Business telecom placeholder for Econet Wireless",
            source=source_name,
            url="fixture://newsday-business/econet-telecom-placeholder",
            summary="Local fixture for future NewsDay Business ingestion.",
            content="This fixture mentions Econet Wireless Zimbabwe for asset-linking tests only.",
        )
    ]
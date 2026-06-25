"""Financial Gazette placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class FinancialGazetteScraper(FixtureScraper):
    """Fixture-only Financial Gazette scraper placeholder."""

    source_name = "Financial Gazette"
    source_url = "https://www.financialgazette.co.zw/"
    fixture_articles = [
        sample_article(
            title="Sample: Financial Gazette market news placeholder for Delta Corporation",
            source=source_name,
            url="fixture://financial-gazette/delta-market-placeholder",
            summary="Local fixture for future Financial Gazette business news ingestion.",
            content="This fixture mentions Delta Corporation for asset-linking tests only.",
        )
    ]
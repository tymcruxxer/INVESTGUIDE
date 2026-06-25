"""RBZ macro placeholder scraper."""

from scrapers.fixtures import FixtureScraper, sample_article


class RBZMacroScraper(FixtureScraper):
    """Fixture-only RBZ macro scraper placeholder."""

    source_name = "Reserve Bank of Zimbabwe"
    source_url = "https://www.rbz.co.zw/"
    fixture_articles = [
        sample_article(
            title="Sample: RBZ macro policy placeholder",
            source=source_name,
            url="fixture://rbz/macro-policy-placeholder",
            summary="Local fixture for future RBZ macroeconomic ingestion.",
            content="This fixture discusses inflation and interest rates without asserting a real policy event.",
        )
    ]
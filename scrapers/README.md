# InvestGuide Scrapers

Sprint 009 introduces the scraper engine foundation only.

The current scraper package provides:

* `BaseScraper`, `ScrapedArticle`, and `ScraperResult` contracts
* fixture-only placeholder source scrapers
* article normalization helpers
* batch deduplication helpers
* simple asset-linking contract
* backend-compatible ingestion payload contract

Current limitations:

* no real HTTP requests
* no browser automation or Playwright execution
* no scheduler jobs
* no database writes
* no sentiment, embeddings, RAG, or AI analysis

Placeholder scrapers intentionally return local fixture articles through `fetch()` so tests can validate contracts without external network calls.
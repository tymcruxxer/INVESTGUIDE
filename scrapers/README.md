# InvestGuide Scrapers

The scraper package contains InvestGuide's news ingestion foundation.

Sprint 009 introduced scraper contracts and fixture-only source placeholders. Sprint 010 adds dry-run ingestion orchestration that connects those fixtures into a controlled pipeline without network calls or database writes.

## Current Capabilities

* `BaseScraper`, `ScrapedArticle`, and `ScraperResult` contracts
* fixture-only placeholder source scrapers
* article normalization helpers
* batch deduplication helpers
* simple asset-linking contract
* backend-compatible ingestion payload contract
* source trust tier and credibility scoring metadata
* dry-run ingestion orchestrator
* CLI dry-run summary command

## Dry-Run Command

Run all fixture placeholder scrapers through the dry-run ingestion pipeline:

```bash
python -m scrapers.run_dry_ingestion
```

The command prints:

* sources run
* articles scraped
* duplicates removed
* asset tickers linked
* source trust scores
* errors, if any

## Source Trust Scores

* Tier 1 - Official Sources: `1.0`
* Tier 2 - Institutional Research: `0.85`
* Tier 3 - Financial Journalism: `0.7`
* Tier 4 - General Web Sources: `0.4`

## Current Limitations

* no real HTTP requests
* no browser automation or Playwright execution
* no live website parsing
* no scheduler jobs
* no database writes
* no backend ingestion API endpoints
* no sentiment, embeddings, RAG, or AI analysis

Placeholder scrapers intentionally return local fixture articles through `fetch()` so tests can validate contracts without external network calls.
# InvestGuide Scrapers

The scraper package contains InvestGuide's data ingestion and scraper infrastructure foundation.

Sprint 009 introduced scraper contracts and fixture-only source placeholders. Sprint 010 added dry-run ingestion orchestration. Sprint 012 adds reusable production-grade scraper infrastructure for future live sources while still making no network calls or database writes.

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
* source registry and source metadata
* environment-driven source configuration
* HTTP client abstraction with injectable transport
* retry policy with exponential backoff
* rate limiter with interval, RPM, cooldown, and burst controls
* user-agent manager
* robots policy metadata abstraction
* scraper metrics collector
* scraper lifecycle logger


## Core Scraper Infrastructure

Sprint 012 adds reusable infrastructure under `scrapers/core/`:

* `source_registry.py` - registers source metadata, enables/disables sources, validates uniqueness, and looks up by id, display name, category, or priority.
* `source_config.py` - loads per-source timeout, retry, backoff, rate limit, interval, user-agent, and enabled settings from environment variables.
* `http_client.py` - defines a transport-independent HTTP abstraction for future GET requests. Tests use fake transports; no live requests are made.
* `retry_policy.py` - supports retryable status codes, retryable exceptions, max retries, and exponential backoff.
* `rate_limiter.py` - enforces minimum intervals, requests per minute, cooldowns, and burst protection.
* `user_agent.py` - manages bot, desktop, mobile, and API user-agent profiles.
* `robots.py` - stores robots.txt metadata and future permission-check hooks without downloading robots files.
* `metrics.py` - tracks successful runs, failed runs, execution time, retry count, last run, articles found, and articles ingested.
* `logger.py` - logs scraper lifecycle events and retry attempts while redacting common secret fragments.

Default metadata exists for official, institutional, and financial journalism sources: ZSE, VFEX, RBZ, ZIMSTAT, IH Securities, MMC Capital, Old Mutual Investment Group, ABC Stockbrokers, Financial Gazette, NewsDay Business, and Herald Business.

## Environment Configuration

Source configuration supports defaults and source-specific overrides:

```bash
SCRAPER_DEFAULT_TIMEOUT=10
SCRAPER_DEFAULT_RETRY_COUNT=3
SCRAPER_DEFAULT_RETRY_BACKOFF=0.5
SCRAPER_DEFAULT_RATE_LIMIT=30
SCRAPER_DEFAULT_REQUEST_INTERVAL=2
SCRAPER_DEFAULT_USER_AGENT="InvestGuideBot/0.1 (+https://investguide.app)"
SCRAPER_DEFAULT_ENABLED=true

SCRAPER_FINANCIAL_GAZETTE_TIMEOUT=15
SCRAPER_FINANCIAL_GAZETTE_ENABLED=false
```

Source-specific values override defaults. Environment variable source ids use uppercase with hyphens converted to underscores.
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

* no real HTTP requests by source scrapers; `HttpClient` exists only as an abstraction and tests use fake transports
* no browser automation or Playwright execution
* no live website parsing
* no scheduler jobs
* no database writes
* backend ingestion API exists, but scraper infrastructure still performs no database writes
* no sentiment, embeddings, RAG, or AI analysis

Placeholder scrapers intentionally return local fixture articles through `fetch()` so tests can validate contracts without external network calls.
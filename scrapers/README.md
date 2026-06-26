# InvestGuide Scrapers

The scraper package contains InvestGuide's data ingestion and scraper infrastructure foundation.

Sprint 009 introduced scraper contracts and fixture-only source placeholders. Sprint 010 added dry-run ingestion orchestration. Sprint 012 added reusable production-grade scraper infrastructure. Sprint 013 added the first opt-in live scraper pattern for ZSE announcements while keeping live requests disabled by default and automated tests offline. Sprint 014 adds a live-validation checklist and a backend handoff preview adapter that formats scraper output for `/api/v1/ingestion/news` without sending HTTP requests.

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
* scraper dependency context and context factory
* opt-in ZSE live announcements scraper using saved fixtures and mocked transports in tests
* backend ingestion handoff preview adapter and JSON preview command


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
SCRAPER_LIVE_ENABLED=false

SCRAPER_FINANCIAL_GAZETTE_TIMEOUT=15
SCRAPER_FINANCIAL_GAZETTE_ENABLED=false
```

Source-specific values override defaults. Environment variable source ids use uppercase with hyphens converted to underscores.

## ScraperContext Dependency Injection

Pre-Sprint-013 architecture now groups shared scraper infrastructure into one dependency container:

```python
from scrapers.core.context_factory import ScraperContextFactory
from scrapers.news.financial_gazette import FinancialGazetteScraper

context = ScraperContextFactory().build("financial-gazette")
scraper = FinancialGazetteScraper(context=context)
```

`ScraperContext` owns:

* source configuration
* HTTP client
* retry policy
* rate limiter
* metrics collector and per-source metrics
* scraper logger
* user-agent manager
* robots policy
* optional source definition metadata

Fixture scrapers can still be instantiated without arguments for existing dry-run tests; `BaseScraper` creates a default offline context when one is omitted. Future live scrapers should receive an explicit context from `ScraperContextFactory`.
## Opt-In ZSE Live Scraper

Sprint 013 adds one live scraper candidate: `scrapers/zse/live_announcements_scraper.py`.

Safety controls:

* Live scraping is disabled by default with `SCRAPER_LIVE_ENABLED=false`.
* When disabled, the scraper returns no articles and performs no network request.
* Automated tests use saved HTML fixtures and injected fake HTTP transports only.
* The optional manual command is `python -m scrapers.zse.live_announcements_scraper` and should only be run after explicitly enabling live mode in a local environment.

Source and request policy:

* Source URL: `https://www.zse.co.zw/category/announcements/`
* Source name normalized as: `ZSE`
* Robots policy: metadata is recorded by the shared robots policy abstraction; live use requires a manual robots/terms review before enabling in any shared environment.
* Request interval: default `SCRAPER_DEFAULT_REQUEST_INTERVAL=2` seconds.
* Rate limit: default `SCRAPER_DEFAULT_RATE_LIMIT=30` requests per minute.
* Timeout: default `SCRAPER_DEFAULT_TIMEOUT=10` seconds.
* Retry behavior: default `SCRAPER_DEFAULT_RETRY_COUNT=3` with `SCRAPER_DEFAULT_RETRY_BACKOFF=0.5` exponential backoff.
* User agent: default `InvestGuideBot/0.1 (+https://investguide.app)` unless overridden.

The parser extracts announcement-like links, normalizes relative URLs, supports ISO datetime values when available, and gracefully handles missing dates/content. It returns `ScrapedArticle` objects compatible with the normalizer, deduplicator, asset linker, and ingestion payload builder. It does not write to the backend database.

## Backend Handoff Preview

Sprint 014 adds a contract-only adapter for the existing backend ingestion endpoint.

* Adapter: `scrapers/pipeline/backend_handoff.py`
* Preview command: `python -m scrapers.run_handoff_preview`
* Target endpoint: `/api/v1/ingestion/news`
* Default request mode: `DRY_RUN`

The preview command runs the fixture scraper flow, normalizes and deduplicates articles, links asset tickers, attaches trust scores, builds dry-run payloads, and prints the backend request JSON. It does not send HTTP requests and does not write to the database.

ZSE live validation notes live in `scrapers/zse/LIVE_VALIDATION.md`. Live mode remains disabled by default and manual live validation is optional, local, and gated by robots/terms review.
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

* live HTTP requests are opt-in only; the ZSE live scraper is disabled by default and tests use fixtures/fake transports
* no browser automation or Playwright execution
* live website parsing is limited to the opt-in ZSE announcements parser and is validated with saved HTML fixtures
* no scheduler jobs
* no database writes
* backend ingestion API exists, but scraper infrastructure still performs no database writes
* no sentiment, embeddings, RAG, or AI analysis

Placeholder scrapers intentionally return local fixture articles through `fetch()` so tests can validate contracts without external network calls.




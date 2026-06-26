# ZSE Live Scraper Validation Checklist

## Target Source

* Source: Zimbabwe Stock Exchange announcements
* Target URL: `https://www.zse.co.zw/category/announcements/`
* Scraper: `scrapers/zse/live_announcements_scraper.py`
* Normalized source name: `ZSE`

## Robots / Terms Review Status

* Status: Pending manual review before shared-environment or production use.
* `robots.txt` must be reviewed manually before enabling live scraping outside a local developer environment.
* Source terms and acceptable-use expectations must be reviewed manually before recurring or scheduled access is considered.
* Sprint 014 does not perform live website access as part of automated validation.

## Live Mode Enablement Steps

Live scraping is disabled by default. Enable only for an explicit local manual validation session:

```bash
SCRAPER_LIVE_ENABLED=true
python -m scrapers.zse.live_announcements_scraper
```

Optional source-specific override:

```bash
SCRAPER_ZSE_LIVE_ENABLED=true
python -m scrapers.zse.live_announcements_scraper
```

After validation, unset the variable or set it back to false:

```bash
SCRAPER_LIVE_ENABLED=false
```

## Rate Limit Settings

Default shared scraper settings:

* `SCRAPER_DEFAULT_REQUEST_INTERVAL=2`
* `SCRAPER_DEFAULT_RATE_LIMIT=30`

Manual validation should start with one request only. Do not schedule repeated scraping until robots/terms review is complete.

## Timeout Settings

Default shared scraper setting:

* `SCRAPER_DEFAULT_TIMEOUT=10`

Increase only for manual debugging if the source is slow and the robots/terms review permits access.

## User Agent

Default user agent:

* `InvestGuideBot/0.1 (+https://investguide.app)`

Override only through environment configuration, for example:

```bash
SCRAPER_DEFAULT_USER_AGENT="InvestGuideBot/0.1 (+https://investguide.app)"
```

## Expected Output

The manual command should print a concise result similar to:

```text
ZSE announcements scraped: <count>; errors=<count>
```

Returned articles should be `ScrapedArticle` objects with:

* `source="ZSE"`
* `title`
* `url`
* `published_at` when available, otherwise a safe UTC fallback
* optional `summary` and `content` left empty when unavailable

Parsed output must remain compatible with:

* normalizer
* deduplicator/content hashing
* asset linker
* ingestion payload builder
* backend handoff preview adapter

## Rollback / Safety Notes

* Live scraping remains opt-in and disabled by default.
* If a request fails, disable live mode and keep using fixture-based validation.
* Do not add scheduler jobs until source access rules and failure behavior are reviewed.
* Do not send scraper output to the backend automatically.
* Do not commit real credentials or local environment files.
* If source markup changes, update saved fixtures and parser tests before enabling live mode again.

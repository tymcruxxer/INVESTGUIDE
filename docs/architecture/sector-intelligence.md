# Sector Intelligence Engine

Sprint 051 adds deterministic Sector and Industry Intelligence to InvestGuide. The layer helps users move from single-company research into market-structure learning: macro economy -> sector -> industry -> company -> financial statements -> dividends -> research.

## Purpose

Sector Intelligence answers:

* What is this sector?
* Which industries and companies belong here?
* Why does this sector matter?
* Which macro factors usually affect it?
* What risks and opportunities are common?
* What should the user learn next?

It is educational research only. It does not forecast, rank companies, recommend investments, or provide financial advice.

## Data Flow

Sector and industry reference data follows the verified data pipeline:

```text
External Source
  -> Source Adapter
  -> Normalizer
  -> Validator
  -> Importer
  -> Database
  -> Sector Intelligence
  -> Company/Macro Research
  -> Frontend
```

The frontend consumes backend sector APIs. It does not hardcode sector taxonomies. Development Preview data appears only when verified sector data is unavailable and development fixture policy allows it.

## Persisted Models

`sectors` stores sector reference data:

* name and slug
* description and overview
* exchange coverage
* country
* source name/type/URL
* imported and verified timestamps
* verification status
* dataset version and external key
* development-data flag
* timestamps

`industries` stores industry reference data linked to `sectors.id` with the same provenance fields.

Existing `companies.sector` and `companies.industry` string fields remain unchanged for backward compatibility. Services resolve relationships by normalized sector/industry names until a future migration adds stricter foreign keys.

## Precedence

Sector data follows the existing precedence:

1. Verified imported data
2. Validated manual data
3. Development Preview data
4. Unavailable

Slugs are indexed but not unique, so a verified row can coexist with and supersede a development preview row.

## Engine

`backend/app/services/intelligence/sector_engine.py` provides:

* sector research
* industry research
* company sector summaries
* macro relationships
* related sectors
* related companies
* knowledge graph paths
* Learn Next topics
* deterministic cache clearing

The engine reuses Macro Intelligence mappings so macro pages, sector pages, and company pages explain relationships consistently.

## APIs

Read-only endpoints:

* `GET /api/v1/sectors`
* `GET /api/v1/sectors/{slug}`
* `GET /api/v1/sectors/{slug}/research`
* `GET /api/v1/industries`
* `GET /api/v1/industries/{slug}`
* `GET /api/v1/industries/{slug}/research`

## Frontend

Frontend surfaces:

* `/sector/[slug]`
* `/industry/[slug]`
* Company page Sector Intelligence panel
* Macro page affected-sector links

All pages display data origin, Development Preview labels where applicable, source transparency, Learn Next topics, and the educational/not-advice boundary.

## Limitations

* Sector and industry rows are currently development preview fixture data.
* No live ZSE/VFEX sector taxonomy connector exists.
* No forecasts, predictions, rankings, recommendations, watchlists, alerts, or LLM outputs were added.
* Company-sector mapping still uses current company metadata strings for compatibility.

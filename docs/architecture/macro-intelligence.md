# Macro Intelligence Engine

Sprint 050 adds deterministic macroeconomic intelligence to InvestGuide. The layer explains economic indicators, company impacts, sector sensitivities, related companies, knowledge graph paths, and Learn Next topics without forecasting, predictions, LLMs, buy/sell language, or personalized financial advice.

## Purpose

Macro Intelligence answers five questions:

* What does this indicator mean?
* Why should investors care?
* Which companies and sectors are typically affected?
* How does the relationship work?
* What should the user learn next?

## Data Flow

Macro data follows the verified data pipeline:

```text
External Source
  -> Source Adapter
  -> Normalizer
  -> Validator
  -> Importer
  -> Database
  -> Macro Intelligence
  -> Research Engine
  -> Frontend
```

The frontend never depends on hardcoded macro values. Development fixtures are visible only when verified rows are unavailable and development fixture policy permits them.

## Persisted Model

`macro_indicators` stores all current macro families with shared provenance fields:

* inflation
* interest rates
* exchange rates
* GDP
* commodity prices

Each row stores value, unit, reporting period, country, optional currency, optional commodity, source name/type/URL, imported timestamp, verified timestamp, verification status, dataset version, external key, development-data flag, and timestamps.

## Development Data Precedence

Macro retrieval follows this precedence:

1. Verified or non-development persisted backend data
2. Validated/manual imported data
3. Development Preview fixture rows
4. Unavailable

Development rows never override verified rows.

## Intelligence Architecture

`backend/app/services/intelligence/macro_engine.py` provides:

* macro research by indicator family
* company macro impact reasoning
* sector macro sensitivity mapping
* related company mapping
* macro knowledge graph paths
* Learn Next topics
* deterministic cache helpers

The engine is rule-based and evidence-based. It explains relationships such as:

```text
Inflation -> Consumer purchasing power -> Consumer Staples -> Delta -> Margins -> Cash flow -> Dividend capacity
```

## API Surface

Read-only endpoints:

* `GET /api/v1/macro`
* `GET /api/v1/macro/inflation`
* `GET /api/v1/macro/interest-rates`
* `GET /api/v1/macro/exchange-rates`
* `GET /api/v1/macro/gdp`
* `GET /api/v1/macro/commodities`
* `GET /api/v1/macro/{type}/research`
* `GET /api/v1/macro/company/{ticker}`

## Frontend

Frontend macro pages live at `/macro/[type]` and display overview, current value, evidence, provenance, explanation, affected sectors, affected companies, knowledge graph, and Learn Next topics. Company pages display a Macro Factors panel using `/api/v1/macro/company/{ticker}`.

## Limitations

* Macro fixture values are development preview data, not verified live RBZ/ZIMSTAT/ZSE/VFEX values.
* No live APIs, scraping, schedulers, or source connectors were added.
* Macro impact is deterministic relationship mapping, not forecasting.
* Sector pages are not implemented yet, but the sector impact service is reusable for future pages.

# Data Source Registry Architecture

## Purpose

Sprint 054 introduces the Data Source Registry as the configuration operating system for all future InvestGuide ingestion sources. It does not run live ingestion, scraping, schedulers, queues, or background workers.

Every external source should be configurable, inspectable, versioned, secured, and auditable before an ingestion engine consumes it.

## Lifecycle

```text
Proposed Source
  -> Registry Entry
  -> Connector Configuration
  -> Credential Metadata
  -> Trust + Provenance Rules
  -> Enabled / Disabled / Maintenance
  -> Future Ingestion Engine Consumption
```

Deletion is soft deletion. Registry rows remain available for provenance and historical audit chains.

## Trust Hierarchy

* `tier_1`: verified primary sources, default confidence `1.0`.
* `tier_2`: verified supporting sources, default confidence `0.85`.
* `tier_3`: intelligence sources, default confidence `0.7`.

Tier is not a recommendation signal. It informs provenance confidence and future evidence weighting.

## Normalized Model

The registry uses four normalized tables:

* `sources`: identity, category, tier, organization, connector type, authentication type, and operational status.
* `source_configurations`: base URL, headers, parser settings, connector config, refresh policy, timeout, retries, rate limits, freshness window, trust configuration, parser version, and connector version.
* `source_credentials`: credential metadata and encrypted/hashed secret placeholder fields. Secret values are never returned through APIs.
* `source_versions`: append-only configuration change history with actor, reason, previous values, new values, timestamp, and request id.

## Categories

Supported categories:

* market
* government
* regulator
* company
* research
* news
* international
* commodity
* currency
* weather
* alternative intelligence
* ESG
* corporate registry

## Connector Model

Supported connector types:

* REST API
* RSS
* Website
* HTML Scraper
* PDF
* CSV
* JSON
* XML
* Manual Upload
* Database
* Future Connector

Supported authentication types:

* None
* API Key
* OAuth
* Username/Password
* Token
* Cookie
* Custom

## Operational Settings

Each source can define:

* enabled, disabled, maintenance, or deleted status;
* manual, hourly, daily, weekly, monthly, or future custom cron refresh policy;
* timeout;
* retry count;
* rate limit;
* backoff policy;
* freshness window.

## Security

Admin APIs never return raw credential values. Credential responses include metadata only:

* key;
* label;
* secret type;
* optional external secret reference;
* configured/unconfigured state;
* masked value.

Development seeds may create mock secret references, not real credentials. Production credentials must be provided through secure operator workflows in future sprints.

## Audit and Versioning

Every create, update, status change, and soft delete records:

* actor;
* action;
* target source;
* reason;
* previous values;
* new values;
* timestamp;
* request id when provided.

Audit records are stored in `audit_logs`; source-specific version history is stored in `source_versions`.

## Admin APIs

* `GET /api/v1/admin/sources`
* `GET /api/v1/admin/sources/{id}`
* `POST /api/v1/admin/sources`
* `PATCH /api/v1/admin/sources/{id}`
* `PATCH /api/v1/admin/sources/{id}/status`
* `DELETE /api/v1/admin/sources/{id}`

The endpoints require existing JWT authentication and RBAC permissions:

* `sources.read` for inspection.
* `sources.update` for create, update, status changes, and soft deletion.

## Development Catalogue

The manual development seed now registers source examples for:

* ZSE, VFEX, RBZ, ZIMSTAT, SECZ, Ministry of Finance, IPEC, CDC;
* IH Securities, MMC Capital, Morgan & Co, Old Mutual Research, ABC Stockbrokers;
* Herald, NewsDay, Zimbabwe Independent, Business Weekly, Chronicle;
* IMF, World Bank, AfDB, UNCTAD;
* Commodity Prices, Weather, Google Trends, Social Sentiment.

## Future Ingestion Integration

Future ingestion engines should consume the registry instead of hardcoding source settings. The registry is designed to feed:

```text
Source Registry
  -> Connector Adapter
  -> Normalizer
  -> Validator
  -> Importer
  -> Database
  -> Research Engines
  -> Frontend
```

## Explicit Non-Goals

Sprint 054 does not implement live scraping, live APIs, scheduled jobs, background workers, queue processing, ingestion pipeline execution, analytics, feature flags, or AI provider management.

## Pre-Sprint 055 Enhancement: Operational Capability Metadata

Sources now declare `supported_capabilities` so future ingestion jobs can discover what each source can provide without hard-coded source logic. Supported capability values include market prices, corporate actions, dividends, annual reports, interim reports, trading updates, news, economic indicators, exchange rates, commodity prices, weather, and research reports.

This field belongs to the source identity because it describes what the source can provide, while connector configuration describes how the source is accessed.

Future Connector Registry:

```text
Source
  -> Connector
  -> Parser
  -> Ingestion Job
```

A Connector Registry should be introduced later so multiple sources can reuse the same connector implementation, such as a shared Website Connector for company investor-relations pages.

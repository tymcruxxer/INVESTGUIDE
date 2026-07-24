# Connector Registry Architecture

Sprint 056 establishes the Connector Registry as the reusable execution-contract layer for future verified data ingestion.

## Purpose

Sources describe where data comes from. Jobs describe when work should happen. Connectors describe how future workers will perform the work.

This registry is intentionally metadata-only. It does not perform HTTP requests, scraping, RSS fetching, parsing, scheduling, queue execution, browser automation, or AI processing.

## Core Flow

```text
Data Source
  -> Connector
  -> Future Parser
  -> Future Ingestion Job
  -> Database
  -> Research Engines
  -> Frontend
```

Multiple data sources can reference the same connector, allowing reusable implementations such as Generic REST API, Generic RSS Feed, Generic HTML Scraper, Generic PDF Extractor, and Generic CSV Importer.

## Data Model

The backend defines normalized connector tables:

* `connectors` - identity, type, lifecycle, version, vendor, author, classification, auth strategy, schema metadata, compatibility notes, and soft-archive fields.
* `connector_capabilities` - extensible capability declarations such as market prices, dividends, reports, news, macro indicators, currency rates, commodities, weather, research, and ESG data.
* `connector_configuration_schemas` - configuration contract metadata such as base URL fields, endpoint templates, allowed headers, parser identifier, timeout, retry, pagination, rate limit, compression, request method, and user agent.
* `connector_versions` - immutable version history with previous/new snapshots, actor, compatibility notes, change summary, and request ID.
* `connector_validations` - structured metadata validation results.
* `sources.connector_id` - nullable source binding so existing sources remain backward compatible.

## Lifecycle

Supported lifecycle states:

* Draft
* Active
* Deprecated
* Disabled
* Archived

Archived connectors are soft-deleted from normal registry lists but retain version history, validations, source references, and audit trail.

## Capability Model

Capabilities declare what a connector can support. They do not execute ingestion.

Initial capabilities include market prices, company filings, annual reports, interim reports, trading updates, corporate actions, dividends, news, macroeconomic indicators, currency rates, commodity prices, weather, research reports, and ESG data.

Future ingestion jobs should select connectors and sources by capability instead of hard-coded source names.

## Configuration Contracts

Connector configuration schemas store metadata only. They may describe secret references, but they must not store raw secrets or secret-bearing fields such as passwords, tokens, private keys, or credential values.

Configuration contracts can include:

* Base URL field requirements
* Endpoint templates
* Header schema
* Authentication strategy
* Timeout and retry policy
* Pagination strategy
* Parser identifier
* Rate limit policy
* User agent
* Compression
* Request method

## Authentication Strategy Contracts

Supported strategies:

* None
* API Key
* Bearer Token
* OAuth 2.0
* Username/Password
* Cookie
* Custom

No authentication flows are implemented. Future secure credential storage and auth adapters must consume these contracts without exposing secrets.

## Validation Framework

Connector validation checks metadata only:

* Required configuration fields
* Lifecycle state
* Compatible authentication strategy
* Compatible source category
* Configuration schema integrity
* Secret-boundary safety

Validation never performs outbound network requests and never tests live connectivity.

## Admin APIs

Secure RBAC-protected endpoints:

* `GET /api/v1/admin/connectors`
* `GET /api/v1/admin/connectors/capabilities`
* `GET /api/v1/admin/connectors/{id}`
* `POST /api/v1/admin/connectors`
* `PATCH /api/v1/admin/connectors/{id}`
* `POST /api/v1/admin/connectors/{id}/validate`
* `PATCH /api/v1/admin/connectors/{id}/status`

Permissions:

* `connectors.read`
* `connectors.update`

## Admin Frontend

Admin UI routes:

* `/admin/connectors`
* `/admin/connectors/[id]`

The UI shows connector identity, version, type, lifecycle, capabilities, compatible sources, configuration schema, auth strategy, version history, validation results, and lifecycle controls.

## Seed Workflow

The manual development seed command now seeds reusable connector definitions and binds seeded sources:

```bash
cd backend
python -m app.database.seed
```

Seeded connectors:

* Generic REST API Connector
* Generic RSS Feed Connector
* Generic HTML Scraper Connector
* Generic PDF Extractor Connector
* Generic CSV Importer Connector

No real credentials or live execution are seeded.

## Future Execution Integration

Future ingestion workers should read the Connector Registry, then instantiate a connector implementation based on connector type, parser identifier, source binding, capability, and configuration contract.

Deferred future work:

* Connector implementation registry
* Parser registry
* Secure secret manager integration
* Live connectivity testing
* Worker execution engine
* Scheduler and queue integration
* Connector health checks
* Runtime metrics from real executions

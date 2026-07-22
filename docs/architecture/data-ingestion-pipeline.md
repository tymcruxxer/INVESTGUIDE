# Verified Data Pipeline Framework

Sprint 047 establishes the source-agnostic ingestion architecture for verified and curated financial data.

The pipeline is intentionally not a live connector sprint. It does not scrape websites, call ZSE/VFEX APIs, ingest production documents automatically, or expose a public ingestion API.

## Purpose

InvestGuide needs one reusable path for all future structured data:

```text
External Source
  -> Source Adapter
  -> Normalizer
  -> Validator
  -> Importer
  -> Database
  -> Deterministic Research Engines
  -> Frontend
```

The frontend and intelligence engines should not know whether data came from ZSE, VFEX, CSV, JSON, annual reports, APIs, or manual curation.

## Source Adapters

Current adapters are local-only:

* JSON source adapter
* CSV source adapter

They load files from disk, compute checksums, record source name/type, dataset version, record count, import timestamp, and development-data status.

Future adapters may wrap ZSE, VFEX, annual reports, company filings, APIs, or admin uploads, but they must return the same `LoadedDataset` contract.

## Source Metadata

Every run records:

* source name
* source type
* source URL or local file path
* document date where available
* imported timestamp
* verified timestamp where available
* verification status
* dataset version
* checksum
* record count
* development-data flag

## Verification States

Supported states:

* Unverified
* Validated
* Verified
* Rejected
* Development

Development fixture rows are allowed only when the backend development-data policy permits them.

## Normalization

Normalizers convert source-specific fields into canonical records. Current runtime normalizers cover:

* Company
* Income Statement
* Dividend
* News

The shared normalized contracts also define future shapes for assets, company profiles, balance sheets, cash flow statements, corporate actions, and market snapshots.

Normalization helpers standardize:

* ticker symbols
* exchange names
* currencies
* dates
* datetimes
* decimal values
* URLs
* company names
* statement periods
* dividend types
* corporate action types
* whitespace and UTF-8 BOM handling

## Validation

Validators return structured results instead of failing late:

* valid records
* warnings
* rejected records
* field-level validation issues

Strict mode rejects the full batch when any record is invalid. Lenient mode imports valid records and skips rejected records. Dry-run mode validates and plans without entity writes.

## Import Modes

* `dry_run`: default; writes only an audit run, not entity rows.
* `lenient`: imports valid records, skips rejected records.
* `strict`: rejects the batch if any record fails validation.

Importers are transactional and idempotent. They upsert by deterministic identity and existing model uniqueness constraints.

## Precedence

Verified or non-development persisted records must not be overwritten by lower-quality development records.

Data-origin precedence remains:

1. Verified live/imported data
2. Verified manually curated data
3. Development fixture data
4. Unavailable

## Audit

`ingestion_runs` records pipeline executions without storing raw source documents. It stores source metadata, mode, status, counts, warnings, errors, and timestamps.

## CLI

Example:

```bash
cd backend
python -m app.services.ingestion.cli --entity companies --source-file tests/fixtures/ingestion/companies.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
```

The CLI supports:

* entity
* source file
* source name
* source type
* mode
* dataset version
* strict validation
* development-data flag

## Current Runtime Entities

Sprint 047 validates the pipeline with persisted entities that already exist:

* companies
* income statements
* dividends
* news

No frontend contracts changed.

## Future Extension Points

Future sprints can add:

* ZSE source adapter
* VFEX source adapter
* annual report parser
* company filing importer
* verified balance sheet/cash flow importers
* corporate action importer
* admin upload flow
* operator dashboard

These should plug into the same Source Adapter -> Normalizer -> Validator -> Importer flow.

---

## Sprint 048 Verified Data Ingestion Completion

Sprint 048 completes the source-agnostic verified data ingestion framework for the current persisted financial intelligence layer. The framework remains backend-only and does not add live ZSE/VFEX connectors, scraping, schedulers, public ingestion APIs, AI, predictions, recommendations, or frontend source-specific branching.

Runtime ingestion entities now include:

* companies
* assets
* company profiles
* income statements
* balance sheets
* cash flow statements
* dividends
* corporate actions
* news
* market snapshots

Market snapshots provide verified or development reference prices for deterministic engines. Dividend Intelligence can now use the latest acceptable market snapshot as a reference price when calculating historical dividend-yield availability. The frontend continues to consume existing APIs and does not need to know whether data originated from JSON, CSV, future ZSE/VFEX connectors, annual reports, APIs, or manual curation.

Recovery and re-run behavior:

* Dry-run validates and records audit metadata without entity writes.
* Lenient mode imports valid records, rejects invalid rows, and records warnings.
* Strict mode rejects the full batch when any row is invalid.
* Idempotent importers upsert by deterministic identity.
* Lower-quality development fixture rows do not overwrite verified or non-development persisted rows.
* SQLAlchemy errors roll back the active transaction and surface through the pipeline result.

Sprint 048 example commands:

```bash
cd backend
python -m app.services.ingestion.cli --entity assets --source-file tests/fixtures/ingestion/assets.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity company_profiles --source-file tests/fixtures/ingestion/company_profiles.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity balance_sheets --source-file tests/fixtures/ingestion/balance_sheets.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity cash_flow_statements --source-file tests/fixtures/ingestion/cash_flow_statements.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity corporate_actions --source-file tests/fixtures/ingestion/corporate_actions.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity market_snapshots --source-file tests/fixtures/ingestion/market_snapshots.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
```

---

## Sprint 049 Addendum

Sprint 049 adds operator observability to the verified ingestion pipeline. Internal operations documentation is available at `docs/operations/data-quality-and-ingestion-operations.md`.

Key additions:

* `ingestion_record_issues` persistence.
* Stable issue codes.
* Data-quality scoring and source health.
* Internal read-only APIs.
* Internal data operations dashboard and run detail pages.
* Diagnostics CLI and safe rejection export.

Validation recorded:

* Backend tests: 247 passed.
* Frontend lint: passed.
* Frontend type-check: passed.
* Frontend build: passed, 15 routes.
* Runtime smoke: internal APIs and internal pages passed.

## Sprint 050 Macro Ingestion Addendum

Sprint 050 adds `macro_indicators` to the verified data pipeline. Macro data now follows the same Source Adapter -> Normalizer -> Validator -> Importer -> Database -> Intelligence -> Frontend flow as companies, assets, financial statements, dividends, corporate actions, news, and market snapshots.

Macro development fixtures are local JSON only. They are marked as Development Preview, are guarded by the development-data policy, and never override verified/non-development rows.

## Sprint 051 Sector and Industry Entity Support

Sprint 051 extends the verified data ingestion framework with reference-data support for `sectors` and `industries`.

Pipeline coverage:

* `NormalizedSector` and `NormalizedIndustry` contracts.
* Sector and industry normalizers for source rows.
* Validators for required names, slugs, parent-sector linkage, source metadata, and development-data flags.
* Importers that upsert by slug/source semantics and preserve verified data precedence.
* Registry entries for `EntityType.SECTORS` and `EntityType.INDUSTRIES`.
* Fixture coverage in `backend/tests/fixtures/ingestion/sectors.json` and `backend/tests/fixtures/ingestion/industries.json`.

The frontend and research engines continue to read from backend APIs only; they do not know whether sector data came from JSON fixtures, future verified imports, manual curation, or future admin workflows.

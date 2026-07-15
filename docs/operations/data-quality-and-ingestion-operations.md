# Data Quality and Ingestion Operations

Sprint 049 adds an internal observability layer for InvestGuide's verified data pipeline. It is designed for operators and developers, not public investor users.

## Purpose

Before live ZSE/VFEX connectors are added, operators must be able to answer:

* Did the data arrive?
* Was it valid?
* What changed?
* What failed?
* Why did it fail?
* Is the source healthy?
* Is the dataset fresh?
* Is verified data replacing development fixtures?
* What action should be taken next?

## Ingestion Issue Codes

Stable issue codes are defined in `app.services.ingestion.types.IssueCode`.

Current codes include:

* `MISSING_REQUIRED_FIELD`
* `INVALID_TICKER`
* `INVALID_EXCHANGE`
* `INVALID_CURRENCY`
* `INVALID_DATE`
* `INVALID_DECIMAL`
* `UNKNOWN_COMPANY`
* `UNKNOWN_ASSET`
* `DUPLICATE_EXTERNAL_KEY`
* `LOWER_PRECEDENCE_SKIPPED`
* `DEVELOPMENT_DATA_BLOCKED`
* `BALANCE_SHEET_IMBALANCE`
* `CASH_FLOW_MISMATCH`
* `DIVIDEND_DATE_WARNING`
* `INVALID_PRICE_RANGE`
* `MISSING_SOURCE_METADATA`
* `VERIFICATION_METADATA_MISSING`
* `STRICT_BATCH_ABORTED`
* `DATABASE_WRITE_FAILED`
* `VALIDATION_ERROR`
* `IMPORT_WARNING`
* `IMPORT_ERROR`

Record-level issues are stored in `ingestion_record_issues` and linked to `ingestion_runs`. Only concise safe summaries are persisted; raw source documents, passwords, tokens, and confidential payloads must not be stored.

## Scoring Methodology

Data quality uses deterministic 0-100 score components:

* Completeness: required-field presence by entity.
* Validity: rejection issue burden.
* Provenance: source metadata, timestamps, verification state, and development-data status.
* Freshness: latest update compared with centralized target days.
* Consistency: warning issue burden.
* Overall: average of component scores.

Labels:

* Excellent
* Strong
* Good
* Moderate
* Weak
* Critical

Every score includes reasons. Missing evidence lowers scores instead of being hidden.

## Freshness Targets

Defaults live in `backend/app/services/data_quality/freshness.py`.

* Market snapshots: 1 day
* News: 1 day
* Company profiles: 90 days
* Companies: 90 days
* Assets: 90 days
* Financial statements: 365 days
* Dividends: 365 days
* Corporate actions: 365 days

Development fixture data is never marked as fresh production data.

## Provenance

Provenance labels align with existing data-origin precedence:

* Verified Source
* Validated Import
* Manual Curated
* Development Preview
* Unknown

Development rows are capped below full production provenance credit.

## Internal APIs

Read-only, development-guarded endpoints:

* `GET /api/v1/internal/ingestion/runs`
* `GET /api/v1/internal/ingestion/runs/{run_id}`
* `GET /api/v1/internal/ingestion/runs/{run_id}/issues`
* `GET /api/v1/internal/ingestion/sources`
* `GET /api/v1/internal/data-quality/summary`
* `GET /api/v1/internal/data-quality/entities/{entity_type}`
* `GET /api/v1/internal/data-quality/companies/{ticker}`

Until admin roles exist, these endpoints are available only in development/debug environments.

## Internal Dashboard

Frontend pages:

* `/internal/data-operations`
* `/internal/data-operations/runs/[id]`

The dashboard shows pipeline health, latest runs, source health, entity quality, development-data visibility, and rejection filtering. The run detail page shows run metadata, issue-code distribution, retry guidance, and safe issue details.

## Diagnostics CLI

Examples:

```bash
cd backend
python -m app.services.ingestion.diagnostics runs
python -m app.services.ingestion.diagnostics sources
python -m app.services.ingestion.diagnostics quality --format json
python -m app.services.ingestion.diagnostics company DLTA --format json
python -m app.services.ingestion.diagnostics issues --run-id 23 --format csv
python -m app.services.ingestion.diagnostics issues --run-id 23 --format csv --output rejected-run-23.csv
```

## Rejection Export

CSV/JSON rejection exports include only:

* run ID
* record index
* entity type
* external key
* severity
* issue code
* field name
* safe message

They do not export raw source documents or raw-value summaries.

## Development Data Visibility

The dashboard and quality summary show verified, development, and unverified record counts. Development rows are clearly identified so operators can decide when to run the existing cleanup workflow:

```bash
python -m app.database.cleanup_development_data --dry-run
python -m app.database.cleanup_development_data --confirm
```

No automatic cleanup is performed.

## Known Limitations

* No live ZSE/VFEX connectors exist yet.
* No admin RBAC exists yet; internal APIs are development/debug guarded.
* No public ingestion write endpoints exist.
* The dashboard is an internal operator surface and is not linked from public investor navigation.
* Quality scores are deterministic heuristics for operations, not financial-health or investment scores.

## Recommended Sprint 050

Harden operator access and add either admin-role protection for internal operations or one controlled live-source adapter only after source health, issue reporting, and provenance visibility have been reviewed.

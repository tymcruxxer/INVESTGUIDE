# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides application setup, environment-based configuration, logging, middleware, database session wiring, SQLAlchemy base metadata conventions, Alembic migration scaffolding, response envelope helpers, exception handlers, API versioning, a health endpoint, the investment asset domain model layer, read-only asset API routes, a manual development asset seed command, and the news intelligence foundation with read-only news routes, persisted content hashes for scalable duplicate detection, and a JWT authentication foundation with user-owned investor profiles.

Business features such as asset/news write endpoints, analytics, AI, production notifications, production deployment, portfolio tracking, watchlists, payments, and frontend personalization are intentionally not implemented yet.

## Requirements

* Python 3.12+
* Docker Desktop or another Docker Compose compatible runtime for reproducible local PostgreSQL
* PostgreSQL for hosted/manual migration execution, seeding, and live database-backed asset endpoints

## Install

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Configure Environment

Create a local environment file from the example:

```bash
copy .env.example .env
```

Environment variables:

* `APP_NAME` - FastAPI application name
* `APP_VERSION` - application version, currently `0.1.0-alpha`
* `APP_ENV` - runtime environment, such as `development`
* `APP_DEBUG` - FastAPI debug flag
* `LOG_LEVEL` - logging level
* `DATABASE_URL` - SQLAlchemy database URL
* `CORS_ORIGINS` - comma-separated allowed origins or a JSON array string
* `INGESTION_MODE` - internal ingestion adapter mode, `DRY_RUN` or `WRITE`; defaults to `DRY_RUN`
* `JWT_SECRET_KEY` - JWT signing secret; use the development value locally only and replace in deployed environments
* `JWT_ALGORITHM` - JWT signing algorithm, default `HS256`
* `ACCESS_TOKEN_EXPIRE_MINUTES` - access token lifetime in minutes

Do not commit real database passwords or hosted database credentials.

## One-Command Development Launcher

Sprint 017.1 adds a single backend development entry point. From the repository root, run:

```bash
python backend/scripts/dev.py --port 8001
```

The launcher:

* verifies Docker is installed and the Docker daemon is running
* starts `docker compose up -d` unless `--skip-docker` is provided
* waits for PostgreSQL to accept the configured backend connection
* runs the existing backend bootstrap unless `--skip-bootstrap` is provided
* starts FastAPI with Uvicorn unless `--no-server` is provided
* prints a clear status summary

Available flags:

* `--no-server` - prepare Docker/database state but do not start FastAPI
* `--port 8001` - choose the Uvicorn port
* `--skip-docker` - assume the database already exists and do not start Docker Compose
* `--skip-bootstrap` - do not apply migrations or seed development assets

Safety notes:

* the launcher never prints database credentials
* it does not delete volumes, reset databases, or run destructive commands
* it does not enable WRITE ingestion mode
* it does not start schedulers, scrapers, live scraping, AI, or analytics jobs

Common errors:

* `Docker is not installed or not available on PATH` - install Docker Desktop or another Docker Compose runtime
* `Docker daemon is not running` - start Docker Desktop or your Docker service
* `PostgreSQL did not become reachable` - check Docker health, host port `5433`, and `backend/.env`
## Docker Compose Development Database

Sprint 017 standardizes the local development database with Docker Compose.

From the repository root:

```bash
docker compose up -d
```

This starts PostgreSQL 16 with:

* database: `investguide`
* user: `investguide_user`
* password: `investguide_password`
* host port: `5433`
* named volume: `investguide_postgres_data`

Copy the backend environment example:

```powershell
Copy-Item backend\.env.example backend\.env
```

The default development URL is:

```text
DATABASE_URL=postgresql+psycopg://investguide_user:investguide_password@localhost:5433/investguide
```

Do not commit `.env` or real hosted credentials.

## Bootstrap Local Development

After starting Docker Compose, prepare the backend database from the repository root:

```bash
python backend/scripts/bootstrap_dev.py
```

The bootstrap script waits for PostgreSQL, verifies the connection, applies Alembic migrations, runs the development asset seed command, and prints a summary.

Check the database at any time:

```bash
python backend/scripts/check_database.py
```

The diagnostics command checks database reachability, credentials, migration status, seed data presence, and asset count. It exits non-zero when a critical check fails.

## Manual or Hosted PostgreSQL Setup

For hosted PostgreSQL providers such as Supabase, Neon, Railway, or Render:

1. Create a PostgreSQL database in the provider dashboard.
2. Copy the provider connection string.
3. Ensure the URL uses the SQLAlchemy psycopg driver format: `postgresql+psycopg://...`.
4. Store the full value in `.env` as `DATABASE_URL`.
5. Keep SSL options from the provider if required by the connection string.

Example shape only:

```bash
DATABASE_URL=postgresql+psycopg://user:password@host:5432/database
```

## Run Migrations

Alembic is configured under `backend/alembic` and uses `DATABASE_URL` from application settings.

Check current revision:

```bash
python -m alembic current
```

Apply all migrations:

```bash
python -m alembic upgrade head
```

Create a migration after models change:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Rollback one migration:

```bash
python -m alembic downgrade -1
```

If PostgreSQL is not available or credentials are not configured, `python -m alembic current` will load the Alembic environment and report that revision lookup is deferred. Migration execution requires a working PostgreSQL connection.

## Seed Development Assets

Development asset seed data is defined in `app/database/seed_assets.py` and is inserted only when explicitly requested.

Run migrations first:

```bash
python -m alembic upgrade head
```

Then run the manual seed command:

```bash
python -m app.database.seed
```

The seed command:

* connects using the configured `DATABASE_URL`
* inserts assets from `seed_assets.py`
* skips existing tickers to avoid duplicates
* logs inserted and skipped tickers
* does not run on application startup

If `DATABASE_URL` is not configured or the assets table has not been migrated, real seed execution will fail until the database is ready.

## Authentication Foundation

The backend now includes a basic JWT identity layer for future personalization, watchlists, portfolios, alerts, and learning progress.

Implemented endpoints:

* `POST /api/v1/auth/signup` - creates a user with a bcrypt-hashed password and returns `user`, `access_token`, and `token_type`
* `POST /api/v1/auth/login` - verifies email/password credentials and returns `access_token`, `token_type`, and `user`
* `GET /api/v1/auth/me` - returns the authenticated user from a bearer token

JWT tokens include:

* `sub` - authenticated user id
* `email` - authenticated user email
* `exp` - token expiry

## Asset Assessment Endpoint

Sprint 029 adds a deterministic assessment API for persisted asset details. The new endpoint returns structured, non-advisory assessment metadata based on existing asset profile fields only.

Endpoint:

* `GET /api/v1/assets/{ticker}/assessment`

Response shape includes:

* `ticker`
* `overall_assessment`
* `evidence_strength`
* `investment_horizon`
* `key_strengths`
* `things_to_watch`
* `educational_summary`
* `explain_like_im_18`
* `generated_at`
* `assessment_version`

This endpoint is deterministic and intentionally avoids AI or predictive investment recommendations. It is designed to provide educational context derived from structured asset metadata.

Authentication logic lives in `app/services/auth_service.py`. Future protected routes should use `Depends(get_current_user)`. The backend currently supports a single basic user identity model only; it does not implement roles, RBAC, email verification, OAuth, MFA, sessions, or social login.

Passwords are never stored in plaintext. The backend uses `passlib` with bcrypt for password hashing and `python-jose` for JWT encode/decode.
## Run API

```bash
uvicorn app.main:app --reload
```

If port `8000` is already occupied by another local process, use an alternate port for development smoke tests:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response shape:

```json
{
  "success": true,
  "message": "Backend is healthy",
  "data": {
    "status": "ok",
    "database": "connected",
    "migrations": "current",
    "environment": "development",
    "version": "0.1.0-alpha"
  }
}
```

If PostgreSQL is unavailable, the endpoint still reports FastAPI liveness with `database: "unavailable"` and `migrations: "unavailable"`; it does not expose credentials.

## Asset Read API

Read-only asset endpoints are available under `/api/v1/assets`:

* `GET /api/v1/assets` - list assets with optional filters and pagination
* `GET /api/v1/assets/{ticker}` - retrieve one asset by ticker

Supported list filters:

* `exchange`: `ZSE`, `VFEX`
* `sector`: case-insensitive exact sector match
* `asset_type`: `equity`, `REIT`, `bond`, `money_market`, `alternative`
* `status`: `active`, `suspended`, `delisted`
* `search`: matches ticker, company name, sector, or industry
* `page`: defaults to `1`
* `limit`: defaults to `20`, maximum `100`

List response shape:

```json
{
  "success": true,
  "message": "Assets retrieved successfully",
  "data": [],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 0,
    "has_next": false
  }
}
```

Missing ticker response shape:

```json
{
  "success": false,
  "message": "Asset 'DLTA' was not found",
  "error_code": "ASSET_NOT_FOUND",
  "details": {}
}
```

No create, update, delete, price, dividend, analytics, AI, or scraper endpoints exist yet.

## News Read API

Read-only news endpoints are available under `/api/v1/news`:

* `GET /api/v1/news` - list investment news with optional filters, date sorting, and pagination
* `GET /api/v1/news/{id}` - retrieve one news article by id

Supported list filters:

* `source`: case-insensitive exact source match
* `asset`: related asset ticker, such as `DLTA` or `ECO`
* `search`: matches title, summary, content, source, or author
* `sort`: `desc` or `asc` by published date, defaults to `desc`
* `page`: defaults to `1`
* `limit`: defaults to `20`, maximum `100`

If the configured PostgreSQL database is unavailable, the service falls back to clearly marked development sample articles from `app/database/seed_news.py`. This fallback exists only so the foundation API can be exercised before scraper ingestion and database setup are complete.

List response shape:

```json
{
  "success": true,
  "message": "News retrieved successfully",
  "data": [],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 0,
    "has_next": false,
    "source": null,
    "asset": null,
    "sort": "desc"
  }
}
```

Missing article response shape:

```json
{
  "success": false,
  "message": "News article '999' was not found",
  "error_code": "NEWS_NOT_FOUND",
  "details": {}
}
```

No news create, update, delete, scraper, AI, sentiment-analysis, summarization, embedding, or RAG endpoints exist yet.

## News Intelligence Foundation

The news foundation is implemented for future scraper and AI modules:

* SQLAlchemy model: `app/models/news.py`
* Asset-news association table: `app/models/associations.py`
* Pydantic schemas: `app/schemas/news.py`
* Read-only service: `app/services/news_service.py`
* Read-only routes: `app/api/v1/news.py`
* Development sample data: `app/database/seed_news.py`
* Alembic migration: `alembic/versions/20260625_0002_create_news_articles_table.py`
* Content hash migration: `alembic/versions/20260625_0003_add_news_content_hash.py`


## Internal News Ingestion Adapter

Sprint 011 adds an internal backend adapter for normalized news ingestion payloads:

* Endpoint: `POST /api/v1/ingestion/news`
* Default behavior: dry-run report only through `INGESTION_MODE=DRY_RUN`
* Optional write behavior: set `INGESTION_MODE=WRITE` or pass request `mode: "WRITE"`
* Duplicate checks: URL, stored indexed `content_hash`, normalized title, and published timestamp where appropriate
* Asset resolution: links active asset tickers, warns for missing or inactive tickers
* Hash ownership: backend generates the canonical SHA-256 `content_hash` before persistence and ignores caller-supplied hashes for stored records
* Transaction handling: each article commits only after validation, duplicate checks, mapping, and relationship resolution; failures roll back the article

This endpoint is intended for internal ingestion workflows only. It accepts normalized backend-compatible payloads, not raw scraper output, and it is not a public user-facing API.

Request shape:

```json
{
  "mode": "DRY_RUN",
  "articles": [
    {
      "title": "Sample normalized article",
      "source": "Financial Gazette",
      "published_at": "2026-06-25T08:00:00Z",
      "summary": "Development summary.",
      "content": "Development article body.",
      "url": "https://example.com/article",
      "language": "en",
      "asset_tickers": ["DLTA"],
      "credibility_score": 0.7,
      "content_hash": "optional-caller-hash-backend-regenerates-before-write"
    }
  ]
}
```

Report fields include `articles_received`, `articles_written`, `duplicates_skipped`, `failed_articles`, `assets_linked`, `execution_time`, `errors`, `warnings`, `mode`, and per-article results. The persisted `news_articles.content_hash` column is fixed-length 64 characters, indexed, unique, and non-nullable.

Automated write-mode coverage uses in-memory SQLite. Live PostgreSQL ingestion requires valid `DATABASE_URL`, applied migrations, and seeded assets.

## Scraper Submission Workflow

Sprint 015 adds a scraper-side backend submission client for controlled internal ingestion.

Scraper command:

```bash
python -m scrapers.run_backend_submission
```

Scraper-side controls:

* `BACKEND_SUBMISSION_MODE=OFF` - default; no backend request is sent.
* `BACKEND_SUBMISSION_MODE=DRY_RUN` - sends `mode: "DRY_RUN"` to `/api/v1/ingestion/news`.
* `BACKEND_SUBMISSION_MODE=WRITE` - requests persistence, but the scraper client downgrades to dry-run unless `SCRAPER_LIVE_ENABLED=true` is also set.
* `BACKEND_URL` - backend base URL, for example `http://localhost:8000`.
* `BACKEND_API_VERSION` - API version path segment, currently `v1`.

Backend-side controls still apply. `INGESTION_MODE` defaults to `DRY_RUN`, and live persistence requires the backend database to be configured, migrations to be applied, assets to be seeded, and the request mode/backend settings to allow writes. The scraper client does not bypass backend validation, duplicate checks, asset resolution, or transaction handling.
### Local DRY_RUN Smoke Validation

To validate scraper submission against a running local backend without enabling writes:

1. Start the backend from `backend/`:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

2. From the repository root, run the PowerShell smoke command:

```powershell
$env:BACKEND_SUBMISSION_MODE='DRY_RUN'; $env:BACKEND_URL='http://127.0.0.1:8001'; python -m scrapers.run_backend_submission_smoke; Remove-Item Env:BACKEND_SUBMISSION_MODE; Remove-Item Env:BACKEND_URL
```

The smoke command checks `/api/v1/health`, builds fixture scraper payloads, and posts to `/api/v1/ingestion/news` with `mode: "DRY_RUN"`. It never uses WRITE mode.

Current local validation reached the ingestion endpoint and received HTTP 200, but article-level validation reported PostgreSQL authentication failure for `investguide_user`. Configure `DATABASE_URL`, apply migrations, and seed assets before expecting full DRY_RUN validation with duplicate and asset checks.
## Asset Domain Foundation

The first domain model layer is implemented for investment assets:

* SQLAlchemy model: `app/models/asset.py`
* Pydantic schemas: `app/schemas/asset.py`
* Read-only service: `app/services/asset_service.py`
* Read-only routes: `app/api/v1/assets.py`
* Development seed data: `app/database/seed_assets.py`
* Manual seed command: `app/database/seed.py`
* Alembic migration: `alembic/versions/20260625_0001_create_assets_table.py`

## Test

```bash
pytest
```

Automated tests use mocks or in-memory SQLite where database behavior is needed, so they do not require live PostgreSQL credentials.

## Investor Profile API

Sprint 020 connects investor profiles to authenticated users while preserving a development-only fallback:

* `GET /api/v1/investor-profile` - returns the authenticated user's profile, or the development profile only when `APP_ENV=development` and no bearer token is supplied
* `POST /api/v1/investor-profile` - creates a profile attached to the authenticated user; in development without auth, creates a fallback development profile
* `PUT /api/v1/investor-profile` - updates the authenticated user's profile; in development without auth, updates the fallback development profile

Production identity rule:

* With a valid bearer token, profile lookup is by `investor_profiles.user_id`.
* Without authentication outside development, the API returns `401 AUTHENTICATION_REQUIRED`.
* The first-row profile fallback exists only to keep local development workflows usable while frontend auth/onboarding remains unimplemented.

The `InvestorProfile.user_id` column now references `users.id` and has a one-profile-per-user uniqueness constraint. Existing development seed behavior remains manual through `python -m app.database.seed`; no profile is created automatically during FastAPI startup.

Authentication is intentionally limited to identity. This sprint does not add AI recommendations, frontend onboarding, dashboards, watchlists, portfolio tracking, payments, notifications, live scraping, or scheduler behavior.

## Investor Personalization Foundation
Sprint 018 adds the backend foundation for investor personalization without adding authentication, frontend onboarding, AI recommendations, or public personalization routes.

Implemented foundation pieces:

* Model: `app/models/investor_profile.py`
* Schemas: `app/schemas/investor_profile.py`
* Service rules: `app/services/personalization_service.py`
* Migration: `alembic/versions/20260626_0004_create_investor_profiles_table.py`
* Product vision: `../docs/product/personalization-and-adaptive-intelligence.md`

The `investor_profiles` table stores:

* nullable `user_id` foreign key to `users.id` for authenticated profile ownership, while still allowing a development fallback profile
* `experience_level`: `beginner`, `intermediate`, `advanced`
* `risk_appetite`: `conservative`, `moderate`, `aggressive`
* `investment_horizon`
* `planned_investment_range`
* `preferred_asset_types`
* `investment_goals`
* `preferred_language_level`
* `education_focus`
* `created_at` and `updated_at`

The personalization service derives presentation settings such as language complexity, metrics visibility, education depth, and explanation style from profile inputs. It does not generate recommendations, call AI services, expose API routes, or perform portfolio/advisory logic.
## Folder Structure

```text
backend/
|-- alembic/
|   |-- versions/
|   |   |-- 20260625_0001_create_assets_table.py
|   |   |-- 20260625_0002_create_news_articles_table.py
|   |   `-- 20260625_0003_add_news_content_hash.py
|   |-- env.py
|   `-- script.py.mako
|-- app/
|   |-- api/
|   |   `-- v1/
|   |       |-- assets.py
|   |       |-- health.py
|   |       |-- ingestion.py
|   |       |-- news.py
|   |       `-- router.py
|   |-- core/
|   |   |-- config.py
|   |   |-- exceptions.py
|   |   |-- logging.py
|   |   |-- middleware.py
|   |   `-- responses.py
|   |-- database/
|   |   |-- base.py
|   |   |-- seed.py
|   |   |-- seed_assets.py
|   |   |-- seed_news.py
|   |   `-- session.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- asset.py
|   |   |-- associations.py
|   |   |-- mixins.py
|   |   `-- news.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- asset.py
|   |   |-- ingestion_report.py
|   |   `-- news.py
|   |-- services/
|   |   |-- asset_resolution_service.py
|   |   |-- asset_service.py
|   |   |-- duplicate_service.py
|   |   |-- ingestion_service.py
|   |   `-- news_service.py
|   |-- utils/
|   `-- main.py
|-- tests/
|   |-- test_asset_model.py
|   |-- test_asset_routes.py
|   |-- test_asset_schema.py
|   |-- test_asset_service.py
|   |-- test_database.py
|   |-- test_health.py
|   |-- test_ingestion_adapter.py
|   |-- test_news_model.py
|   |-- test_news_routes.py
|   |-- test_news_schema.py
|   |-- test_news_service.py
|   |-- test_seed_assets.py
|   `-- test_seed_command.py
|-- .env.example
|-- alembic.ini
|-- README.md
`-- requirements.txt
```





## Sprint 021 Authentication Validation Notes

Sprint 021 validated the authentication foundation and added only focused hardening tests.

Validation summary:

* `python backend/scripts/dev.py --no-server` failed clearly because Docker is not installed or not available on PATH.
* `python backend/scripts/check_database.py` failed because local PostgreSQL rejects `investguide_user` credentials.
* `python -m alembic current` loaded Alembic configuration successfully, but current revision lookup was deferred until PostgreSQL is reachable.
* `python -m pytest` from the repository root passed with 184 tests.
* `python -m uvicorn app.main:app --reload --port 8001` started successfully.
* `GET /api/v1/health` returned a healthy application response with `database: unavailable` and `migrations: unavailable`.
* `GET /api/v1/auth/me` without a bearer token returned a 401 response envelope.
* `POST /api/v1/auth/signup` reached the auth service but could not complete because the configured PostgreSQL credentials are rejected.

Hardening added:

* Expired bearer tokens are covered by automated tests and return 401.
* Inactive users with otherwise valid tokens are covered by automated tests and return 401.

Full authenticated signup/login/profile runtime smoke requires Docker PostgreSQL or corrected local PostgreSQL credentials, followed by migrations and seed data.

## Sprint 023 End-to-End Validation Notes

Sprint 023 started FastAPI successfully on port `8001` and confirmed `/api/v1/health` returns 200 with `database: unavailable` and `migrations: unavailable` while PostgreSQL is blocked.

Database validation results:

* `docker compose up -d` could not run because Docker is not installed or not available on PATH.
* `python backend/scripts/bootstrap_dev.py` failed clearly because local PostgreSQL rejects `investguide_user` credentials.
* `python backend/scripts/check_database.py` failed for the same PostgreSQL authentication reason.
* `python -m alembic current` loads Alembic configuration, but current revision lookup remains deferred until PostgreSQL is reachable.

Runtime endpoint results:

* `GET /api/v1/health`: 200.
* `GET /api/v1/auth/me` without a token: 401 envelope.
* `POST /api/v1/auth/signup`: reached the backend and returned 500 because the database connection failed.
* `POST /api/v1/auth/login`: reached the backend and returned 500 because the database connection failed.
* `GET /api/v1/investor-profile` and `GET /api/v1/assets`: blocked by the same database credential issue.
* `GET /api/v1/news`: 200 using development sample/fallback data.

No backend code changes were required in Sprint 023. Full persisted auth/profile validation requires Docker PostgreSQL or corrected local PostgreSQL credentials.

## Sprint 024 Persisted Environment Validation Notes

Sprint 024 revalidated the local database workflow and confirmed the blocker remains machine-level environment setup.

Docker/PostgreSQL results:

* `docker --version`: failed because `docker` is not recognized on PATH.
* `docker compose version`: failed because `docker` is not recognized on PATH.
* `docker info`: failed because `docker` is not recognized on PATH.
* `docker compose up -d`: failed because `docker` is not recognized on PATH.
* `python backend/scripts/bootstrap_dev.py`: failed because local PostgreSQL rejects `investguide_user` credentials.
* `python backend/scripts/check_database.py`: failed because PostgreSQL is unavailable or unreachable with the configured credentials.
* `python -m alembic current`: Alembic configuration loads, but current revision lookup is deferred until PostgreSQL is reachable.

Runtime results:

* `python -m uvicorn app.main:app --port 8001`: backend starts successfully without reload.
* `GET /api/v1/health`: 200 with `database: unavailable` and `migrations: unavailable`.
* `POST /api/v1/auth/signup`: 500 due PostgreSQL connection failure.
* `POST /api/v1/auth/login`: 500 due PostgreSQL connection failure.
* `GET /api/v1/investor-profile` and `GET /api/v1/assets`: blocked by PostgreSQL connection failure.
* `GET /api/v1/news`: 200 using development sample/fallback data.

No backend code changes or persistence bypasses were made. Full persisted auth/profile validation requires Docker PostgreSQL or corrected local PostgreSQL credentials.

## Sprint 031 Company Intelligence Foundation

Sprint 031 introduces the Company Intelligence layer above investment assets. Companies are now first-class issuer records that can connect to listed assets, related news, deterministic assessments, and future analytics surfaces.

Backend additions:

* `GET /api/v1/companies` - list companies with pagination and optional filters.
* `GET /api/v1/companies/{ticker}` - return company overview, related assets, latest news, and `assessment_available`.
* `GET /api/v1/companies/{ticker}/assessment` - reuse the existing deterministic asset assessment summary through the company's primary related asset when available.

Database changes:

* `companies` table for issuer-level company knowledge.
* `company_news` table for Company to News relationships.
* `assets.company_id` nullable foreign key for Company to Assets relationships.

Relationships:

* Company -> many Assets.
* Company -> many News Articles.
* Company news may also be derived from related asset-news links.

Future extension points are prepared for financial statements, dividends, filings, directors, competitors, historical metrics, and portfolio holdings, but none of those product features are implemented yet. This sprint does not add AI, predictions, recommendations, portfolio features, watchlists, live prices, financial statements, dividend engines, scrapers, or authentication changes.

Validation:

* `python -m pytest -q`: passed, 158 tests.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

## Sprint 032 Company Intelligence Enrichment Foundation

Sprint 032 adds the Company Intelligence Enrichment layer. This layer stores structured, source-transparent company facts that future company research pages, financial statement analysis, AI explanations, portfolio intelligence, comparisons, industry analysis, and investment assessments can consume.

Implemented backend pieces:

* SQLAlchemy model: `app/models/company_profile.py`
* Pydantic schemas: `app/schemas/company_profile.py`
* Read service: `app/services/company_profile_service.py`
* Enrichment service: `app/services/company_enrichment.py`
* Development fixture data: `app/database/company_profile_seed.py`
* Alembic migration: `alembic/versions/20260703_0001_create_company_profiles_table.py`

Database changes:

* `company_profiles` table.
* One-to-one `companies.id -> company_profiles.company_id` relationship.
* Research status, source name, source URL, and last verified timestamp fields.

Endpoint:

* `GET /api/v1/companies/{ticker}/profile`

Response shape:

```json
{
  "success": true,
  "message": "Company profile retrieved successfully",
  "data": {
    "company": {},
    "profile": {},
    "verification": {
      "last_verified": "2026-07-03T00:00:00Z",
      "source_name": "InvestGuide development fixture data",
      "source_url": "https://example.com",
      "research_status": "development"
    }
  }
}
```

Research status values:

* `development`
* `verified`
* `needs_review`
* `unavailable`

The enrichment service fills missing structured fields from development fixtures while preserving existing verified data. It does not scrape, call external APIs, generate AI summaries, fabricate financial metrics, or run automatically at startup. Development fixtures are clearly labeled as fixture data and are intended for local development and tests only.

## Sprint 033 Company Intelligence Persistence Workflow

Sprint 033 moves Company Intelligence enrichment data toward persisted runtime use without adding new product features.

Manual seed commands:

```bash
python -m alembic upgrade head
python -m app.database.seed
```

The unified development seed command now runs in this order:

1. Seed development assets from `app/database/seed_assets.py`.
2. Create or update issuer-level `Company` records from seeded assets and link `assets.company_id`.
3. Seed persisted `CompanyProfile` records from `app/database/company_profile_seed.py` through `app/database/seed_company_profiles.py`.
4. Seed the development investor profile fallback.

Company profile seed behavior:

* inserts missing `company_profiles` rows
* avoids duplicate profile records
* fills missing fields where development fixture data is available
* preserves verified profile fields and source metadata
* logs inserted, skipped, updated, and missing-company counts
* rolls back cleanly on SQLAlchemy errors
* never runs automatically during FastAPI startup

Standalone profile seed command:

```bash
python -m app.database.seed_company_profiles
```

Runtime validation status:

* Docker CLI is installed: `Docker version 29.6.1`.
* Docker Compose is installed: `Docker Compose version v5.3.0`.
* Docker Desktop daemon is blocked locally: `Docker Desktop is unable to start`.
* `python backend/scripts/check_database.py` reports PostgreSQL unavailable with connection timeouts on `localhost:5432`.
* `python -m alembic current` loads configuration but defers revision lookup because PostgreSQL rejects or cannot complete the configured `investguide_user` connection.

Because PostgreSQL is unavailable on this machine, persisted endpoint validation for `/api/v1/companies`, `/api/v1/companies/{ticker}`, `/api/v1/companies/{ticker}/profile`, `/api/v1/assets`, `/api/v1/assets/{ticker}`, and `/api/v1/assets/{ticker}/assessment` remains blocked until Docker Desktop starts or local PostgreSQL credentials are corrected.

## Sprint 033.1 Local PostgreSQL Runtime Fix

Sprint 033.1 fixed the local Docker/PostgreSQL backend runtime path.

Root cause:

* `backend/.env` contained a UTF-8 BOM, visible in some shells as `∩╗┐APP_NAME=InvestGuide Backend`.
* Host port `5432` had multiple listeners: Docker internals and a separate local `postgres.exe` process.
* Backend host connections to `localhost:5432` could hit the non-Docker PostgreSQL service, causing `password authentication failed for user "investguide_user"` even though credentials worked inside the Docker container.

Fix applied:

* Rewrote `backend/.env` as UTF-8 without BOM.
* Remapped Docker PostgreSQL from host `5432` to host `5433` while keeping container port `5432`.
* Updated `docker-compose.yml`, `backend/.env`, and `backend/.env.example` to use:

```text
DATABASE_URL=postgresql+psycopg://investguide_user:investguide_password@localhost:5433/investguide
```

Runtime validation:

* `docker compose down -v`: completed and removed the old development volume.
* `docker compose up -d`: completed and started `investguide-postgres`.
* `docker ps`: showed `investguide-postgres` running with `0.0.0.0:5433->5432/tcp` and healthy status.
* `docker exec investguide-postgres psql -U investguide_user -d investguide`: connected successfully.
* `python -m alembic upgrade head`: applied all migrations through `20260703_0001`.
* `python -m app.database.seed`: completed successfully.
* `python backend/scripts/check_database.py`: reported database connected, migrations current, seed data present, and asset count 9.

Backend smoke results on `http://127.0.0.1:8001/api/v1`:

* `GET /health`: passed, database connected and migrations current.
* `GET /assets`: passed, returned 9 seeded assets.
* `GET /companies`: passed, returned 9 seeded companies.
* `GET /companies/DLTA/profile`: passed, returned persisted CompanyProfile data.
* `GET /assets/DLTA/assessment`: passed, returned deterministic assessment data.

Note: `DELTA` is not the stored ticker. The canonical seeded ticker is `DLTA`, so `/companies/DELTA/profile` and `/assets/DELTA/assessment` correctly return 404 until an alias layer is intentionally designed.
---

## Authentication Dependency Stabilization

Backend password hashing uses `passlib[bcrypt]` with bcrypt pinned to the compatible `4.0.x` line. The supported local combination is:

* `passlib==1.7.4`
* `bcrypt==4.0.1`

This avoids the bcrypt metadata compatibility issue where newer bcrypt releases no longer expose `bcrypt.__about__`, while keeping bcrypt password hashing intact. Do not truncate passwords as a workaround.

Local CORS defaults allow both `http://localhost:3000` and `http://127.0.0.1:3000` for frontend development.
Local CORS note: development CORS now includes `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:3001`, and `http://127.0.0.1:3001` because Next.js may move to port 3001 when port 3000 is already occupied.
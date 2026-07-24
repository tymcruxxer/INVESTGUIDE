# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides application setup, environment-based configuration, logging, middleware, database session wiring, SQLAlchemy base metadata conventions, Alembic migration scaffolding, response envelope helpers, exception handlers, API versioning, a health endpoint, the investment asset domain model layer, read-only asset API routes, deterministic asset/company research endpoints, a manual development asset seed command, and the news intelligence foundation with read-only news routes, persisted content hashes for scalable duplicate detection, and a JWT authentication foundation with user-owned investor profiles.

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

* `backend/.env` contained a UTF-8 BOM, visible in some shells as `ÃƒÂ¢Ã‹â€ Ã‚Â©ÃƒÂ¢Ã¢â‚¬Â¢Ã¢â‚¬â€ÃƒÂ¢Ã¢â‚¬ÂÃ‚ÂAPP_NAME=InvestGuide Backend`.
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
## Sprint 036 Runtime Demo Validation

Sprint 036 revalidated the local persisted backend path against Docker PostgreSQL on host port `5433`.

Runtime commands used:

```bash
docker compose up -d
cd backend
python -m alembic upgrade head
python -m app.database.seed
cd ..
python backend/scripts/check_database.py
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

Backend smoke results on `http://127.0.0.1:8001/api/v1`:

* `GET /health`: passed.
* `GET /assets`: passed, returned 9 seeded assets.
* `GET /companies`: passed, returned 9 seeded companies.
* `GET /news`: passed, returned 0 persisted articles in the current local database.
* `GET /companies/DLTA/profile`: passed, returned persisted company profile data.
* `GET /assets/DLTA/assessment`: passed, returned deterministic assessment data.
* `POST /auth/signup`: passed with a unique test account.
* `POST /auth/login`: passed with the same test account.
* `GET /auth/me`: passed with bearer token.
* `POST /investor-profile`: passed with frontend-compatible onboarding values.
* `GET /investor-profile`: passed and returned the persisted authenticated profile.

Canonical ticker note:

* Delta Corporation is seeded as `DLTA`.
* The frontend maps friendly `delta` routes to `DLTA`; backend endpoints remain canonical and expect `DLTA` unless a future alias layer is designed.

Known runtime limitation:

* The current local PostgreSQL database has zero persisted news rows after the standard seed. News API reachability is healthy, but live or seeded article population remains a future data task.
## Sprint 038 AI Research Engine Foundation

Sprint 038 adds a deterministic AI Research Engine foundation without connecting to any LLM, external AI provider, recommendation model, prediction model, or chatbot.

Backend additions:

* `GET /api/v1/assets/{ticker}/research` - returns structured research for an asset.
* `GET /api/v1/companies/{ticker}/research` - returns structured research for a company using company facts, primary related asset data, and CompanyProfile context where available.
* New schema: `app/schemas/research.py`.
* New deterministic intelligence modules under `app/services/intelligence/`: opportunity, risk, evidence, education, question, summary, scoring, shared models, and research composition service.

Research payload sections:

* `overall_assessment`
* `opportunity`
* `risk`
* `evidence`
* `education`
* `eli18`
* `suggested_questions`
* `transparency`
* `generated_at`, `assessment_version`, and `engine_version`

The research service is deterministic and evidence-based. It explains what available structured data suggests, records evidence strength and data used, and avoids buy/sell language, price targets, predictions, or personalized recommendations. A process-local cache prevents unnecessary recomputation for unchanged asset/company inputs.

Future AI integration should enhance this structured research layer, not replace it. Any future LLM output should consume the deterministic research payload as source context and preserve the same safety constraints.

Validation:

* `python -m pytest -q` from the repository root: passed, 235 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
## Sprint 039 Research Experience Runtime Validation

Sprint 039 polished and validated the AI Research runtime experience without adding new AI capabilities, LLM integrations, predictions, recommendations, portfolios, watchlists, alerts, live scraping, or backend architecture changes.

Runtime validation on `http://127.0.0.1:8001/api/v1`:

* `GET /health`: 200.
* `GET /assets`: 200.
* `GET /assets/DLTA`: 200.
* `GET /assets/DLTA/research`: 200; measured at approximately 45ms from the operator smoke command and approximately 9ms in backend request logs after startup.
* `GET /companies`: 200.
* `GET /companies/DLTA`: 200.
* `GET /companies/DLTA/research`: 200; measured at approximately 354ms from the operator smoke command and approximately 140ms in backend request logs.
* `GET /companies/DLTA/profile`: 200.
* `GET /news`: 200.
* `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`, `POST /investor-profile`, and `GET /investor-profile`: passed with valid onboarding values.

Performance observations:

* Research endpoint response times are acceptable for the current deterministic, read-only implementation.
* The process-local research cache remains in place for unchanged inputs.
* No duplicate backend research calls or server-side regeneration issues were observed during route smoke; future browser tooling should verify client-side query duplication visually in DevTools if needed.

Known limitations:

* Browser QA was represented by local route/API smoke and server log checks from this environment; full interactive human QA across desktop, tablet, and mobile remains recommended.
* Research remains rule-based and limited to structured fields currently available in the backend.
## Sprint 040 Research Intelligence v2

Sprint 040 extends deterministic research from single-subject analysis into relationship-aware financial intelligence.

Backend additions:

* `GET /api/v1/compare` compares either `asset_a` + `asset_b` or `company_a` + `company_b`.
* `GET /api/v1/companies/{ticker}/related` returns related companies, related sectors, related asset types, Learn Next topics, and a lightweight knowledge graph.
* `app/services/intelligence/comparison_engine.py` compares business context, opportunity framing, risk drivers, evidence strength, educational differences, and follow-up questions.
* `app/services/intelligence/related_engine.py` ranks related companies using deterministic sector, industry, exchange, asset type, and descriptive overlap.
* `app/services/intelligence/knowledge_graph.py` maps companies/assets to educational concepts such as Consumer Staples, Dividend Investing, REITs, Risk, and Diversification.

Relationship outputs always include explanations for why links exist. They are educational research paths, not predictions, buy/sell recommendations, portfolio advice, or personalized financial advice.

Validation:

* `python -m pytest -q`: passed, 241 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Relationships are deterministic and rule-based.
* No graph database is used.
* No LLMs, external AI services, financial statements, live prices, portfolio context, predictions, or recommendations are included.

## Sprint 041 Product Experience Polish

Sprint 041 was a frontend-focused polish sprint. It did not add backend APIs, database tables, AI features, predictions, recommendations, portfolios, watchlists, notifications, live scraping, or API contract changes.

Runtime notes:

* `python -m pytest -q`: passed, 241 tests, 1 non-blocking pytest cache permission warning.
* Runtime relationship API retry: `GET /api/v1/compare?asset_a=DLTA&asset_b=TIGZ` passed.
* Runtime related API retry: `GET /api/v1/companies/DLTA/related` passed with 4 related companies, 6 Learn Next topics, and 10 knowledge graph nodes.
* First cold `/api/v1/compare` request during smoke completed with 200 in backend logs after the client-side timeout; warmed retry passed.
* A health smoke during this session returned `database: unavailable` even though direct relationship endpoints and prior diagnostics worked. Recheck `python backend/scripts/check_database.py` before relying on health database status in the next runtime QA pass.

## Sprint 042 News Intelligence Engine

Sprint 042 adds a deterministic News Intelligence layer for existing news articles. It does not use LLMs, sentiment models, predictions, buy/sell recommendations, alerts, live scraping, or portfolio advice.

Backend additions:

* `GET /api/v1/news/{id}/research` - returns deterministic research for one news article.
* `app/services/intelligence/news_engine.py` - classifies article events, scores importance, evaluates evidence, links related companies/sectors/asset types, builds Learn Next topics, and integrates the lightweight knowledge graph.

Research payload sections:

* `event_category` - rule-based category such as Earnings, Dividend, Regulatory, Macro Economy, Exchange, Commodity, Currency, or Market Update.
* `importance` - Low, Medium, or High with visible reasons.
* `evidence` - source quality, data completeness, confidence, data used, and missing data.
* `why_it_matters` and `explain_like_im_18` - deterministic educational explanations.
* `related_companies`, `related_sectors`, `related_asset_types`, `related_topics`, `learn_next`, and `knowledge_graph`.
* `transparency` - methodology and educational-not-advisory boundary.

Design rules:

* The engine explains what happened, why it matters, what users should learn next, and which companies or concepts are connected.
* It never infers future prices and never generates investment advice.
* Process-local caching avoids recomputing unchanged article research during the current runtime.

Validation:

* `python -m pytest -q`: passed, 247 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

## Sprint 043 Business Intelligence Engine

Sprint 043 adds deterministic Business Intelligence and Industry Intelligence on top of the existing Company Intelligence layer. This is not an LLM feature and does not provide predictions, buy/sell recommendations, personalized advice, alerts, watchlists, portfolio optimization, or live scraping.

Backend additions:

* `GET /api/v1/companies/{ticker}/business` - returns deterministic company deep-dive intelligence.
* `GET /api/v1/industries/{industry}` - returns deterministic industry overview, companies, risks, opportunities, Learn Next topics, and related industries.
* `app/services/intelligence/business_engine.py` - composes company metadata, CompanyProfile facts, industry context, competitor reasoning, revenue drivers, operational risks, business maturity, geographic exposure, and knowledge graph expansion.
* `app/services/intelligence/industry_engine.py` - maps industries to typical characteristics, common risks, common opportunities, economic sensitivity, cyclical/defensive profile, and educational summaries.
* `app/services/intelligence/competitor_engine.py` - ranks direct competitors, similar businesses, and related businesses using shared industry, sector, exchange, market, and descriptive overlap.

Business intelligence payload sections:

* Business Summary
* Business Model
* Revenue Drivers
* Competitive Position
* Industry Position
* Business Maturity
* Geographic Exposure
* Operational Risks
* Industry Intelligence
* Competitors
* Knowledge Graph
* Educational Notes
* Transparency

Architecture rules:

* Uses persisted structured data or clearly marked development profile data.
* Missing facts are marked as unavailable instead of fabricated.
* Every label includes reasoning or methodology.
* Competitor relationships are research paths, not recommendations.

Validation:

* `python -m pytest -q`: passed, 253 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

## Sprint 044 Financial Intelligence Engine

Sprint 044 adds deterministic Financial Intelligence to the Company Intelligence layer.

New backend persistence:

* `income_statements`
* `balance_sheets`
* `cash_flow_statements`

Each statement row belongs to a company, records fiscal year/period/currency/source metadata, and includes `is_development_data` so development fixtures cannot be mistaken for verified filings.

New endpoints:

* `GET /api/v1/companies/{ticker}/financials`
* `GET /api/v1/companies/{ticker}/financial-health`

Architecture:

* `app/services/intelligence/financial_engine.py` transforms structured financial statement rows into financial health, revenue analysis, profitability analysis, liquidity analysis, leverage analysis, cash flow analysis, growth characteristics, stability assessment, financial ratios, trend analysis, educational summary, ELI18 explanation, and transparency metadata.
* `app/services/financial_statement_service.py` is the database access boundary for persisted statements.
* `app/database/seed_financial_statements.py` provides manual, duplicate-aware development seed data. It does not run automatically on startup.
* The unified manual seed command `python -m app.database.seed` now seeds assets, companies, company profiles, financial statements, and the development investor profile.

Ratio engine:

* Profit Margin
* Operating Margin
* Net Margin
* Current Ratio
* Quick Ratio
* Debt-to-Equity
* Debt Ratio
* Return on Equity
* Return on Assets
* Asset Turnover
* Operating Cash Flow Ratio
* Interest Coverage

Every ratio returns a value, interpretation, why it matters, and educational explanation.

Financial Health scoring remains deterministic and evidence-based. It combines profitability, liquidity, leverage, operating cash flow, and trend evidence into one of: Excellent, Strong, Healthy, Moderate, Weak, or Concerning. Missing data and uncertainty are always reported.

Constraints preserved:

* No LLMs.
* No price or earnings predictions.
* No buy/sell recommendations.
* No portfolio optimization.
* No watchlists, alerts, live scraping, or personalized advice.

Validation:

* `python -m pytest -q`: passed, 260 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

## Sprint 045 Financial Runtime Validation and Development Data Isolation

Sprint 045 validates the Sprint 044 financial intelligence stack against local PostgreSQL and adds production safeguards for development fixture data.

Runtime validation:

* `docker compose up -d`: PostgreSQL container running.
* `python -m alembic upgrade head`: migrated to `20260713_0002`.
* `python -m app.database.seed`: completed after the migration was applied sequentially.
* `python backend/scripts/check_database.py`: connected, migrations current, current revision `20260713_0002`, seed data present, asset count 9.
* Port `8001` was occupied by an unresolvable stale local listener during this session, so backend smoke validation ran on `http://127.0.0.1:8010`.

Financial endpoint smoke:

* `GET /api/v1/companies/DLTA/financials`: passed.
* `GET /api/v1/companies/DLTA/financial-health`: passed.
* Response included company data, two income statement periods, two balance sheet periods, two cash flow periods, 12 ratios, financial health, 7 trend rows, educational summary, ELI18 explanation, data sources, available periods, missing data, development-data status, last updated, and methodology.

Development data isolation:

* `ALLOW_DEVELOPMENT_DATA=true` is required together with `APP_ENV=development` for fixture seed commands.
* Production or disabled fixture mode raises: `Development seed aborted: fixture data is disabled in this environment.`
* Financial statement reads prefer verified rows over development rows.
* Production financial reads exclude development financial rows.
* Development fixture rows remain marked with `is_development_data` and source metadata.

Data-origin precedence:

1. Verified live or imported data.
2. Verified manually curated data.
3. Development preview data.
4. Unavailable.

Safe cleanup workflow:

```bash
python -m app.database.cleanup_development_data --dry-run
python -m app.database.cleanup_development_data --confirm
```

The command defaults to dry-run, reports counts by entity, deletes only explicit development records when confirmed, and preserves verified records. Back up production data before any confirmed cleanup.

Future ingestion contract:

The package `app/services/ingestion/` defines future contracts for verified ZSE/VFEX ingestion without calling live sources yet:

* `base.py`
* `company_ingestion.py`
* `financial_ingestion.py`
* `market_ingestion.py`
* `news_ingestion.py`

These contracts are intended to normalize external source data into existing company, asset, financial statement, company profile, market, and news models without changing frontend contracts or deterministic intelligence engines.

Validation:

* `python -m pytest -q`: passed, 268 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

## Sprint 046 Dividend Intelligence Engine

Sprint 046 adds deterministic Dividend Intelligence on top of the existing Company and Financial Intelligence layers.

Implemented:

* Persisted `dividends` and `corporate_actions` tables with company/asset relationships, source metadata, development-data flags, indexes, and uniqueness rules.
* Alembic migrations `20260714_0001_create_dividends_and_corporate_actions.py` and `20260714_0002_add_dividend_timestamp_defaults.py`.
* Manual duplicate-aware development dividend seed runner: `python -m app.database.seed_dividends`.
* Unified manual seed workflow now includes development dividend fixtures through `python -m app.database.seed`.
* Dividend data follows the existing production isolation policy: verified records take precedence, development rows appear only when `APP_ENV=development` and `ALLOW_DEVELOPMENT_DATA=true`, and production reads exclude development rows.
* Cleanup workflow reports dividend and corporate-action fixture rows and deletes them only with explicit `--confirm`.
* Read-only endpoints:
  * `GET /api/v1/companies/{ticker}/dividends`
  * `GET /api/v1/companies/{ticker}/dividend-intelligence`
* Future ingestion contracts:
  * `app/services/ingestion/dividend_ingestion.py`
  * `app/services/ingestion/corporate_action_ingestion.py`

Methodology:

* Dividend yield is calculated only when annual dividend per share and a reliable reference price are available. No fake or stale price is used.
* Dividend payout ratio is calculated as `total dividends / net profit` only when both values are available and net profit is positive.
* Cash payout ratio is calculated as `total dividends / operating cash flow` only when operating cash flow is available and positive.
* Dividend growth compares year-over-year dividend-per-share values only across available comparable periods and never forecasts future growth.
* Sustainability combines historical dividend records, payout ratio, cash payout ratio, growth, consistency, and available financial statement evidence.

Safety and transparency:

* Dividend Intelligence is educational and historical. It does not predict future dividends, price movement, or returns.
* Development dividend fixtures are labelled `Development Preview` and must never be presented as verified ZSE or VFEX data.
* Missing data is explicit; missing InvestGuide records are not treated as proof that a company did not pay a dividend.

Runtime validation:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260714_0002`.
* `python -m app.database.seed`: passed after timestamp defaults were fixed.
* `python backend/scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* `GET /api/v1/companies/DLTA/dividends`: passed on `http://127.0.0.1:8011`, returned 2 development preview records.
* `GET /api/v1/companies/DLTA/dividend-intelligence`: passed on `http://127.0.0.1:8011` with dividend status, payout ratio, cash payout ratio, growth, sustainability, and transparency.
* `/company/delta`: returned HTTP 200 from Next.js dev server.

Validation:

* `python -m pytest -q`: passed, 280 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

## Sprint 047 Verified Data Pipeline Framework

Sprint 047 turns the earlier ingestion contracts into a reusable source-agnostic pipeline. This is not a live ZSE/VFEX connector sprint and does not add public ingestion APIs.

Pipeline flow:

```text
External Source -> Source Adapter -> Normalizer -> Validator -> Importer -> Database -> Deterministic Engines -> Frontend
```

New backend architecture:

* `app/services/ingestion/types.py` defines source metadata, verification states, import modes, normalized records, validation issues, import results, and pipeline results.
* `app/services/ingestion/sources/` provides local JSON and CSV adapters with checksum and record-count metadata.
* `app/services/ingestion/normalizers/` standardizes ticker, exchange, currency, dates, decimals, URLs, company names, dividend types, and statement periods.
* `app/services/ingestion/validators/` returns valid records, warnings, rejected records, and field-level errors.
* `app/services/ingestion/importers/` performs idempotent database upserts for companies, income statements, dividends, and news.
* `app/services/ingestion/pipeline.py` orchestrates loading, normalization, validation, importing, and audit recording.
* `app/services/ingestion/registry.py` maps entities to their normalizer, validator, and importer.
* `app/models/ingestion.py` stores `ingestion_runs` audit rows without storing raw source documents.

Import modes:

* `dry_run` is the default and does not write entity rows.
* `lenient` imports valid rows and skips rejected rows.
* `strict` rejects the entire batch when validation rejects any row.

CLI examples:

```bash
cd backend
python -m app.services.ingestion.cli --entity companies --source-file tests/fixtures/ingestion/companies.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity income_statements --source-file tests/fixtures/ingestion/financial_statements.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity dividends --source-file tests/fixtures/ingestion/dividends.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
python -m app.services.ingestion.cli --entity news --source-file tests/fixtures/ingestion/news.json --source-type DEVELOPMENT_FIXTURE --mode lenient --development-data
```

Development fixture imports still require the existing development-data policy: `APP_ENV=development` and `ALLOW_DEVELOPMENT_DATA=true` for non-dry-run modes. Verified/non-development persisted records must not be overwritten by lower-quality development fixture rows.

Architecture reference: `docs/architecture/data-ingestion-pipeline.md`.


## Sprint 048 Verified Data Ingestion Completion

Sprint 048 completes the reusable verified ingestion framework for the backend's current persisted intelligence domains. It does not add live connectors, scraping, schedulers, public ingestion APIs, predictions, recommendations, or AI.

Added ingestion coverage:

* Assets
* Company profiles
* Balance sheets
* Cash flow statements
* Corporate actions
* Market snapshots

Existing Sprint 047 coverage remains:

* Companies
* Income statements
* Dividends
* News

Market snapshots are persisted in the new `market_snapshots` table and are used as the latest acceptable reference price for Dividend Intelligence when available. The endpoint contract remains unchanged; deterministic engines consume persisted backend data.

Example verified-ingestion commands:

```bash
cd backend
python -m app.services.ingestion.cli --entity assets --source-file tests/fixtures/ingestion/assets.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity company_profiles --source-file tests/fixtures/ingestion/company_profiles.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity balance_sheets --source-file tests/fixtures/ingestion/balance_sheets.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity cash_flow_statements --source-file tests/fixtures/ingestion/cash_flow_statements.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity corporate_actions --source-file tests/fixtures/ingestion/corporate_actions.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
python -m app.services.ingestion.cli --entity market_snapshots --source-file tests/fixtures/ingestion/market_snapshots.json --source-type DEVELOPMENT_FIXTURE --mode dry_run --development-data
```

Use `--mode lenient --development-data` only in development environments where fixture imports are intentionally allowed. Verified or non-development rows are protected from lower-quality development fixture overwrites.

Runtime validation completed:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260715_0002`.
* `python -m alembic current`: `20260715_0002 (head)`.
* `python -m app.database.seed`: supported existing development seed workflow.
* `python scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* Dry-run and lenient imports passed for assets, company profiles, balance sheets, cash flow statements, corporate actions, and market snapshots.
* Backend smoke passed for company profile, financials, financial health, dividend intelligence, asset assessment, assets, and news endpoints on `http://127.0.0.1:8013`.

## Sprint 049 Ingestion Operations and Data Quality

Sprint 049 adds an internal read-only operations layer for the verified ingestion framework. It does not add live ZSE/VFEX connectors, scraping, external APIs, schedulers, public ingestion write endpoints, AI, predictions, recommendations, watchlists, alerts, portfolio optimization, or personalized advice.

Backend additions:

* `ingestion_record_issues` table for safe record-level warning, rejection, and error details.
* Additional run counters on `ingestion_runs`: normalized records, warning count, error count, and optional triggered-by metadata.
* Stable issue-code contract in `IssueCode`.
* Data-quality scoring package under `app/services/data_quality/`.
* Source health, entity quality, company quality, and deterministic operator recommendations.
* Diagnostics CLI: `python -m app.services.ingestion.diagnostics`.
* Internal read-only APIs under `/api/v1/internal/...`.

Internal API endpoints:

* `GET /api/v1/internal/ingestion/runs`
* `GET /api/v1/internal/ingestion/runs/{run_id}`
* `GET /api/v1/internal/ingestion/runs/{run_id}/issues`
* `GET /api/v1/internal/ingestion/sources`
* `GET /api/v1/internal/data-quality/summary`
* `GET /api/v1/internal/data-quality/entities/{entity_type}`
* `GET /api/v1/internal/data-quality/companies/{ticker}`

Internal access limitation:

* Until admin roles exist, internal operations endpoints are guarded to development/debug environments only.

Runtime validation:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260715_0003`.
* `python -m alembic current`: `20260715_0003 (head)`.
* Generated successful dry-run, successful lenient, warning/rejection, and failed strict ingestion runs.
* Diagnostics commands passed for runs, sources, quality, company `DLTA`, and CSV issue export.
* `python scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* Backend internal API smoke passed on `http://127.0.0.1:8014`.

Validation:

* `python -m pytest -q`: passed, 247 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 15 routes generated.

Documentation:

* See `docs/operations/data-quality-and-ingestion-operations.md`.

## Sprint 050 Macro Intelligence Engine

Sprint 050 adds deterministic Macro Intelligence without live APIs, scraping, schedulers, forecasting, LLMs, recommendations, or personalized advice.

Backend additions:

* `macro_indicators` persisted model with source, verification, ingestion, development-data, and timestamp metadata.
* Alembic migration `20260715_0004_create_macro_indicators.py`.
* Manual development seed support through `seed_macro_indicators()` and `python -m app.database.seed`.
* Verified-over-development retrieval in `app.services.macro_service`.
* Deterministic `app.services.intelligence.macro_engine` for macro explanations, company impact, sector sensitivities, related companies, knowledge graph paths, and Learn Next.
* Verified data pipeline support for `macro_indicators` via normalizer, validator, importer, registry, and local JSON fixture.

Read-only APIs:

* `GET /api/v1/macro`
* `GET /api/v1/macro/inflation`
* `GET /api/v1/macro/interest-rates`
* `GET /api/v1/macro/exchange-rates`
* `GET /api/v1/macro/gdp`
* `GET /api/v1/macro/commodities`
* `GET /api/v1/macro/{type}/research`
* `GET /api/v1/macro/company/{ticker}`

Runtime validation:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260715_0004`.
* `python -m app.database.seed`: passed after macro fixture loader was made UTF-8 BOM tolerant.
* `python scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* Macro API smoke passed on backend port `8015` for `/macro`, `/macro/inflation`, `/macro/inflation/research`, `/macro/gdp`, `/macro/exchange-rates`, `/macro/commodities`, and `/macro/company/DLTA`.

Known limitations:

* Macro values are development preview fixtures until verified RBZ/ZIMSTAT/ZSE/VFEX imports exist.
* Sector pages are not implemented yet; sector impact logic is reusable for future pages.
* No forecasting, predictions, live connectors, or financial advice were added.

## Sprint 051 Sector Intelligence Engine

Sprint 051 adds deterministic Sector and Industry Intelligence without LLMs, predictions, recommendations, personalized advice, portfolio features, live scraping, or live APIs.

Backend additions:

* Persisted `sectors` and `industries` tables with provenance, verification, ingestion, development-data, and timestamp metadata.
* Alembic migration `20260715_0005_create_sectors_and_industries.py`.
* Manual development seed support through `seed_sectors()` and `python -m app.database.seed`.
* Verified-data pipeline support for `sectors` and `industries` through normalizers, validators, importers, registry entries, and local JSON fixtures.
* `app.services.sector_service` with verified-over-development precedence and serialization helpers.
* Deterministic `app.services.intelligence.sector_engine` for sector research, industry research, macro relationships, related companies, knowledge graph paths, Learn Next topics, and transparent educational notes.

Read-only APIs:

* `GET /api/v1/sectors`
* `GET /api/v1/sectors/{slug}`
* `GET /api/v1/sectors/{slug}/research`
* `GET /api/v1/industries`
* `GET /api/v1/industries/{slug}`
* `GET /api/v1/industries/{slug}/research`

Data precedence:

1. Verified imported data.
2. Validated manual data.
3. Development Preview data when development fixture policy allows it.
4. Unavailable when no acceptable record exists.

Runtime validation:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260715_0005`.
* `python -m app.database.seed`: completed successfully.
* `python scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* Backend smoke passed on port `8016`: `/health`, `/sectors`, `/sectors/consumer-staples`, `/sectors/consumer-staples/research`, `/industries`, `/industries/beverages`, `/industries/beverages/research`, `/companies/DLTA`, and `/macro/inflation`.

Validation:

* `python -m pytest -q`: passed, 265 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 18 routes generated.

Documentation:

* See `docs/architecture/sector-intelligence.md`.

## Sprint 052 Financial Statement Intelligence Engine

Sprint 052 adds deterministic Financial Statement Intelligence on top of the existing persisted financial statement foundation.

Backend additions:

* Financial statement provenance fields for income statements, balance sheets, and cash flow statements: source type, imported timestamp, verified timestamp, verification status, dataset version, and external key.
* Alembic migration `20260721_0006_add_financial_statement_provenance.py`.
* Retrieval helpers for latest statements, available periods, statement trends, missing fields, and serialized statement payloads.
* Deterministic `financial_statement_engine` with revenue, profitability, liquidity, leverage, cash flow, and earnings quality sections.
* Read-only APIs:
  * `GET /api/v1/companies/{ticker}/financial-statements`
  * `GET /api/v1/companies/{ticker}/financial-intelligence`

Architecture notes:

* The backend owns statement intelligence and exposes structured evidence, confidence, provenance, educational explanations, ELI18 text, and Learn Next topics.
* The engine does not call AI services, forecast prices, provide buy/sell recommendations, or personalize financial advice.
* Development fixture data remains explicitly labelled; production-facing confidence should depend on verified imported or validated manual records.

Validation:

* `python -m pytest -q -o cache_dir=C:/tmp/investguide-pytest-cache`: passed, 269 tests.
* `python -m alembic history -r-5:current`: timed out in this local environment while loading Alembic/database configuration; migration file is present but live DB migration validation remains pending.

## Sprint 052 Owner and Administration Foundation

Sprint 052 adds the secure administration foundation without implementing user management, role editing, ingestion dashboards, analytics dashboards, feature flags, or AI provider configuration.

Backend additions:

* RBAC models: `Role`, `Permission`, `RolePermission`, and `UserRole`.
* Audit model: `AuditLog` for privileged action records.
* Sensitive-action model: `SensitiveActionRequest` for future re-authentication, MFA-compatible, and confirmation workflows.
* Alembic migration `20260721_0007_create_rbac_and_audit_foundation.py`.
* RBAC bootstrap through `python -m app.database.seed` using development-only `ADMIN_OWNER_EMAIL` and `ADMIN_OWNER_PASSWORD` settings.
* Reusable `require_permission()` dependency for server-side authorization.
* Owner protection helper that blocks normal delete, suspend, and demotion workflows.
* Admin APIs:
  * `GET /api/v1/admin/me`
  * `GET /api/v1/admin/navigation`
  * `GET /api/v1/admin/permissions`

Security notes:

* Owner bypasses normal permission checks while still being auditable.
* Exactly one active Owner assignment is expected after bootstrap.
* Production Owner creation must be performed securely and must not use committed development credentials.
* Frontend checks are convenience only; admin APIs enforce permissions server-side.

Validation:

* `python -m pytest tests/test_admin_rbac.py -q --tb=short -o cache_dir=C:/tmp/investguide-pytest-cache`: passed, 14 tests.
* `python -m pytest -q -o cache_dir=C:/tmp/investguide-pytest-cache`: passed, 283 tests.

## Sprint 053: User, Role & Permission Management

The administration foundation now includes controlled user, role, and permission inspection workflows.

Backend APIs:

* `GET /api/v1/admin/users` - user directory with search, pagination, sorting, and filters.
* `GET /api/v1/admin/users/{id}` - safe user detail with roles, effective permissions, activity summary, and audit summary.
* `PATCH /api/v1/admin/users/{id}/roles` - assign or remove non-Owner roles with confirmation, reason, audit history, and duplicate prevention.
* `PATCH /api/v1/admin/users/{id}/status` - suspend or restore users with confirmation, reason, audit history, and Owner/self/last-admin protections.
* `GET /api/v1/admin/roles` - read-only role catalog with inherited permission metadata.
* `GET /api/v1/admin/roles/{id}` - read-only role detail.
* `GET /api/v1/admin/permissions` - permission catalog and current admin permission context.

Development seed workflow:

```bash
cd backend
python -m app.database.seed
```

The manual seed now creates RBAC roles/permissions, the development Owner, and sample admin users for local testing. It is duplicate-aware and does not run automatically on application startup.

Security notes:

* Password hashes and secrets are never exposed in admin user responses.
* Owner role assignment/removal is blocked in normal workflows.
* Owner suspension is blocked.
* Self-suspension and self role changes are blocked.
* Suspending the last active administrator is blocked.
* Role/status changes require a reason and are recorded in audit/history tables.

See `docs/architecture/user-role-management.md` for the detailed architecture.

## Sprint 054: Data Source Registry

The backend now includes a normalized Data Source Registry for configuring future ingestion sources without code changes.

Admin APIs:

* `GET /api/v1/admin/sources` - source list with search, pagination, and filters.
* `GET /api/v1/admin/sources/{id}` - source detail with configuration, masked credentials, provenance, version history, and recent activity.
* `POST /api/v1/admin/sources` - create a source registry entry.
* `PATCH /api/v1/admin/sources/{id}` - update source identity, connector configuration, or credential metadata.
* `PATCH /api/v1/admin/sources/{id}/status` - set enabled, disabled, or maintenance mode.
* `DELETE /api/v1/admin/sources/{id}` - soft delete a source with reason and audit trail.

Manual development seed:

```bash
cd backend
python -m app.database.seed
```

The seed registers development catalogue entries for market, government, regulator, research, news, international, commodity, weather, and alternative-intelligence sources. It does not enable live ingestion and does not seed production credentials.

Security:

* Raw credential values are write-only.
* API responses expose only masked credential metadata.
* Every create/update/status/delete action records source version history and audit metadata.

See `docs/architecture/data-source-registry.md`.

## Pre-Sprint 055: Source Capabilities

The Data Source Registry now includes `supported_capabilities` on each source. This lets future ingestion jobs discover whether a source can provide market prices, corporate actions, dividends, reports, news, macroeconomic indicators, exchange rates, commodities, weather, or research reports without hard-coded source assumptions.

Connector Registry is intentionally deferred. Future work should allow many sources to reuse one connector implementation.

## Sprint 055: Ingestion Operations Centre

The backend now includes an Ingestion Operations Centre for defining and observing future ingestion jobs without executing live ingestion.

Backend additions:

* Normalized models for `IngestionJob`, `IngestionExecution`, `ExecutionMetric`, and `ExecutionFailure`.
* Alembic migration `20260722_0010_create_ingestion_operations_centre.py`.
* Manual development seed support through `seed_ingestion_operations()` and `python -m app.database.seed`.
* Secure admin APIs under `/api/v1/admin/ingestion`.
* RBAC enforcement using `ingestion.read` and `ingestion.manage`.
* Audit records for job create, update, run, retry, pause, resume, and cancel requests.

Admin APIs:

* `GET /api/v1/admin/ingestion/jobs`
* `GET /api/v1/admin/ingestion/jobs/{id}`
* `POST /api/v1/admin/ingestion/jobs`
* `PATCH /api/v1/admin/ingestion/jobs/{id}`
* `POST /api/v1/admin/ingestion/jobs/{id}/run`
* `POST /api/v1/admin/ingestion/jobs/{id}/retry`
* `POST /api/v1/admin/ingestion/jobs/{id}/pause`
* `POST /api/v1/admin/ingestion/jobs/{id}/resume`
* `POST /api/v1/admin/ingestion/jobs/{id}/cancel`
* `GET /api/v1/admin/ingestion/executions`
* `GET /api/v1/admin/ingestion/executions/{id}`

Manual operation requests are recorded only. No worker, scheduler, queue, parser, connector, scraper, or live API execution runs in this sprint.

See `docs/architecture/ingestion-operations-centre.md`.

## Sprint 056: Connector Registry

The backend now includes a reusable Connector Registry for future ingestion execution contracts.

Backend additions:

* Normalized models for `Connector`, `ConnectorCapability`, `ConnectorConfigurationSchema`, `ConnectorVersion`, and `ConnectorValidation`.
* Alembic migration `20260722_0011_create_connector_registry.py`.
* Nullable `sources.connector_id` binding so multiple sources can reuse one connector.
* Manual development seed support through `seed_connectors()` and `python -m app.database.seed`.
* Secure admin APIs under `/api/v1/admin/connectors`.
* RBAC enforcement using `connectors.read` and `connectors.update`.
* Audit records for connector create, update, validate, and lifecycle changes.

Admin APIs:

* `GET /api/v1/admin/connectors`
* `GET /api/v1/admin/connectors/capabilities`
* `GET /api/v1/admin/connectors/{id}`
* `POST /api/v1/admin/connectors`
* `PATCH /api/v1/admin/connectors/{id}`
* `POST /api/v1/admin/connectors/{id}/validate`
* `PATCH /api/v1/admin/connectors/{id}/status`

Connector validation is metadata-only. It checks required fields, lifecycle, auth compatibility, source-category compatibility, and unsafe secret-bearing schema fields. It never performs external network requests.

Seeded development connectors:

* Generic REST API Connector
* Generic RSS Feed Connector
* Generic HTML Scraper Connector
* Generic PDF Extractor Connector
* Generic CSV Importer Connector

No live HTTP calls, scraping, RSS fetching, parsing engines, workers, queues, schedulers, browser automation, or AI processing were added.

See `docs/architecture/connector-registry.md`.

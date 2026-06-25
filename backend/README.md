# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides application setup, environment-based configuration, logging, middleware, database session wiring, SQLAlchemy base metadata conventions, Alembic migration scaffolding, response envelope helpers, exception handlers, API versioning, a health endpoint, the investment asset domain model layer, read-only asset API routes, a manual development asset seed command, and the news intelligence foundation with read-only news routes, and persisted content hashes for scalable duplicate detection.

Business features such as authentication, asset/news write endpoints, analytics, AI, scrapers, notifications, and production deployment are intentionally not implemented yet.

## Requirements

* Python 3.12+
* PostgreSQL for migration execution, seeding, and live database-backed asset endpoints

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

Do not commit real database passwords or hosted database credentials.

## Local PostgreSQL Setup

Install PostgreSQL server and client tools, and ensure commands such as `psql` are available on your PATH. Start the PostgreSQL service before running migrations.

Create a local development database and user using your PostgreSQL client. Example SQL:

```sql
CREATE DATABASE investguide_dev;
CREATE USER investguide_user WITH PASSWORD 'replace_me';
GRANT ALL PRIVILEGES ON DATABASE investguide_dev TO investguide_user;
```

Then set `DATABASE_URL` in `.env`:

```bash
DATABASE_URL=postgresql+psycopg://investguide_user:replace_me@localhost:5432/investguide_dev
```

If you use the default local `postgres` user, update the username and password to match your machine. The repository does not include real credentials.

## Hosted PostgreSQL Setup

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

Expected response:

```json
{
  "success": true,
  "message": "Backend is healthy",
  "data": {
    "status": "ok",
    "version": "0.1.0-alpha"
  }
}
```

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
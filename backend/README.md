# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides application setup, environment-based configuration, logging, middleware, database session wiring, SQLAlchemy base metadata conventions, Alembic migration scaffolding, response envelope helpers, exception handlers, API versioning, a health endpoint, the investment asset domain model layer, read-only asset API routes, and a manual development asset seed command.

Business features such as authentication, asset write endpoints, analytics, AI, scrapers, notifications, and production deployment are intentionally not implemented yet.

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

Do not commit real database passwords or hosted database credentials.

## Local PostgreSQL Setup

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
|   |   `-- 20260625_0001_create_assets_table.py
|   |-- env.py
|   `-- script.py.mako
|-- app/
|   |-- api/
|   |   `-- v1/
|   |       |-- assets.py
|   |       |-- health.py
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
|   |   `-- session.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- asset.py
|   |   `-- mixins.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   `-- asset.py
|   |-- services/
|   |   `-- asset_service.py
|   |-- utils/
|   `-- main.py
|-- tests/
|   |-- test_asset_model.py
|   |-- test_asset_routes.py
|   |-- test_asset_schema.py
|   |-- test_asset_service.py
|   |-- test_database.py
|   |-- test_health.py
|   |-- test_seed_assets.py
|   `-- test_seed_command.py
|-- .env.example
|-- alembic.ini
|-- README.md
`-- requirements.txt
```
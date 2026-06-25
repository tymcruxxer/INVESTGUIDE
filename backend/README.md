# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides application setup, environment-based configuration, logging, middleware, database session wiring, SQLAlchemy base metadata conventions, Alembic migration scaffolding, response envelope helpers, exception handlers, API versioning, a health endpoint, and the initial investment asset domain model layer.

Business features such as authentication, asset CRUD endpoints, analytics, AI, scrapers, and notifications are intentionally not implemented yet.

## Requirements

* Python 3.12+
* PostgreSQL for migration execution and future database-backed modules

## Install

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Configure

```bash
copy .env.example .env
```

Environment variables:

* `APP_NAME` - FastAPI application name
* `APP_VERSION` - application version, currently `0.1.0-alpha`
* `ENVIRONMENT` - runtime environment
* `APP_DEBUG` - FastAPI debug flag
* `LOG_LEVEL` - logging level
* `DATABASE_URL` - SQLAlchemy database URL
* `CORS_ORIGINS` - comma-separated allowed origins

## Run

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

## Asset Domain Foundation

The first domain model layer is implemented for investment assets:

* SQLAlchemy model: `app/models/asset.py`
* Pydantic schemas: `app/schemas/asset.py`
* Development seed data structure: `app/database/seed_assets.py`
* Alembic migration: `alembic/versions/20260625_0001_create_assets_table.py`

The asset layer is database-only at this stage. It does not expose API routes or CRUD behavior. Seed data is provided as importable development data and is not executed automatically.

Supported domain values:

* `exchange`: `ZSE`, `VFEX`
* `asset_type`: `equity`, `REIT`, `bond`, `money_market`, `alternative`
* `currency`: `ZWG`, `USD`
* `status`: `active`, `suspended`, `delisted`

## Database Migrations

Alembic is configured under `backend/alembic` and uses the application `DATABASE_URL` from `app.core.config`.

Check current revision:

```bash
python -m alembic current
```

Create a migration after models are added:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Rollback one migration:

```bash
python -m alembic downgrade -1
```

If PostgreSQL is not available or credentials are not configured, `python -m alembic current` will load the Alembic environment and report that revision lookup is deferred. Migration execution requires a working PostgreSQL connection.

## Test

```bash
pytest
```

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
|   |-- utils/
|   `-- main.py
|-- tests/
|   |-- test_asset_model.py
|   |-- test_asset_schema.py
|   |-- test_database.py
|   |-- test_health.py
|   `-- test_seed_assets.py
|-- .env.example
|-- alembic.ini
|-- README.md
`-- requirements.txt
```
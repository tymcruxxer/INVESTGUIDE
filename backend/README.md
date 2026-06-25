# InvestGuide Backend

FastAPI backend foundation for InvestGuide.

This package currently provides infrastructure only: application setup, environment-based configuration, logging, middleware, database session wiring, response envelope helpers, exception handlers, API versioning, and a health endpoint.

Business features such as authentication, users, assets, analytics, AI, scrapers, and notifications are intentionally not implemented yet.

## Requirements

* Python 3.12+
* PostgreSQL for future database-backed modules

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

## Test

```bash
pytest
```

## Folder Structure

```text
backend/
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
|   |   `-- session.py
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |-- utils/
|   `-- main.py
|-- tests/
|   `-- test_health.py
|-- .env.example
|-- README.md
`-- requirements.txt
```


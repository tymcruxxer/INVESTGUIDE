# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 008

Sprint Goal: Build the News Intelligence Foundation without implementing scrapers, AI, external API calls, authentication, or frontend integration.

Current Tasks:

* [x] Created the `News` SQLAlchemy model.
* [x] Added the `asset_news` many-to-many association table.
* [x] Linked `Asset` and `News` through SQLAlchemy relationships.
* [x] Created Pydantic news schemas.
* [x] Created read-only news service functions.
* [x] Created read-only `/api/v1/news` endpoints.
* [x] Added development-only sample news data.
* [x] Added Alembic migration for `news_articles` and `asset_news`.
* [x] Added tests for news model, schemas, service behavior, and routes.
* [x] Updated backend README, project state, and context.

Sprint Exit Criteria:

* News model exists.
* Asset-news relationship exists.
* News schemas exist.
* News service exists.
* Read-only News API exists.
* Seed/sample data exists.
* Tests pass.
* Health endpoint still works.
* No scraper code exists yet.
* No AI code exists yet.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, and read-only news endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: Not Started

Analytics Engine: Not Started

AI/RAG: Not Started

Notifications: Not Started

Testing: In Progress

Deployment: Not Started

Documentation: Stable

---

## Current Technology Stack

Frontend: Next.js 14.2.x, React 18.3.x, TypeScript 5.3.x

Backend: Python 3.12+ target; validated on Python 3.13.2, FastAPI, Uvicorn

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset and news domain models/migrations added; real migration/seed blocked by local PostgreSQL authentication

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health, database foundation, asset model/schema/service/routes, asset seed command, news model/schema/service/routes tests pass; live database smoke testing remains blocked by local PostgreSQL authentication

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |   |-- versions/
|   |   |   |-- 20260625_0001_create_assets_table.py
|   |   |   `-- 20260625_0002_create_news_articles_table.py
|   |   |-- env.py
|   |   `-- script.py.mako
|   |-- app/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |       |-- assets.py
|   |   |       |-- health.py
|   |   |       |-- news.py
|   |   |       `-- router.py
|   |   |-- core/
|   |   |-- database/
|   |   |   |-- seed.py
|   |   |   |-- seed_assets.py
|   |   |   `-- seed_news.py
|   |   |-- models/
|   |   |   |-- asset.py
|   |   |   |-- associations.py
|   |   |   |-- mixins.py
|   |   |   `-- news.py
|   |   |-- schemas/
|   |   |   |-- asset.py
|   |   |   `-- news.py
|   |   |-- services/
|   |   |   |-- asset_service.py
|   |   |   `-- news_service.py
|   |   |-- utils/
|   |   `-- main.py
|   |-- tests/
|   |-- .env.example
|   |-- alembic.ini
|   |-- README.md
|   `-- requirements.txt
|-- ai-services/
|-- scrapers/
|-- shared/
|-- infrastructure/
|-- docs/
|-- AGENT.md
|-- PROJECT_STATE.md
|-- context.md
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, and Alembic migration scaffolding wired to application settings.

The asset foundation includes the asset domain model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation now includes the news article model, `asset_news` many-to-many association table, asset-news relationships, read-only service, read-only `/api/v1/news` API, development sample news data, and migration.

The news service queries the database when available and falls back to clearly marked development sample articles when PostgreSQL is unavailable. This keeps the foundation API testable before Sprint 009 scraper ingestion and before local database credentials are corrected.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, scrapers, notifications, or frontend integration.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 009 should introduce the web scraping engine foundation for investment news: create modular scraper interfaces and source-specific placeholders, normalization/deduplication contracts, article-to-asset linking workflow, and tests using fixtures. Do not implement AI, sentiment, embeddings, RAG, authentication, or frontend integration yet.

---

## Definition of Done

Sprint 008 is complete because:

* News model and asset-news relationship exist.
* News schemas, service, and read-only API routes exist.
* Development sample news data exists and is clearly marked as placeholder content.
* Migration for news tables exists.
* Tests pass without requiring live PostgreSQL.
* Health and news endpoints work on the current backend process using development fallback data while local PostgreSQL remains blocked.
* No scraper code, AI code, sentiment analysis, embeddings, RAG, authentication, or frontend integration was added.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 008 News Intelligence Foundation.

---

## Validation Results

* Tests: `python -m pytest` passed, 37 tests passed with one non-blocking pytest cache permission warning.
* Alembic: `python -m alembic current` exited successfully and loaded configuration; database revision lookup remains deferred because PostgreSQL authentication fails for the configured local development user.
* Server startup: `python -m uvicorn app.main:app --reload --port 8001` started the current backend successfully because local port `8000` remains occupied by PID `4288`.
* Health endpoint: `GET /api/v1/health` passed on `127.0.0.1:8001` and returned the expected success envelope.
* News list endpoint: `GET /api/v1/news?limit=2` passed on `127.0.0.1:8001` and returned development sample news through the fallback path.
* News detail endpoint: `GET /api/v1/news/1` passed on `127.0.0.1:8001` and returned a development sample article.
* Live PostgreSQL-backed news validation: deferred until valid local PostgreSQL credentials are configured and migrations are applied.
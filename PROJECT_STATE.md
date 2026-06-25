# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 011

Sprint Goal: Convert the dry-run ingestion pipeline into a production-ready backend ingestion adapter that safely validates normalized news payloads, detects duplicates, resolves asset relationships, supports DRY_RUN/WRITE modes, and persists records only through controlled transactions.

Current Tasks:

* [x] Created backend ingestion report schemas.
* [x] Created duplicate detection service for URL, normalized title, content hash, and published timestamp checks.
* [x] Created asset resolution service for active, missing, and inactive tickers.
* [x] Created backend ingestion service with dry-run and write-mode execution.
* [x] Added article-level transaction boundaries and rollback handling.
* [x] Added internal `POST /api/v1/ingestion/news` endpoint.
* [x] Added tests for duplicate detection, dry-run mode, write mode, rollback behavior, asset resolution, malformed payload rejection, missing assets, and route registration.
* [x] Updated backend README, project state, and context.
* [x] Added persisted `news_articles.content_hash` for scalable duplicate detection before Sprint 012.

Sprint Exit Criteria:

* Backend ingestion adapter exists.
* `news_articles.content_hash` is persisted, fixed-length, non-nullable, indexed, and unique.
* Duplicate service exists.
* Asset resolution service exists.
* Transaction boundaries are implemented.
* DRY_RUN mode works without database writes.
* WRITE mode works with SQLite test coverage.
* Duplicate prevention and rollback behavior are tested.
* News article duplicate detection uses a persisted indexed `content_hash`.
* Internal ingestion endpoint exists and is documented as non-public.
* Tests pass.
* Project state and context are updated.
---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, read-only news, and internal news ingestion endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: In Progress - fixture-only scraper contracts, placeholders, pipeline utilities, and dry-run ingestion orchestration exist; backend ingestion adapter can consume normalized payloads; real fetching not implemented

Analytics Engine: Not Started

AI/RAG: Not Started

Notifications: Not Started

Testing: In Progress - root pytest runs backend and scraper tests

Deployment: Not Started

Documentation: Stable

---

## Current Technology Stack

Frontend: Next.js 14.2.x, React 18.3.x, TypeScript 5.3.x

Backend: Python 3.12+ target; validated on Python 3.13.2, FastAPI, Uvicorn

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset and news domain models/migrations added; real migration/seed blocked by local PostgreSQL authentication

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, normalization, deduplication, asset linking, source trust scoring, and dry-run ingestion orchestration; no requests, Playwright, browser automation, external calls, scheduler, or DB writes yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 60 tests pass

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |-- tests/
|   |-- .env.example
|   |-- alembic.ini
|   |-- README.md
|   `-- requirements.txt
|-- scrapers/
|   |-- base_scraper.py
|   |-- fixtures.py
|   |-- run_dry_ingestion.py
|   |-- news/
|   |-- pipeline/
|   |   |-- asset_linker.py
|   |   |-- deduplicator.py
|   |   |-- ingestion_contract.py
|   |   |-- ingestion_orchestrator.py
|   |   |-- normalizer.py
|   |   `-- source_trust.py
|   |-- rbz/
|   |-- research/
|   |-- tests/
|   |-- vfex/
|   |-- zse/
|   `-- README.md
|-- ai-services/
|-- shared/
|-- infrastructure/
|-- docs/
|-- AGENT.md
|-- PROJECT_STATE.md
|-- context.md
|-- pytest.ini
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, and Alembic migration scaffolding wired to application settings.

The asset foundation includes the asset domain model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` many-to-many association table, asset-news relationships, read-only service, read-only `/api/v1/news` API, development sample news data, and migrations.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, normalization, deduplication, explicit asset linking, backend-compatible ingestion payloads, source trust scoring, and dry-run ingestion orchestration. The dry-run command reports what would be persisted but does not write to any database. The backend ingestion adapter now accepts normalized payloads, validates them, checks duplicates with URL and indexed content-hash lookups, resolves asset relationships, supports DRY_RUN and WRITE modes, and persists news records through article-level transaction boundaries.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The scraper layer intentionally contains no real HTTP fetching, browser automation, scheduling, sentiment, embeddings, RAG, or database persistence.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Real scraper fetching is not implemented by design and requires source-specific parsing, rate limiting, robots.txt review, and network policy decisions in a future sprint.
* Resolved: dry-run ingestion can now hand normalized payloads to the backend ingestion adapter; persistence is available only through explicit WRITE mode.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 012 should harden live PostgreSQL ingestion validation: fix local database credentials, run migrations including `20260625_0003_add_news_content_hash`, seed assets, exercise `POST /api/v1/ingestion/news` against PostgreSQL in DRY_RUN and WRITE modes, and confirm duplicate prevention with real persisted content hashes. Do not add live scraping, AI, scheduling, authentication, or frontend integration yet.

---

## Definition of Done

Sprint 011 is complete because:

* Backend ingestion adapter exists.
* `news_articles.content_hash` is persisted, fixed-length, non-nullable, indexed, and unique.
* Duplicate detection service exists.
* Asset resolution service exists.
* `INGESTION_MODE` supports `DRY_RUN` and `WRITE`, defaulting to `DRY_RUN`.
* Article-level transaction boundaries commit only after processing and roll back on failure.
* Internal `POST /api/v1/ingestion/news` endpoint exists and is documented as non-public.
* Tests cover duplicate detection, dry-run mode, write mode, rollback behavior, malformed payload rejection, missing/inactive assets, and route registration.
* `python -m pytest` passes from repository root.
* Project documentation is updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 011 backend news ingestion adapter.

---

## Validation Results

* Full repository tests: `python -m pytest` passed from repository root, 65 tests passed.
* Alembic load check: `python -m alembic current` from `backend/` loaded configuration successfully but deferred current revision lookup because PostgreSQL authentication failed for the configured local development user.
* Backend runtime: `python -m uvicorn app.main:app --reload --port 8001` started successfully; `Invoke-RestMethod -Uri http://127.0.0.1:8001/api/v1/health` returned `success=True`, `message=Backend is healthy`, `status=ok`, `version=0.1.0-alpha`.
* Ingestion dry-run/write validation: covered by SQLite-backed automated tests; no live PostgreSQL ingestion validation yet because credentials remain blocked.
* Content hash validation: tests verify deterministic hash generation, different-content hash changes, persisted hash metadata, stored-hash duplicate lookup, and ingestion hash persistence.
* Network safety: no live scraping, external HTTP requests, Playwright, Selenium, scheduler jobs, AI, sentiment, embeddings, RAG, frontend changes, or authentication were added.
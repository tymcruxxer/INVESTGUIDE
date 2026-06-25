# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 010

Sprint Goal: Build a dry-run news ingestion orchestration layer that runs fixture-only scraper sources, normalizes and deduplicates articles, links assets, assigns source-trust metadata, builds backend-compatible payloads, and reports what would be persisted without database writes or external network calls.

Current Tasks:

* [x] Created source trust metadata and tier scoring.
* [x] Created dry-run ingestion orchestrator.
* [x] Created dry-run report and payload contracts.
* [x] Created CLI command `python -m scrapers.run_dry_ingestion`.
* [x] Added tests for source trust scoring.
* [x] Added tests for dry-run orchestration success path.
* [x] Added tests for failed scraper handling.
* [x] Added tests for deduplication during orchestration.
* [x] Added tests for credibility score attachment and asset ticker linking.
* [x] Added tests for CLI command importability.
* [x] Verified no external network calls and no database writes are required.
* [x] Updated scraper README, project state, and context.

Sprint Exit Criteria:

* Source trust metadata exists.
* Dry-run orchestrator exists.
* Dry-run report exists.
* CLI dry-run command exists.
* Tests pass.
* No real network calls are made.
* No database writes occur.
* Project state and context are updated.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, and read-only news endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: In Progress - fixture-only scraper contracts, placeholders, pipeline utilities, and dry-run ingestion orchestration exist; real fetching not implemented

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

Testing: `python -m pytest` from repository root runs backend and scraper tests; 50 tests pass

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

The asset foundation includes the asset domain model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, `asset_news` many-to-many association table, asset-news relationships, read-only service, read-only `/api/v1/news` API, development sample news data, and migration.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, normalization, deduplication, explicit asset linking, backend-compatible ingestion payloads, source trust scoring, and dry-run ingestion orchestration. The dry-run command reports what would be persisted but does not write to any database.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The scraper layer intentionally contains no real HTTP fetching, browser automation, scheduling, sentiment, embeddings, RAG, or database persistence.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Real scraper fetching is not implemented by design and requires source-specific parsing, rate limiting, robots.txt review, and network policy decisions in a future sprint.
* Dry-run ingestion does not persist to the backend database by design.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 011 should implement a persistence-ready news ingestion adapter without enabling writes by default: map dry-run payloads to backend news/asset models, define duplicate lookup interfaces, add transaction boundaries behind an explicit dry-run/write switch, and keep tests database-free or SQLite-only until PostgreSQL credentials are fixed.

---

## Definition of Done

Sprint 010 is complete because:

* Source trust metadata exists.
* Dry-run orchestrator and dry-run report contracts exist.
* CLI dry-run command exists and prints a readable summary.
* Fixture scrapers are run through normalization, deduplication, asset linking, source trust scoring, and payload building.
* `python -m pytest` passes from repository root.
* `python -m scrapers.run_dry_ingestion` succeeds.
* No real network calls, database writes, scheduler jobs, AI, sentiment, embeddings, RAG, authentication, or frontend changes were added.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 010 dry-run news ingestion orchestration.

---

## Validation Results

* Scraper tests: `python -m pytest scrapers/tests` passed, 13 tests passed.
* Full repository tests: `python -m pytest` from repository root passed, 50 tests passed.
* Dry-run CLI: `python -m scrapers.run_dry_ingestion` passed and printed a readable ingestion summary for 8 fixture sources, 8 scraped articles, 0 duplicates, linked tickers, trust scores, and no errors.
* Network safety: tests monkeypatch `socket.create_connection`; all dry-run orchestration and placeholder scrapers pass without network calls.
* Database safety: scraper package contains no database engine/session usage and performs no database writes.
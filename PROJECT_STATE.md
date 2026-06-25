# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 009

Sprint Goal: Build the web scraping engine foundation for investment news without performing real web scraping, external website calls, database writes, AI, sentiment, embeddings, RAG, authentication, or frontend integration.

Current Tasks:

* [x] Created the base scraper interface and result/article contracts.
* [x] Created fixture-only placeholder scrapers for Financial Gazette, NewsDay Business, Herald Business, ZSE announcements, VFEX market data, RBZ macro data, IH Securities, and MMC Capital.
* [x] Created the normalization pipeline contract.
* [x] Created the deduplication pipeline contract.
* [x] Created the asset-linking contract using explicit keyword matching.
* [x] Created the ingestion payload contract compatible with backend `NewsCreate` semantics.
* [x] Added scraper tests that verify base behavior, fixtures, normalization, deduplication, asset linking, ingestion payloads, and no network calls.
* [x] Added root `pytest.ini` so `python -m pytest` runs backend and scraper tests from the repository root.
* [x] Updated scraper README, project state, and context.

Sprint Exit Criteria:

* Scraper base interface exists.
* Placeholder source scrapers exist.
* Normalization pipeline exists.
* Deduplication pipeline exists.
* Asset linker exists.
* Ingestion contract exists.
* Tests pass.
* No real external network calls are made.
* No database writes are made.
* Project state and context are updated.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, and read-only news endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: In Progress - foundation contracts and fixture-only placeholders exist; real fetching not implemented

Analytics Engine: Not Started

AI/RAG: Not Started

Notifications: Not Started

Testing: In Progress - root pytest now runs backend and scraper tests

Deployment: Not Started

Documentation: Stable

---

## Current Technology Stack

Frontend: Next.js 14.2.x, React 18.3.x, TypeScript 5.3.x

Backend: Python 3.12+ target; validated on Python 3.13.2, FastAPI, Uvicorn

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset and news domain models/migrations added; real migration/seed blocked by local PostgreSQL authentication

Scraping: Python dataclass-based scraper contracts and fixture-only placeholder source modules; no requests, Playwright, browser automation, external calls, scheduler, or DB writes yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 43 tests pass

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
|   |-- news/
|   |-- pipeline/
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

The scraper foundation now includes source-independent contracts, fixture-only source placeholders, normalization, deduplication, explicit asset linking, and a backend-compatible ingestion payload contract. Placeholder scrapers return local fixture articles only and do not call external websites or write to the database.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The scraper layer intentionally contains no real HTTP fetching, browser automation, scheduling, sentiment, embeddings, RAG, or database persistence.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Real scraper fetching is not implemented by design and requires source-specific parsing, rate limiting, robots.txt review, and network policy decisions in a future sprint.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 010 should implement the controlled news ingestion preparation layer: transform normalized scraper payloads into backend-compatible persistence commands, add duplicate-aware in-memory/dry-run ingestion orchestration, define source trust metadata, and keep execution dry-run only until PostgreSQL credentials and source-specific fetch rules are ready.

---

## Definition of Done

Sprint 009 is complete because:

* Base scraper contracts exist.
* Source-specific placeholder scrapers exist and return local fixtures only.
* Normalization, deduplication, asset linking, and ingestion contracts exist.
* Root test configuration exists for one-command validation.
* `python -m pytest` passes from repository root with backend and scraper tests.
* No real network calls, database writes, scheduler jobs, AI, sentiment, embeddings, RAG, authentication, or frontend changes were added.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 009 web scraping engine foundation.

---

## Validation Results

* Scraper tests: `python -m pytest scrapers/tests` passed, 6 tests passed.
* Backend tests: `python -m pytest` from `backend/` passed, 37 tests passed with one non-blocking pytest cache permission warning.
* Full repository tests: `python -m pytest` from repository root passed, 43 tests passed.
* Network safety: tests monkeypatch `socket.create_connection` and all placeholder scrapers pass without network calls.
* Database safety: scraper package contains no database engine/session usage and performs no database writes.
# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 018

Sprint Goal: Implement the backend foundation for user profiles and investor personalization without frontend onboarding, authentication, AI recommendations, or product recommendation features.

Current Tasks:

* [x] Created `docs/product/personalization-and-adaptive-intelligence.md` with the personalization and adaptive intelligence vision.
* [x] Added investor profile model foundation with nullable `user_id` placeholder for future auth.
* [x] Added investor profile Pydantic create, update, and read schemas.
* [x] Added personalization service rules for language complexity, metrics visibility, education depth, and explanation style.
* [x] Added Alembic migration for the `investor_profiles` table.
* [x] Added tests for model metadata, schema validation, personalization behavior, beginner defaults, advanced behavior, and migration registration.
* [x] Updated backend README, project state, and context documentation.
* [x] Ran full repository pytest suite successfully.

Sprint Exit Criteria:

* Product personalization document exists.
* Investor profile model exists.
* Schemas exist.
* Personalization service exists.
* Migration exists.
* Tests pass.
* No frontend onboarding, auth, AI, recommendations, portfolio tracking, watchlists, payments, live scraping, or scheduler work was added.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - SQLAlchemy/Alembic models exist for assets, news, content hashes, and investor personalization; local full DB validation is still blocked because Docker is not installed or not on PATH on this machine

Authentication: Not Started

API: In Progress - health, read-only assets, read-only news, and internal news ingestion endpoints exist; no investor profile routes are exposed yet

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Personalization: In Progress - product vision, investor profile model, schemas, migration, and backend personalization rule service exist; no frontend onboarding, auth integration, AI recommendations, or recommendation endpoints yet

Scrapers: In Progress - fixture-only scraper contracts, core scraper infrastructure, opt-in ZSE live scraper, dry-run orchestration, backend handoff preview, controlled backend submission, and DRY_RUN smoke path exist; live fetching remains disabled by default

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

Database: PostgreSQL 16 for local Docker development, PostgreSQL planned for hosted environments, SQLAlchemy 2.x, Alembic, psycopg 3

Developer Tooling: Docker Compose, `backend/scripts/dev.py`, `backend/scripts/bootstrap_dev.py`, `backend/scripts/check_database.py`

Personalization: SQLAlchemy investor profile model, Pydantic v2 schemas, deterministic backend rule service for presentation settings

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, `ScraperContext`, context factory, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, dry-run ingestion orchestration, backend handoff preview formatting, and controlled backend submission reporting

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 136 tests pass

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- scripts/
|   |-- tests/
|   |-- .env.example
|   |-- alembic.ini
|   |-- README.md
|   `-- requirements.txt
|-- scrapers/
|-- ai-services/
|-- shared/
|-- infrastructure/
|-- docs/
|   `-- product/
|-- docker-compose.yml
|-- AGENT.md
|-- PROJECT_STATE.md
|-- context.md
|-- pytest.ini
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository remains a modular monorepo. The frontend foundation is stable. The backend foundation is stable and includes reproducible local database infrastructure plus a single-command development launcher.

The asset foundation includes the asset model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` relationship, read-only service/API, development sample data, and backend ingestion adapter.

The personalization foundation includes the product personalization vision document, `InvestorProfile` model, Pydantic schemas, Alembic migration, and a pure personalization service that derives presentation settings. It intentionally exposes no routes and performs no AI recommendations or advisory logic.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend intentionally contains no authentication, users auth flow, investor profile routes, analytics engine, AI, notifications, portfolio tracking, watchlists, payments, or frontend integration.

---

## Current Blockers

* Docker is not installed or not available on PATH on this machine, so the full one-command launcher cannot start the Compose stack locally yet.
* Existing local PostgreSQL on port `5432` rejects the Compose development credentials for `investguide_user`, so bootstrap, diagnostics, Alembic revision lookup, and article-level DRY_RUN ingestion remain database-blocked until Docker PostgreSQL is available or credentials are corrected.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Full database-backed asset/news/profile validation is blocked until PostgreSQL is reachable, migrated, and seeded.
* Investor personalization is backend foundation only; frontend onboarding, auth linkage, profile API routes, AI recommendations, and adaptive dashboards are not implemented.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 019 should add read-only/internal investor profile service or API planning only after deciding the authentication boundary. Do not implement frontend onboarding, auth, AI recommendations, portfolio tracking, watchlists, payments, live scraping, or schedulers until explicitly requested.

---

## Definition of Done

Sprint 018 is complete because the product personalization document, investor profile backend model, schemas, personalization service, migration, tests, and documentation updates exist, and the full test suite passes.

---

## Last Updated

* Date: 2026-06-26
* AI Agent: Codex
* Completed Task: Completed Sprint 018 backend investor personalization foundation.

---

## Validation Results

* Tests: `python -m pytest` passed from repository root, 136 tests passed.
* Warning: pytest could not write its cache under `.pytest_cache` due Windows access denial; this did not fail tests.
* Git status: reviewed after documentation updates; working tree contains Sprint 017/017.1 and Sprint 018 changes pending commit.
# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 006

Sprint Goal: Configure a real development database workflow and add a controlled manual asset seed execution system.

Current Tasks:

* [x] Document local PostgreSQL setup.
* [x] Document hosted PostgreSQL setup.
* [x] Document required environment variables and `DATABASE_URL` workflow.
* [x] Document Alembic migration commands.
* [x] Document development asset seeding.
* [x] Update `.env.example` with `APP_NAME`, `APP_VERSION`, `APP_ENV`, `APP_DEBUG`, `DATABASE_URL`, and `CORS_ORIGINS`.
* [x] Add a manual duplicate-aware development asset seed command.
* [x] Add tests for seed data shape, ticker normalization, insert behavior, and duplicate prevention.
* [x] Validate pytest, Alembic load, uvicorn startup, and health endpoint.

Sprint Exit Criteria:

* `DATABASE_URL` workflow is clearly documented.
* Seed command exists and is manually run only.
* Seed command is duplicate-aware.
* Tests pass without requiring live PostgreSQL.
* Backend health endpoint still works.
* No automatic seeding occurs.
* Documentation is updated.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress

Authentication: Not Started

API: In Progress

Market Data: In Progress

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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset domain model and migration added; read-only asset API exists; manual duplicate-aware asset seed command exists

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health, database foundation, asset model, asset schema, asset service, asset routes, seed data, and seed command tests pass; frontend lint/type-check/build validation previously passes

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |   |-- versions/
|   |   |   `-- 20260625_0001_create_assets_table.py
|   |   |-- env.py
|   |   `-- script.py.mako
|   |-- app/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |       |-- assets.py
|   |   |       |-- health.py
|   |   |       `-- router.py
|   |   |-- core/
|   |   |-- database/
|   |   |   |-- seed.py
|   |   |   `-- seed_assets.py
|   |   |-- models/
|   |   |   |-- asset.py
|   |   |   `-- mixins.py
|   |   |-- schemas/
|   |   |   `-- asset.py
|   |   |-- services/
|   |   |   `-- asset_service.py
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
`-- README.md
```

---

## Current Architecture

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, Alembic migration scaffolding wired to application settings, the asset domain model/migration, read-only asset endpoints, and a controlled manual seed command for development assets.

The backend intentionally contains no authentication, users, asset write routes, analytics, AI, scrapers, notifications, or business workflow logic. Alembic can load the migration environment and asset revision; actual migration execution and real seed execution require a configured PostgreSQL `DATABASE_URL`.

---

## Current Blockers

* Real migration execution is blocked until valid local or hosted PostgreSQL credentials are configured.
* Real seed execution is blocked until `DATABASE_URL` points to a migrated PostgreSQL database.
* Live asset endpoint database testing is blocked until PostgreSQL credentials are configured, migrations are applied, and assets are seeded.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 007 should validate the real database workflow against a configured PostgreSQL instance: set `DATABASE_URL`, run `python -m alembic upgrade head`, run `python -m app.database.seed`, and smoke-test `GET /api/v1/assets` and `GET /api/v1/assets/{ticker}` against real seeded data. Do not add analytics, AI, scrapers, authentication, or frontend integration until the live database path is verified.

---

## Definition of Done

Sprint 006 is complete because:

* Local and hosted PostgreSQL setup instructions are documented.
* `DATABASE_URL`, migration, and seed workflows are documented.
* `.env.example` includes the required Sprint 006 environment variables without real credentials.
* The manual command `python -m app.database.seed` exists.
* The seed command inserts missing assets and skips duplicate tickers.
* Seed tests pass without requiring live PostgreSQL.
* Backend health endpoint still works.
* No automatic seeding, frontend changes, auth, asset writes, analytics, AI, scrapers, notifications, or deployment work was added.
* Documentation is updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 006 development database workflow documentation and manual duplicate-aware asset seed command with tests and validation.

---

## Validation Results

* Backend tests: passed with `python -m pytest` from `backend/`; 24 tests passed. Pytest emitted a non-blocking cache-write warning in this sandbox.
* Alembic load: passed with `python -m alembic current`; PostgreSQL revision lookup was deferred because local database credentials are not configured.
* Server startup: passed with `python -m uvicorn app.main:app --reload` from `backend/`.
* Health endpoint: passed with `GET http://127.0.0.1:8000/api/v1/health`.
* Runtime: uvicorn started without startup errors; health endpoint returned the expected success envelope.
* Real migration and seed execution: deferred until `DATABASE_URL` points to a valid PostgreSQL database.
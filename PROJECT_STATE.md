# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 007

Sprint Goal: Validate the backend against a real PostgreSQL development database and smoke-test asset read endpoints with real seeded data.

Current Tasks:

* [x] Checked local PostgreSQL availability.
* [x] Created local `backend/.env` from `.env.example` without committing credentials.
* [x] Added `backend/.env` to `.gitignore` so local credentials cannot be committed accidentally.
* [x] Set a local development `DATABASE_URL` placeholder in ignored `.env`.
* [x] Ran live migration and seed validation commands.
* [x] Smoke-tested health and asset routes against the current backend process.
* [x] Documented blockers preventing real migration, seed, and seeded endpoint success.
* [x] Reviewed Sprint 007 repository changes before commit.
* [x] Categorized repository-safe changes and local-only files.
* [x] Confirmed `backend/.env` is ignored and untracked.
* [x] Revalidated tests, Alembic configuration loading, backend startup, and health endpoint.

Sprint Exit Criteria:

* Real PostgreSQL connection is configured locally or setup blocker is clearly documented.
* Migration runs successfully, or blocker is clearly documented.
* Seed command runs successfully, or blocker is clearly documented.
* Asset endpoints are tested against seeded data, or blocker is clearly documented.
* No credentials are committed.
* Project state and context are updated.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - blocked on valid local PostgreSQL credentials

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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset domain model and migration added; read-only asset API exists; manual duplicate-aware asset seed command exists; real migration/seed blocked by local PostgreSQL authentication

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health, database foundation, asset model, asset schema, asset service, asset routes, seed data, and seed command tests pass; live database smoke testing blocked by local PostgreSQL authentication

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
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, Alembic migration scaffolding wired to application settings, the asset domain model/migration, read-only asset endpoints, and a controlled manual seed command for development assets.

Sprint 007 validated the workflow far enough to confirm a PostgreSQL listener is available at `localhost:5432`, but the configured local development database user is not authenticated. Migration, seed execution, and live seeded asset endpoint tests remain blocked until valid PostgreSQL credentials/database/user are configured.

The backend intentionally contains no authentication, users, asset write routes, analytics, AI, scrapers, notifications, or business workflow logic.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live asset endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and assets are seeded.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 008 should resolve the remaining local database blocker: install/expose PostgreSQL client tools, create or verify the `investguide_dev` database and application user, update ignored `backend/.env` with valid local credentials, rerun `python -m alembic upgrade head`, rerun `python -m app.database.seed`, and smoke-test asset endpoints against seeded data.

---

## Definition of Done

Sprint 007 is complete with blockers documented because:

* Local `.env` was created from `.env.example` and ignored by git.
* `DATABASE_URL` was set for a local development attempt without committing credentials.
* Migration command was run and reached PostgreSQL, but failed authentication.
* Seed command was run and failed on the same authentication blocker.
* Health endpoint passed on the current backend process.
* Asset list/detail endpoints were smoke-tested on the current backend process and failed only because database authentication is blocked.
* Minimal workflow fixes were made for CORS dotenv parsing and `.env` git safety.
* Project state and context are updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 007 repository review before commit, categorized repository versus local-only changes, applied a minimal CORS settings parser correction, and revalidated backend checks.

---

## Validation Results

* Git review: `git status --short` shows only repository-safe tracked changes: `.gitignore`, `PROJECT_STATE.md`, `backend/README.md`, `backend/app/core/config.py`, and `context.md`.
* Local-only files: `backend/.env` exists for local development validation, is ignored by `.gitignore`, and is not tracked by git.
* Repository review: no credentials, hardcoded local filesystem paths, machine-specific assumptions, frontend changes, or feature additions were found in Sprint 007 changes.
* Config review: `CORS_ORIGINS` supports comma-separated dotenv values and documented JSON-array strings using explicit settings parsing.
* Tests: `python -m pytest` passed, 24 tests passed with one non-blocking pytest cache permission warning.
* Alembic: `python -m alembic current` exited successfully and loaded configuration; database revision lookup remains deferred because PostgreSQL authentication fails for the configured local development user.
* Server startup: `python -m uvicorn app.main:app --reload` was run; port `8000` still has a persistent local listener on PID `4288`, so current-app smoke testing was verified on alternate port `8001`.
* Health endpoint: `GET /api/v1/health` passed on `127.0.0.1:8001` and returned the expected success envelope.
* Migration/seed/live seeded assets: still blocked until valid PostgreSQL credentials and database/user setup are available.
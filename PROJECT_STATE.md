# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 017.1

Sprint Goal: Add a single-command backend developer launcher on top of the Sprint 017 Docker/bootstrap workflow.

Current Tasks:

* [x] Added `python backend/scripts/dev.py` as the one-command backend development launcher.
* [x] Added Docker installed and Docker daemon checks with clear failure messages.
* [x] Added Docker Compose startup, PostgreSQL wait, bootstrap delegation, and Uvicorn launch flow.
* [x] Added `--no-server`, `--port`, `--skip-docker`, and `--skip-bootstrap` flags.
* [x] Added mocked tests for Docker failures, command construction, wait behavior, bootstrap delegation, Uvicorn startup, and flag behavior.
* [x] Updated root and backend documentation with launcher workflow, flags, common errors, and safety notes.
* [x] Validated automated tests and real missing-Docker launcher behavior.
* [ ] Validate full one-command launch after Docker is installed or available on PATH.

Sprint Exit Criteria:

* `backend/scripts/dev.py` exists.
* One-command development workflow is documented.
* Missing Docker and stopped Docker daemon cases fail clearly.
* Launcher can start Docker Compose, bootstrap the backend, and start Uvicorn when Docker/PostgreSQL are available.
* Tests pass without Docker.
* No product features, frontend changes, auth, AI, analytics, scraping, scheduler, WRITE mode, new database models, or destructive database reset commands are added.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - SQLAlchemy/Alembic models, Docker Compose workflow, bootstrap script, diagnostics script, and one-command dev launcher exist; local full validation is blocked because Docker is not installed or not on PATH on this machine

Authentication: Not Started

API: In Progress - health, read-only assets, read-only news, and internal news ingestion endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

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

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, `ScraperContext`, context factory, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, dry-run ingestion orchestration, backend handoff preview formatting, and controlled backend submission reporting

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 122 tests pass

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |-- scripts/
|   |   |-- bootstrap_dev.py
|   |   |-- check_database.py
|   |   `-- dev.py
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

The repository remains a modular monorepo. The frontend foundation is stable. The backend foundation is stable and now includes reproducible local database infrastructure plus a single-command development launcher. The launcher coordinates Docker checks, Compose startup, PostgreSQL readiness, bootstrap migrations/seeding, and Uvicorn startup without adding app startup side effects or destructive database behavior.

The asset foundation includes the asset model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` relationship, read-only service/API, development sample data, and backend ingestion adapter.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The launcher intentionally does not enable WRITE ingestion mode, schedulers, scrapers, live scraping, AI, or analytics jobs.

---

## Current Blockers

* Docker is not installed or not available on PATH on this machine, so the full one-command launcher cannot start the Compose stack locally yet.
* Existing local PostgreSQL on port `5432` rejects the Compose development credentials for `investguide_user`, so bootstrap, diagnostics, Alembic revision lookup, and article-level DRY_RUN ingestion remain database-blocked until Docker PostgreSQL is available or credentials are corrected.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Real seed execution is blocked until PostgreSQL credentials match the configured `DATABASE_URL` and migrations are applied.
* Full database-backed asset/news endpoint validation is blocked until PostgreSQL is reachable, migrated, and seeded.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 018 should install/enable Docker Desktop or another Docker Compose runtime, rerun `python backend/scripts/dev.py --no-server`, then run `python backend/scripts/dev.py --port 8001` and verify backend health plus DRY_RUN ingestion without PostgreSQL authentication errors. Do not enable WRITE mode, schedulers, authentication, AI, or frontend integration yet.

---

## Definition of Done

Sprint 017.1 is implemented in repository code because the launcher, flags, tests, and documentation exist. Full local runtime acceptance is pending host Docker availability.

---

## Last Updated

* Date: 2026-06-26
* AI Agent: Codex
* Completed Task: Added Sprint 017.1 one-command backend developer launcher and documented the Docker host blocker.

---

## Validation Results

* Tests: `python -m pytest` passed from repository root, 122 tests passed.
* Launcher validation: `python backend/scripts/dev.py --no-server` failed clearly because Docker is not installed or not available on PATH.
* Docker-backed launch: not run because Docker is unavailable on this machine.
* Product safety: no frontend changes, API features, auth, AI, analytics, scraping, scheduler, WRITE mode, new models, destructive database commands, or database reset behavior were added.
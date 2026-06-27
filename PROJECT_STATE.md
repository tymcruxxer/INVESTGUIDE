# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 020

Sprint Goal: Establish authentication and user identity so investor profiles can attach to real users instead of the temporary first-profile development behavior.

Current Tasks:

* [x] Added `User` SQLAlchemy model with unique email, optional username, hashed password, active/verified flags, and timestamps.
* [x] Added bcrypt password hashing and verification through `passlib`.
* [x] Added JWT creation and validation through `python-jose` with `sub`, `email`, and `exp` claims.
* [x] Added `POST /api/v1/auth/signup`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`.
* [x] Added reusable `get_current_user` and optional current-user auth dependencies.
* [x] Linked `InvestorProfile.user_id` to `users.id` and resolved profiles by authenticated user.
* [x] Preserved development-only profile fallback when `APP_ENV=development` and no auth token is supplied.
* [x] Added Alembic migration for `users` and investor profile foreign key/unique ownership.
* [x] Added tests for auth service, auth routes, user model, migration registration, and auth-aware investor profile behavior.
* [x] Updated backend README, PROJECT_STATE.md, and context.md.

Sprint Exit Criteria:

* User model exists.
* Signup, login, and current-user endpoints exist.
* JWT authentication and password hashing work.
* Investor profiles are user-owned when authenticated.
* Development fallback remains limited to development mode.
* Tests pass with 170+ tests.
* Frontend, AI, recommendations, analytics, scrapers, scheduler, portfolio, watchlists, payments, and notifications remain unchanged.
---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - SQLAlchemy/Alembic models exist for assets, news, content hashes, and investor personalization; local full DB validation is still blocked because Docker is not installed or not on PATH on this machine

Authentication: In Progress - basic user model, bcrypt password hashing, JWT signup/login/me endpoints, and current-user dependency exist

API: In Progress - health, auth signup/login/me, read-only assets, read-only news, internal news ingestion, and auth-aware investor profile endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Personalization: In Progress - product vision, investor profile model, schemas, migration, service layer, seed data, and create/read/update API endpoints exist; profiles now bind to authenticated users with a development-only fallback; no frontend onboarding, AI recommendations, or adaptive dashboards yet

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

Personalization: SQLAlchemy investor profile model, Pydantic v2 schemas, deterministic backend service for profile CRUD and presentation settings, versioned FastAPI profile endpoints

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, `ScraperContext`, context factory, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, dry-run ingestion orchestration, backend handoff preview formatting, and controlled backend submission reporting

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 182 tests pass

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- api/v1/
|   |   |-- database/
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

The personalization foundation includes the product personalization vision document, `InvestorProfile` model, Pydantic schemas, Alembic migration, service layer, demo seed data, and authentication-independent create/read/update API endpoints. Authenticated profile requests resolve by `investor_profiles.user_id`; unauthenticated requests use the first-row development fallback only when `APP_ENV=development`.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend now contains a basic JWT authentication foundation and user/profile linkage. It intentionally contains no AI recommendation engine, analytics engine, notifications, portfolio tracking, watchlists, payments, RBAC, OAuth, MFA, email verification, or frontend onboarding integration.

---

## Current Blockers

* Docker is not installed or not available on PATH on this machine, so the full one-command launcher cannot start the Compose stack locally yet.
* Existing local PostgreSQL on port `5432` rejects the Compose development credentials for `investguide_user`, so bootstrap, diagnostics, Alembic revision lookup, and article-level DRY_RUN ingestion remain database-blocked until Docker PostgreSQL is available or credentials are corrected.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Full database-backed auth/asset/news/profile validation is blocked until PostgreSQL is reachable, migrated, and seeded.
* Frontend onboarding, AI recommendations, adaptive dashboards, portfolio tracking, watchlists, payments, live scraping, and schedulers remain intentionally unimplemented.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Architectural Backlog

* Future enhancement: introduce an `AuthContext` object after authentication-dependent services begin to grow. It should mirror the existing `ScraperContext` pattern and bundle authenticated user state such as `user`, JWT claims, investor profile, permissions, feature flags, locale, onboarding completion, and future tenant/organization data. Protected services should eventually accept one context object rather than several separate auth-related parameters. This is intentionally not implemented in Sprint 020.

---
## Next Immediate Task

Sprint 021 should add protected user-owned profile hardening or begin frontend auth integration only after confirming the UX boundary. Do not implement AI recommendations, portfolio tracking, watchlists, payments, live scraping, or schedulers yet.

---

## Definition of Done

Sprint 020 is complete because the authentication foundation, JWT signup/login/me endpoints, user model, user-owned investor profile linkage, tests, and documentation updates exist, and the full repository test suite passes.

---

## Last Updated

* Date: 2026-06-27
* AI Agent: Codex
* Completed Task: Completed Sprint 020 Authentication and User Identity Foundation.

---

## Validation Results

* Tests: `python -m pytest` passed from repository root, 182 tests passed.
* Warning: pytest could not write its cache under `.pytest_cache` due Windows access denial; this did not fail tests.
* Alembic: `python -m alembic current` loaded configuration and deferred revision lookup because local PostgreSQL rejects `investguide_user` credentials.
* Runtime: `python -m uvicorn app.main:app --reload --port 8001` started successfully.
* Health smoke: `GET /api/v1/health` returned success with `database: unavailable` and `migrations: unavailable`.
* Auth smoke: `GET /api/v1/auth/me` without token returned 401 envelope; `POST /api/v1/auth/signup` reached the auth service but failed with the existing PostgreSQL password authentication blocker.





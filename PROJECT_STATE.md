# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 033.1

Sprint Goal: Fix the local Docker/PostgreSQL/backend runtime setup so InvestGuide can be manually tested end to end against a real PostgreSQL database.

Current Tasks:

* [x] Inspected `backend/.env` for UTF-8 BOM.
* [x] Removed BOM and rewrote `backend/.env` as UTF-8 without BOM.
* [x] Confirmed Docker Compose credentials match backend settings.
* [x] Identified port `5432` conflict with a non-Docker `postgres.exe` process.
* [x] Remapped Docker PostgreSQL host port from `5432` to `5433`.
* [x] Updated `docker-compose.yml`, `backend/.env`, and `backend/.env.example`.
* [x] Restarted Docker PostgreSQL with `docker compose down -v` and `docker compose up -d`.
* [x] Applied Alembic migrations and ran unified development seed.
* [x] Smoke-tested backend health, assets, companies, company profile, and assessment endpoints.
* [x] Ran Python tests and frontend lint/type-check/build.
* [x] Started frontend with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api/v1` and verified requested routes return 200.
* [x] Updated backend README, frontend README, PROJECT_STATE.md, and context.md.

Sprint Exit Criteria:

* Local Docker PostgreSQL is reachable from the backend.
* Migrations apply successfully.
* Seed data runs successfully.
* Backend smoke endpoints pass against PostgreSQL.
* Frontend validation passes.
* Frontend browser routes are reachable.
* No product features or architecture changes are added beyond local runtime repair.

---
## Module Status

Frontend: In Progress - auth/login/signup pages, onboarding flow, protected shell, backend-connected dashboard, asset explorer, asset detail, company page with backend-first CompanyProfile loading, explicit Development Preview fallback, news sections, comparison page, and search routing exist

Backend: Stable - FastAPI starts without reload and health endpoint works; DB-backed routes remain dependent on reachable PostgreSQL

Database: Stable Locally - Docker PostgreSQL 16 runs on host port `5433`, migrations apply, seed data loads, and diagnostics report database connected/current

Authentication: In Progress - backend JWT foundation and frontend login/signup/session hydration exist; database connectivity is now available for manual auth validation

API: In Progress - health, auth signup/login/me, investor profile, read-only assets, read-only companies, company profiles, read-only news, asset/company assessments, and internal news ingestion endpoints exist; frontend now consumes assets/news/profile/company APIs where available

Market Data: In Progress - asset domain/API foundation exists and Company Intelligence now links issuers to assets, news, assessments, and persisted-or-preview structured enrichment profiles; real market data ingestion not implemented

Personalization: In Progress - backend investor profile APIs exist and frontend onboarding now captures experience, goals, asset preferences, risk, horizon, planned range, and language preference; no AI recommendations or adaptive dashboards yet

Scrapers: In Progress - fixture-only scraper contracts, core scraper infrastructure, opt-in ZSE live scraper, dry-run orchestration, backend handoff preview, controlled backend submission, and DRY_RUN smoke path exist; live fetching remains disabled by default

Analytics Engine: In Progress - centralized analytics package foundation exists with engine, registry, context, result object, score contracts, explanation layer, exceptions, versioning, docs, and tests; no real calculations yet

AI/RAG: Not Started

Notifications: Not Started

Testing: Stable - root pytest passes backend/scraper tests; frontend lint, type-check, and build pass

Deployment: Not Started

Documentation: Stable - Sprint 033.1 local PostgreSQL runtime fix documentation added

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

Testing: frontend lint/type-check/build pass; `python -m pytest` from repository root runs backend and scraper tests with 194 tests passing

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

The repository remains a modular monorepo. The frontend foundation now includes client-side authentication, onboarding, session hydration, route protection, backend-connected dashboard data, asset exploration, asset detail views, news display, and asset comparison with explicit demo fallback. The backend foundation is stable and includes reproducible local database infrastructure plus a single-command development launcher.

The asset foundation includes the asset model, migration, development seed command, read-only service, and read-only API. Sprint 031 adds Company Intelligence as an issuer-level layer above assets with `companies`, `company_news`, `assets.company_id`, read-only company APIs, company detail frontend page, related assets, related news, and assessment reuse. Sprint 032 adds Company Intelligence Enrichment with `company_profiles`, source transparency, research status, fixture-backed structured facts, and `/companies/{ticker}/profile`. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` relationship, read-only service/API, development sample data, and backend ingestion adapter.

The personalization foundation includes the product personalization vision document, `InvestorProfile` model, Pydantic schemas, Alembic migration, service layer, demo seed data, and authentication-independent create/read/update API endpoints. Authenticated profile requests resolve by `investor_profiles.user_id`; unauthenticated requests use the first-row development fallback only when `APP_ENV=development`.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend contains a basic JWT authentication foundation and user/profile linkage. The frontend now contains login, signup, onboarding, auth state, and client-side protected navigation. The product intentionally contains no AI recommendation engine, real analytics calculations, notifications, portfolio tracking, watchlists, payments, RBAC, OAuth, MFA, email verification, or production auth hardening.

---

## Current Blockers

* Local non-Docker PostgreSQL still listens on host port `5432`; InvestGuide Docker PostgreSQL intentionally uses host port `5433` to avoid the conflict.
* Backend API examples using `DELTA` return 404 because the canonical seeded ticker is `DLTA`; an alias/slug strategy is not implemented yet.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH, but Docker `psql` works inside the `investguide-postgres` container.
* AI recommendations, adaptive dashboards, portfolio tracking, watchlists, payments, live scraping, and schedulers remain intentionally unimplemented.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---
## Architectural Backlog

* Future enhancement: introduce an `AuthContext` object after authentication-dependent services begin to grow. It should mirror the existing `ScraperContext` pattern and bundle authenticated user state such as `user`, JWT claims, investor profile, permissions, feature flags, locale, onboarding completion, and future tenant/organization data. Protected services should eventually accept one context object rather than several separate auth-related parameters. This is intentionally not implemented in Sprint 020.
* Future enhancement: move auth orchestration into a dedicated `AuthProvider` once auth behavior grows beyond the current MVP client-side flow. The provider should manage login, logout, hydration, redirects, onboarding status, auth loading state, future session refresh, roles, subscription plans, premium gates, and feature flags, while Zustand stores current state.
* Future production security enhancement: replace localStorage JWT persistence with a stronger auth model after backend database validation is stable. Candidate direction: HTTP-only cookies, refresh tokens, CSRF protection, and silent token refresh. LocalStorage remains acceptable for the MVP and is documented as a limitation.
* Future developer-experience enhancement: add a development-only internal diagnostics endpoint such as `GET /api/v1/system/status` to report database connectivity, migration status, scraper enablement, ingestion mode, environment status, and PostgreSQL/Docker readiness without exposing secrets. This should remain disabled or protected outside development.
* Future developer-experience enhancement: add a lightweight `python backend/scripts/doctor.py` command that checks Docker availability, PostgreSQL connectivity, Alembic revision, required environment variables, seed status, and API health, then prints a simple pass/fail report.
* Future architecture documentation enhancement: add `docs/product/data-flow.md` to explain how information moves through InvestGuide across news ingestion, scraper normalization, deduplication, storage, analytics, AI, frontend delivery, onboarding personalization, portfolio analytics, macro outlooks, education, learning, roadmaps, and financial health.
* Future architecture documentation enhancement: add `docs/architecture/system-map.md` as the one-platform diagram covering frontend, backend, AI layer, analytics engine, scrapers, PostgreSQL, future vector database, future cache, authentication, and background workers.
* Future analytics architecture enhancement: introduce an `AnalyticsPipeline` execution layer when analytics modules need dependency ordering, caching, parallel execution, timeout handling, partial failures, execution metrics, or audit logging. This should preserve `AnalyticsEngine` as the orchestration layer while letting execution behavior evolve independently.

---
## Next Immediate Task

Manual end-to-end product testing can now proceed against Docker PostgreSQL on port `5433`, backend on port `8001`, and frontend on port `3000`. Next implementation sprint should validate signup/login/onboarding/profile persistence through the browser before adding new product modules.

---
## Definition of Done

Sprint 033.1 is complete because the UTF-8 BOM was removed from `backend/.env`, Docker PostgreSQL was remapped to host port `5433` to avoid the local PostgreSQL conflict on `5432`, migrations and seed data completed successfully, backend smoke endpoints passed against PostgreSQL, frontend validation passed, and requested frontend routes returned 200.

---
## Last Updated

* Date: 2026-07-06
* AI Agent: Codex
* Completed Task: Completed Sprint 033.1 local Docker/PostgreSQL/backend runtime repair and validation.

---
## Validation Results

* BOM check: `backend/.env` previously began with `EF BB BF`; it now begins with `41 50 50` and reports `NO_BOM`.
* Final `DATABASE_URL`: `postgresql+psycopg://investguide_user:investguide_password@localhost:5433/investguide`.
* Port check: host port `5432` has Docker internals plus a separate `postgres.exe`; Docker PostgreSQL now maps `5433:5432`.
* Docker restart: `docker compose down -v` and `docker compose up -d` passed.
* Container health: `investguide-postgres` running and healthy on `0.0.0.0:5433->5432/tcp`.
* Container psql: `docker exec investguide-postgres psql -U investguide_user -d investguide` passed.
* Migrations: `python -m alembic upgrade head` passed through revision `20260703_0001`.
* Seed: `python -m app.database.seed` passed.
* Diagnostics: `python backend/scripts/check_database.py` passed, database connected, migrations current, seed data present, asset count 9.
* Seed counts: 9 assets, 9 companies, 4 company profiles, 1 investor profile.
* Backend smoke: `/health`, `/assets`, `/companies`, `/companies/DLTA/profile`, and `/assets/DLTA/assessment` passed on `http://127.0.0.1:8001/api/v1`.
* Backend note: `/companies/DELTA/profile` and `/assets/DELTA/assessment` return 404 because canonical ticker is `DLTA`.
* Tests: `python -m pytest -q` passed, 225 tests passed, 1 non-blocking pytest cache permission warning.
* Frontend lint: `npm.cmd run lint` passed.
* Frontend type-check: `npm.cmd run type-check` passed.
* Frontend build: `npm.cmd run build` passed, 14 routes generated.
* Frontend route smoke: `/auth/signup`, `/auth/login`, `/onboarding`, `/dashboard`, `/assets`, `/company/delta`, and `/compare` returned HTTP 200 from the Next.js dev server.
---

## Stabilization Update - Authentication and Test Suite

Date: 2026-07-06

Completed:

* Pinned bcrypt to `>=4.0.1,<4.1.0` for compatibility with `passlib==1.7.4`.
* Verified installed versions: `bcrypt==4.0.1`, `passlib==1.7.4`.
* Verified password hashing and verification behavior with bcrypt.
* Hardened route registration tests to inspect only FastAPI route objects that expose `.path`.
* Updated frontend auth API fallback to `http://127.0.0.1:8001/api/v1`.
* Updated signup/login network error handling to show a clear backend-unreachable message.
* Fixed landing page auth navigation from `/auth/register` to `/auth/signup`.
* Updated local CORS defaults to include `http://127.0.0.1:3000`.
* Polished the public frontend palette toward dark navy, slate cards, blue primary actions, teal accent, and high-contrast text.

Validation:

* `python -m pytest -q`: passed before the final no-BOM rewrite with 174 tests passed and 1 non-blocking pytest cache permission warning. Final rerun was blocked by the execution sandbox approval layer.
* Password hash smoke: passed (`hash_password`, valid password verification, invalid password rejection).
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed and generated 14 routes.
* Backend health on `http://127.0.0.1:8001/api/v1/health`: reachable, but reported database unavailable.
* `python backend/scripts/check_database.py`: failed because PostgreSQL on `localhost:5433` timed out.
* `docker compose ps`: failed due Docker Desktop engine API error.

Known Runtime Blocker:

* Manual signup/login cannot be honestly confirmed until Docker/PostgreSQL is reachable again. Backend starts and health responds, but database-backed auth requests cannot complete while PostgreSQL times out.
---

## Stabilization Update - Local CORS

Date: 2026-07-06

Completed:

* Added local frontend fallback origins `http://localhost:3001` and `http://127.0.0.1:3001` to backend CORS configuration.
* Updated `backend/.env`, `backend/.env.example`, and backend CORS defaults.
* Verified `OPTIONS /api/v1/auth/signup` from `Origin: http://localhost:3001` returns `Access-Control-Allow-Origin: http://localhost:3001`.

Validation:

* `python -m pytest -q`: passed, 174 tests passed, 1 non-blocking pytest cache permission warning.
* CORS preflight for signup from `http://localhost:3001`: passed.
---

## Stabilization Update - Permanent CORS/Auth Connectivity Fix

Date: 2026-07-07

Completed:

* Diagnosed CORS/auth connectivity for frontend origin `http://localhost:3001` and backend `http://127.0.0.1:8001`.
* Confirmed `CORS_ORIGINS` is configured in `backend/.env` and parsed into a list of four origins.
* Made backend settings load from an absolute `backend/.env` path instead of a working-directory-relative `.env` path.
* Added startup diagnostics for APP_ENV, masked DATABASE_URL, parsed CORS_ORIGINS, CORSMiddleware installation, and middleware order.
* Confirmed middleware order is `CORSMiddleware` before `RequestLoggingMiddleware` and routers are included after middleware registration.
* Added CORS regression tests for parsing and auth preflight from `http://localhost:3001`.
* Verified signup and login succeed with `Origin: http://localhost:3001`.

Validation:

* Startup logs show APP_ENV `development`, masked PostgreSQL URL on `localhost:5433`, CORS origins as a Python list, CORSMiddleware installed, and middleware order `['CORSMiddleware', 'RequestLoggingMiddleware']`.
* `OPTIONS /api/v1/auth/signup`: HTTP 200, `Access-Control-Allow-Origin: http://localhost:3001`, allowed methods include POST, allowed headers include content-type.
* `OPTIONS /api/v1/auth/login`: HTTP 200 with the same CORS headers.
* Signup smoke: passed.
* Login smoke: passed.
* `python -m pytest -q`: passed, 177 tests passed, 1 non-blocking pytest cache warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.
---

## Sprint 034 Update - World-Class UI/UX Redesign and Auth UX Polish

Date: 2026-07-07

Completed:

* Added cohesive premium design-system utilities for cards, inputs, buttons, badges, success, warning, and error states.
* Redesigned landing page with a premium fintech hero, platform metrics, featured companies, benefit cards, how-it-works cards, and polished CTA/footer.
* Redesigned signup with validation, password visibility, password strength, friendly existing-account messaging, and a dedicated account-created success state before onboarding.
* Redesigned login with premium layout, password visibility, and friendly error handling.
* Polished public layout, sidebar, navbar/search, onboarding surfaces, dashboard cards, roadmap, warning states, and shared page card treatments.
* Preserved existing frontend/backend architecture and API contracts.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed, 177 tests passed, 1 non-blocking pytest cache warning.
* Runtime auth smoke: blocked by PostgreSQL timeout on `localhost:5433`; backend CORS works, but database-backed signup/login cannot complete until local PostgreSQL is reachable.
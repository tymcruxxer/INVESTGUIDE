# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 026

Sprint Goal: Build the Analytics Engine Foundation as the centralized architecture for future asset intelligence, portfolio intelligence, AI assistant context, news intelligence, comparison engine, opportunity radar, financial health, and future recommendation systems.

Current Tasks:

* [x] Created `backend/app/analytics/` package structure.
* [x] Added `AnalyticsContext` for asset, historical prices, news, macro data, financial statements, user profile, and metadata inputs.
* [x] Added `AnalyticsResult` standard output object.
* [x] Added `BaseAnalytics` abstract architecture and metadata contract.
* [x] Added analytics registry with register, unregister, calculate, calculate_all, and metadata support.
* [x] Added `AnalyticsEngine` with centralized execution, aggregation, warning collection, and version metadata.
* [x] Added purpose-only score modules for quality, growth, dividend, value, liquidity, risk, macro, and confidence.
* [x] Added deterministic explanation layer.
* [x] Added analytics exceptions and version constants.
* [x] Added analytics engine architecture documentation.
* [x] Added analytics foundation tests.
* [x] Updated README.md, PROJECT_STATE.md, and context.md.
* [x] Ran backend tests and frontend lint/type-check/build validation.

Sprint Exit Criteria:

* Analytics package exists.
* Analytics engine exists.
* Registry exists.
* Base analytics class exists.
* Context exists.
* Result object exists.
* Explanation layer exists.
* Exceptions exist.
* Architecture document exists.
* Tests pass.
* No real calculations, AI, recommendations, portfolio analytics, macro calculations, frontend charts, comparisons, or predictions are implemented.

---

## Module Status

Frontend: In Progress - auth/login/signup pages, onboarding flow, auth state hydration, and client-side protected shell exist; Sprint 024 route smoke passed on the Next.js dev server

Backend: Stable - FastAPI starts without reload and health endpoint works; DB-backed routes remain dependent on reachable PostgreSQL

Database: Blocked Locally - SQLAlchemy/Alembic models exist for assets, news, content hashes, users, and investor personalization; Docker is not installed or not on PATH, and local PostgreSQL rejects the configured development credentials for `investguide_user`

Authentication: In Progress - backend JWT foundation and frontend login/signup/session hydration exist; live signup/login remains blocked locally by PostgreSQL authentication failure

API: In Progress - health, auth signup/login/me, read-only assets, read-only news, internal news ingestion, and auth-aware investor profile endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Personalization: In Progress - backend investor profile APIs exist and frontend onboarding now captures experience, goals, asset preferences, risk, horizon, planned range, and language preference; no AI recommendations or adaptive dashboards yet

Scrapers: In Progress - fixture-only scraper contracts, core scraper infrastructure, opt-in ZSE live scraper, dry-run orchestration, backend handoff preview, controlled backend submission, and DRY_RUN smoke path exist; live fetching remains disabled by default

Analytics Engine: In Progress - centralized analytics package foundation exists with engine, registry, context, result object, score contracts, explanation layer, exceptions, versioning, docs, and tests; no real calculations yet

AI/RAG: Not Started

Notifications: Not Started

Testing: In Progress - root pytest passes backend/scraper tests; frontend lint, type-check, and build pass

Deployment: Not Started

Documentation: Stable - Sprint 026 analytics engine architecture documentation added

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

Testing: frontend lint/type-check/build pass; `python -m pytest` from repository root runs backend and scraper tests with 184 tests passing

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

The repository remains a modular monorepo. The frontend foundation now includes client-side authentication, onboarding, session hydration, and route protection. The backend foundation is stable and includes reproducible local database infrastructure plus a single-command development launcher.

The asset foundation includes the asset model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` relationship, read-only service/API, development sample data, and backend ingestion adapter.

The personalization foundation includes the product personalization vision document, `InvestorProfile` model, Pydantic schemas, Alembic migration, service layer, demo seed data, and authentication-independent create/read/update API endpoints. Authenticated profile requests resolve by `investor_profiles.user_id`; unauthenticated requests use the first-row development fallback only when `APP_ENV=development`.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend contains a basic JWT authentication foundation and user/profile linkage. The frontend now contains login, signup, onboarding, auth state, and client-side protected navigation. The product intentionally contains no AI recommendation engine, analytics engine, notifications, portfolio tracking, watchlists, payments, RBAC, OAuth, MFA, email verification, or production auth hardening.

---

## Current Blockers

* Docker is not installed or not available on PATH on this machine, so the full one-command launcher cannot start the Compose stack locally yet.
* Existing local PostgreSQL on port `5432` rejects the Compose development credentials for `investguide_user`, so bootstrap, diagnostics, Alembic revision lookup, and article-level DRY_RUN ingestion remain database-blocked until Docker PostgreSQL is available or credentials are corrected.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Full database-backed auth/asset/news/profile validation is blocked until PostgreSQL is reachable, migrated, and seeded.
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

Sprint 027 should choose a narrow analytics/data implementation layer. Recommended: add historical price data models and ingestion-ready context builders, then implement the first real low-risk analytics calculation only after data availability is established. Do not implement AI recommendations yet.

---

## Definition of Done

Sprint 026 is complete because the analytics package, engine, registry, base analytics contract, context, result object, explanation layer, exceptions, score module architecture, versioning, architecture documentation, tests, and project memory updates exist, and validation passes without real financial calculations or product feature expansion.

---

## Last Updated

* Date: 2026-07-02
* AI Agent: Codex
* Completed Task: Completed Sprint 026 Analytics Engine Foundation.

---

## Validation Results

* Backend/scraper tests: `python -m pytest` passed from repository root, 194 tests passed.
* Focused analytics tests: `python -m pytest backend/tests/test_analytics_foundation.py` passed, 10 tests passed.
* Frontend lint: `npm.cmd run lint` passed with no ESLint warnings or errors.
* Frontend type-check: `npm.cmd run type-check` passed.
* Frontend build: `npm.cmd run build` passed and generated 12 app routes including `/auth/login`, `/auth/signup`, and `/onboarding`.
* Warning: pytest could not write its cache under `.pytest_cache` due Windows access denial; this did not fail tests.
* Runtime limitation remains: fully persisted signup/login/onboarding/profile reload is still blocked until Docker is available or local PostgreSQL credentials/database are corrected.

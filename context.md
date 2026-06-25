# Project Overview

InvestGuide is an AI-powered Zimbabwean investment intelligence platform. Its mission is to bridge the gap between institutional-grade financial intelligence and everyday Zimbabwean investors by transforming fragmented ZSE, VFEX, REIT, macroeconomic, news, sentiment, and research information into understandable, educational, analytics-driven insights.

InvestGuide is an educational decision-support and market intelligence platform. It is not a brokerage, automated trading bot, speculative prediction engine, portfolio manager, or licensed financial advisor.

---

# Project Health

Frontend: Stable

Backend: Not Started

Database: Not Started

AI Services: Not Started

Scrapers: Not Started

Analytics: Not Started

Testing: Minimal

Deployment: Not Started

Documentation: Excellent

---

# Current Sprint

Sprint Number: Sprint 001

Goal: Establish frontend foundation stability and permanent AI-agent project memory.

Tasks:

* [x] Analyze repository architecture and implementation status.
* [x] Fix frontend lint and build blockers.
* [x] Create `context.md` as project memory.
* [x] Create `AGENT.md` as permanent AI-agent operating manual.
* [x] Update `context.md` into the required living engineering log structure.
* [ ] Build backend foundation under `backend/`.
* [ ] Add a backend health endpoint and global response envelope.

Exit Criteria:

* Frontend lint passes.
* Frontend type-check passes.
* Frontend production build passes.
* `AGENT.md` exists and captures permanent agent rules.
* `context.md` exists and captures project health, sprint state, session history, architecture, known issues, and next task.

---

# Session History

## Session 001

Date: 2026-06-25

Objective: Analyze the repository, fix frontend lint/build blockers, and create initial project continuity memory.

Completed:

* Repository analyzed and current implementation state identified.
* Frontend lint and build blockers fixed while preserving existing architecture and routing.
* Frontend `metadata.viewport` warning fixed by moving viewport configuration to the dedicated Next.js `viewport` export.
* Initial `context.md` created for continuity between AI-agent sessions.

Files Created:

* `context.md`

Files Modified:

* `frontend/app/layout.tsx`
* `frontend/app/assets/[ticker]/page.tsx`
* `frontend/components/layout/app-shell.tsx`
* `frontend/components/layout/navbar.tsx`
* `frontend/hooks/index.ts`
* `frontend/providers/theme-provider.tsx`
* `frontend/store/index.ts`

Architectural Decisions:

* Preserve Next.js 14.x and React 18.x.
* Preserve frontend App Router routing structure.
* Keep lint fixes minimal by removing unused imports, marking placeholder args with underscore prefixes, and fixing observer cleanup.
* Move viewport configuration to the supported Next.js `viewport` export.

Validation Results:

* Lint: passed with `npm.cmd run lint`.
* Type-check: passed with `npm.cmd run type-check`.
* Build: passed with `npm.cmd run build`.
* Tests: no dedicated test suite implemented.
* Runtime: production build succeeded; no dev server smoke test was running.

Next Recommended Task:

* Build the backend foundation under `backend/`.

---

## Session 002

Date: 2026-06-25

Objective: Establish mandatory AI-agent operating manual and update project memory structure.

Completed:

* Read `README.md`, existing `context.md`, and all markdown documentation under `docs/`.
* Confirmed `docs/ai/ai-agent-rules.md` currently exists but is empty.
* Created `AGENT.md` as the permanent operating manual for future AI agents.
* Updated `context.md` to include project health, current sprint, session history, current architecture, repository structure, validation status, and next recommended task.

Files Created:

* `AGENT.md`

Files Modified:

* `context.md`

Architectural Decisions:

* Treat `AGENT.md` as the permanent engineering operating manual.
* Treat `context.md` as the living project memory and engineering log.
* Preserve protected stack decisions: Next.js 14.x, React 18.x, FastAPI, PostgreSQL, TailwindCSS, Zustand, TanStack Query, Framer Motion, modular monorepo, analytics-first architecture, and educational-not-broker positioning.

Validation Results:

* Lint: passed with `npm.cmd run lint`.
* Type-check: passed with `npm.cmd run type-check`.
* Build: passed with `npm.cmd run build`.
* Tests: no test script is currently defined in `frontend/package.json`.
* Runtime: no dev server/runtime smoke test was run.

Next Recommended Task:

* Build the backend foundation under `backend/` with FastAPI, config, health endpoint, CORS, and global response envelope.

---

# Current Architecture

* Frontend: Next.js App Router scaffold exists under `frontend/`; core pages, AppShell, Sidebar, Navbar, theme provider, Zustand stores, TanStack Query provider, Axios API client, shared types, utility helpers, and skeleton states are present. Pages are mostly static placeholders/skeletons and are not yet wired to backend data.
* Backend: `backend/` exists as an architectural folder but has no implemented FastAPI application yet.
* Database: PostgreSQL schema and relationships are documented, but no database models, migrations, seed data, runtime DB connection, or repository layer are implemented.
* AI: AI/RAG architecture is documented; `ai-services/` exists but no AI orchestration, prompts, retrieval, embeddings, validation layer, or model integration are implemented.
* Scrapers: scraping pipeline and source strategy are documented; `scrapers/` exists but no source-specific scraper modules are implemented.
* Analytics: formulas and scoring strategy are documented; no analytics engine modules are implemented yet.

---

# Completed Work

* Repository analyzed and current implementation state identified.
* Frontend lint and build blockers fixed while preserving existing architecture and routing.
* Frontend `metadata.viewport` warning fixed.
* Initial `context.md` created.
* `AGENT.md` created as permanent AI-agent operating manual.
* `context.md` updated into the required living memory and engineering log structure.

---

# Files Created

* `context.md`
* `AGENT.md`

---

# Files Modified

* `context.md`
* `frontend/app/layout.tsx`
* `frontend/app/assets/[ticker]/page.tsx`
* `frontend/components/layout/app-shell.tsx`
* `frontend/components/layout/navbar.tsx`
* `frontend/hooks/index.ts`
* `frontend/providers/theme-provider.tsx`
* `frontend/store/index.ts`

---

# Architectural Decisions

* Monorepo structure follows documented folders: `frontend/`, `backend/`, `ai-services/`, `scrapers/`, `shared/`, `docs/`, and `infrastructure/`.
* Frontend framework: Next.js App Router, currently installed as Next.js 14.2.x.
* React version: React 18.3.x.
* TypeScript remains strict with frontend path aliases using `@/*` from the frontend root.
* Styling: TailwindCSS with CSS-variable theme tokens; dark mode is default with a `.light` class override.
* UI direction: fintech dashboard shell with AppShell, Sidebar, Navbar, skeleton loading states, Framer Motion, and Lucide icons.
* State/data choices: Zustand for auth/theme/UI client state; TanStack Query for server state; Axios for API requests.
* API standard: frontend client assumes a versioned backend at `/api/v1` and a global response envelope with `success`, `message`, `data`, and optional `meta`.
* AI safety/product positioning: platform must remain educational analysis, not financial advice; AI outputs should be grounded, cite sources, and acknowledge uncertainty once implemented.
* Permanent project memory policy: read `README.md`, `context.md`, and relevant `docs/` markdown before implementation; update `context.md` after every completed task.

---

# Known Issues

* Unresolved: Backend, database, AI services, analytics, scrapers, shared package, and infrastructure are not implemented yet.
* Unresolved: Frontend pages still use placeholder skeletons/mock behavior and are not connected to real APIs.
* Unresolved: Auth store methods are TODO stubs.
* Unresolved: AI Assistant page returns a simulated placeholder response.
* Unresolved: No dedicated automated test suite is currently present beyond lint/type-check/build validation.
* Unresolved: Documentation contains encoding artifacts from converted documents.
* Unresolved: `docs/ai/ai-agent-rules.md` exists but is empty.
* Unresolved: Root git status previously showed a deleted Word temp lock file: `docs/~$vestGuide_Technical_Planning.docx`; confirm before committing if it reappears.
* Resolved: Frontend lint and production build blockers from unused imports, unused placeholder variables, hook cleanup warning, and unsupported metadata viewport configuration.

---

# Current Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|-- ai-services/
|-- scrapers/
|-- shared/
|-- infrastructure/
|-- docs/
|-- context.md
|-- AGENT.md
`-- README.md
```

---

# Next Recommended Task

Build the backend foundation: create a minimal FastAPI application under `backend/` with configuration, health endpoint, CORS setup, global response envelope, and an initial module structure aligned to the documented architecture.

---

# Validation Results

* Lint: passed with `npm.cmd run lint`.
* Type-check: passed with `npm.cmd run type-check`.
* Tests: no test script is currently defined in `frontend/package.json`.
* Build: passed with `npm.cmd run build`.
* Runtime: no dev server/runtime smoke test was run; production build completed successfully.

---

# Session Summary

Created `AGENT.md` as the permanent AI-agent operating manual and updated `context.md` into the requested living memory structure. The update preserves previous frontend stabilization history, records current project health, defines the current sprint, captures known issues, and points the next agent toward backend foundation work.



---

## Session 003

Date: 2026-06-25

Objective: Establish `PROJECT_STATE.md` as the current source of truth, improve `AGENT.md`, audit repository health, and record validation without changing application code.

Completed:

* Read `README.md`, `AGENT.md`, `context.md`, and markdown documentation under `docs/` before making changes.
* Confirmed `PROJECT_STATE.md` did not exist and created it as the current-state source of truth.
* Improved `AGENT.md` with coding standards, validation requirements, documentation update requirements, context management rules, and definition of done.
* Performed repository audit for folder structure, documentation consistency, architecture consistency, package versions, placeholder folders, and empty documentation.
* Confirmed frontend validation passes.

Files Created:

* `PROJECT_STATE.md`

Files Modified:

* `AGENT.md`
* `context.md`
* `PROJECT_STATE.md`

Repository Audit Findings:

* Folder structure: documented top-level monorepo folders exist: `frontend/`, `backend/`, `ai-services/`, `scrapers/`, `shared/`, `infrastructure/`, and `docs/`.
* Implementation status: `frontend/` contains the only implemented application layer; backend, AI services, scrapers, shared, and infrastructure folders are placeholders with no implemented files.
* Documentation consistency: architecture, technical planning, startup, and PRD markdown files exist and align on modular monorepo, analytics-first architecture, FastAPI/PostgreSQL backend plan, and AI-as-explanation positioning.
* Empty documentation: `docs/ai/ai-agent-rules.md` exists but is empty.
* Package versions: frontend currently uses Next.js `^14.2.5`, React `^18.3.1`, TypeScript `^5.3.3`, TailwindCSS `^3.4.1`, Zustand `^4.4.7`, TanStack Query `^5.28.0`, Framer Motion `^10.16.16`, and Axios `^1.7.7`.
* Architecture consistency: current implementation is consistent with a frontend foundation stage; planned backend/database/AI/scraping/analytics layers are documented but not implemented.
* Testing gap: no dedicated `test` script exists in `frontend/package.json`.

Architectural Decisions:

* `PROJECT_STATE.md` is the current source of truth for active software state.
* `context.md` remains the historical engineering log and should be appended to, not rewritten.
* `AGENT.md` remains the permanent operating manual for future AI agents.
* No package versions, application code, routing, backend code, APIs, or architecture were changed.

Known Issues Update:

* Unresolved: Backend foundation is not implemented.
* Unresolved: Database models, migrations, and runtime connection are not implemented.
* Unresolved: Frontend data workflows remain blocked by missing backend APIs.
* Unresolved: `docs/ai/ai-agent-rules.md` is empty.
* Unresolved: Dedicated test suites are not implemented.

Validation Results:

* Lint: passed with `npm.cmd run lint`.
* Type-check: passed with `npm.cmd run type-check`.
* Build: passed with `npm.cmd run build`.
* Tests: no test script is currently defined in `frontend/package.json`.
* Runtime: no dev server/runtime smoke test was run; production build completed successfully.

Next Recommended Task:

* Build the backend foundation under `backend/`: create a minimal FastAPI application with configuration, CORS setup, health endpoint, global response envelope, and initial folder/module structure aligned to the documented architecture.

---

## Session 004

Date: 2026-06-25

Objective: Complete Sprint 002 by building only the backend foundation for future InvestGuide modules.

Completed:

* Read `README.md`, `AGENT.md`, `PROJECT_STATE.md`, `context.md`, and relevant markdown documentation under `docs/` before implementation.
* Created FastAPI backend foundation under `backend/app`.
* Added environment-based configuration using `pydantic-settings`.
* Added centralized logging configuration.
* Added SQLAlchemy 2.x declarative base and session factory for future PostgreSQL-backed modules.
* Added versioned API router under `/api/v1`.
* Added `GET /api/v1/health` endpoint returning the documented response envelope.
* Added reusable success/error response envelope helpers.
* Added HTTP, validation, and unhandled exception handlers.
* Added CORS middleware, request logging middleware, and `X-Process-Time` response header.
* Added backend requirements, `.env.example`, README, and health endpoint test.
* Fixed a configuration collision by using `APP_DEBUG` instead of generic `DEBUG`, because the host environment had `DEBUG=release`.
* Validated dependency installation, test suite, uvicorn startup, and live health endpoint response.

Files Created:

* `backend/app/__init__.py`
* `backend/app/api/__init__.py`
* `backend/app/api/v1/__init__.py`
* `backend/app/api/v1/health.py`
* `backend/app/api/v1/router.py`
* `backend/app/core/__init__.py`
* `backend/app/core/config.py`
* `backend/app/core/logging.py`
* `backend/app/core/responses.py`
* `backend/app/core/exceptions.py`
* `backend/app/core/middleware.py`
* `backend/app/database/__init__.py`
* `backend/app/database/base.py`
* `backend/app/database/session.py`
* `backend/app/models/__init__.py`
* `backend/app/schemas/__init__.py`
* `backend/app/services/__init__.py`
* `backend/app/utils/__init__.py`
* `backend/app/main.py`
* `backend/tests/__init__.py`
* `backend/tests/test_health.py`
* `backend/requirements.txt`
* `backend/.env.example`
* `backend/README.md`

Files Modified:

* `PROJECT_STATE.md`
* `context.md`

Architectural Decisions:

* Backend app uses a factory function `create_app()` and exposes `app = create_app()` for uvicorn.
* API routes are versioned under `/api/v1` from the first backend commit.
* Response envelopes are centralized in `app/core/responses.py` for future endpoint reuse.
* Exception handlers return the same envelope shape for HTTP, validation, and unhandled errors.
* SQLAlchemy infrastructure is initialized without business models to keep Sprint 002 foundation-only.
* Configuration uses `pydantic-settings` and environment variables; `APP_DEBUG` is used instead of `DEBUG` to avoid host environment collisions.
* No authentication, business APIs, analytics, AI, scrapers, notifications, or business logic were implemented.

Validation Results:

* `python -m pip install -r requirements.txt`: passed.
* `python -m pytest`: passed, 1 test collected and passed.
* `python -m uvicorn app.main:app --reload`: passed; server started without startup errors.
* `GET http://127.0.0.1:8000/api/v1/health`: passed and returned `{ "success": true, "message": "Backend is healthy", "data": { "status": "ok", "version": "0.1.0-alpha" } }`.
* Runtime cleanup: uvicorn validation session exited after health check; Windows briefly reported a stale listener PID that no longer existed by process lookup.

Known Issues Update:

* Resolved: Backend foundation was not implemented.
* Unresolved: Database models, Alembic migrations, and seed data are not implemented.
* Unresolved: Authentication is not implemented.
* Unresolved: Business APIs for assets, market data, watchlists, analytics, AI, and notifications are not implemented.
* Unresolved: Frontend pages remain mostly placeholders pending backend business APIs.
* Unresolved: `docs/ai/ai-agent-rules.md` is empty.

Sprint Summary:

* Sprint 002 completed the backend foundation only. The backend now has production-oriented FastAPI infrastructure and a verified health endpoint, while intentionally avoiding all business feature implementation.

Next Recommended Task:

* Sprint 003: implement the initial database and Alembic foundation, including Alembic configuration, migration environment, model conventions, and the first asset schema/model plan without adding business API features yet.

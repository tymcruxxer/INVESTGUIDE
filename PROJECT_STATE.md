# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 005

Sprint Goal: Implement the backend asset read API foundation with safe read-only endpoints using the existing asset model and schemas.

Current Tasks:

* [x] Add read-only asset service functions for list and ticker lookup.
* [x] Support asset filtering by exchange, sector, asset type, status, and search query.
* [x] Support page/limit pagination for asset listing.
* [x] Add `GET /api/v1/assets` endpoint.
* [x] Add `GET /api/v1/assets/{ticker}` endpoint.
* [x] Return standard response envelopes for asset success and not-found responses.
* [x] Register asset routes under `/api/v1/assets`.
* [x] Add tests for route registration, list response shape, detail not-found response, and service filtering.
* [x] Keep tests independent of live PostgreSQL credentials.
* [x] Update backend README, project state, and historical context.
* [x] Validate pytest, Alembic load, uvicorn startup, and health endpoint.

Sprint Exit Criteria:

* Read-only asset routes exist.
* Routes are registered under `/api/v1/assets`.
* Asset service layer exists.
* Response envelope is used consistently.
* Tests pass without requiring live PostgreSQL.
* Backend health endpoint still works.
* No create, update, or delete endpoints are added.
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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset domain model and migration added; read-only asset API uses SQLAlchemy sessions

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health, database foundation, asset model, asset schema, asset service, asset routes, and seed data tests pass; frontend lint/type-check/build validation previously passes

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

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, Alembic migration scaffolding wired to application settings, the asset domain model/migration, and read-only asset endpoints.

The backend intentionally contains no authentication, users, asset write routes, analytics, AI, scrapers, notifications, or business workflow logic. Alembic can load the migration environment and asset revision; actual migration execution and live asset endpoint database testing are deferred until PostgreSQL credentials are configured.

---

## Current Blockers

* Database migration execution is blocked until valid local or hosted PostgreSQL credentials are configured.
* Live asset endpoint database testing is blocked until PostgreSQL credentials are configured and the assets migration is applied.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 006 should configure a real local or hosted PostgreSQL development database, apply the existing Alembic migration, and add a controlled seed execution workflow for development assets. Do not add analytics, AI, scrapers, authentication, or frontend integration until the live database path is validated.

---

## Definition of Done

Sprint 005 is complete because:

* Read-only asset service functions exist for listing assets and ticker lookup.
* Asset list supports exchange, sector, asset type, status, search, page, and limit inputs.
* `GET /api/v1/assets` and `GET /api/v1/assets/{ticker}` are registered under the versioned API router.
* Asset responses use the existing response envelope.
* Missing ticker responses return a 404 error envelope.
* Tests pass without requiring live PostgreSQL.
* Backend health endpoint still works.
* No create, update, delete, auth, analytics, AI, scraper, or frontend work was added.
* Documentation is updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 005 asset read API foundation with service filtering, read-only routes, tests, validation, and documentation updates.

---

## Validation Results

* Backend tests: passed with `python -m pytest` from `backend/`; 20 tests passed. Pytest emitted a non-blocking cache-write warning in this sandbox.
* Alembic load: passed with `python -m alembic current`; PostgreSQL revision lookup was deferred because local database credentials are not configured.
* Server startup: passed with `python -m uvicorn app.main:app --reload` from `backend/`.
* Health endpoint: passed with `GET http://127.0.0.1:8000/api/v1/health`.
* Runtime: uvicorn started without startup errors; health endpoint returned the expected success envelope.
* Live asset endpoint database testing: deferred until PostgreSQL credentials are configured and the assets migration is applied.
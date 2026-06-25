# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 004

Sprint Goal: Implement the first real backend domain model layer for investment assets without exposing business API endpoints.

Current Tasks:

* [x] Add the SQLAlchemy asset model.
* [x] Add explicit asset domain value sets for exchanges, asset types, currencies, and statuses.
* [x] Add Pydantic v2 asset schemas.
* [x] Register the asset model for Alembic metadata discovery.
* [x] Add a manual Alembic migration for the assets table.
* [x] Add development-only seed data structure for initial Zimbabwean assets.
* [x] Add tests for asset model metadata, schemas, enum values, and seed data.
* [x] Update backend README, project state, and historical context.
* [x] Validate pytest, Alembic load, uvicorn startup, and health endpoint.

Sprint Exit Criteria:

* Asset model exists.
* Asset schemas exist.
* Alembic migration exists.
* Seed data structure exists and does not run automatically.
* Tests pass without requiring a live database.
* Backend health endpoint still works.
* No asset business endpoints are exposed.
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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; first asset domain model and migration added

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health, database foundation, asset model, asset schema, and seed data tests pass; frontend lint/type-check/build validation previously passes

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
|   |   |-- core/
|   |   |-- database/
|   |   |   `-- seed_assets.py
|   |   |-- models/
|   |   |   |-- asset.py
|   |   |   `-- mixins.py
|   |   |-- schemas/
|   |   |   `-- asset.py
|   |   |-- services/
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

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, Alembic migration scaffolding wired to application settings, and the first asset domain model/migration.

The backend intentionally contains no authentication, users, asset CRUD routes, analytics, AI, scrapers, notifications, or business workflow logic. Alembic can load the migration environment and asset revision; actual migration execution is deferred until PostgreSQL credentials are configured.

---

## Current Blockers

* Database migration execution is blocked until valid local or hosted PostgreSQL credentials are configured.
* Frontend data workflows are blocked by missing business APIs.
* Asset UI/API workflows are blocked because asset CRUD/list/detail endpoints are not implemented yet.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 005 should implement the backend asset repository/service/API read foundation: list assets and retrieve asset detail through `/api/v1/assets`, using the existing response envelope and asset schemas, without authentication, analytics, AI, scraping, or frontend changes.

---

## Definition of Done

Sprint 004 is complete because:

* The asset SQLAlchemy model exists with deterministic indexes, unique ticker constraint, timestamp mixin, and explicit domain value sets.
* Pydantic v2 asset schemas exist for create, update, and read shapes.
* The asset model is registered for Alembic metadata discovery.
* The first assets-table Alembic migration exists.
* Development seed data exists and does not run automatically.
* Tests pass without requiring a live database.
* The backend health endpoint still works.
* No business API endpoints were exposed.
* Documentation is updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 004 asset domain model foundation with SQLAlchemy model, Pydantic schemas, migration, seed structure, tests, validation, and documentation updates.

---

## Validation Results

* Backend tests: passed with `python -m pytest` from `backend/`; 13 tests passed. Pytest emitted a non-blocking cache-write warning in this sandbox.
* Alembic load: passed with `python -m alembic current`; PostgreSQL revision lookup was deferred because local database credentials are not configured.
* Server startup: passed with `python -m uvicorn app.main:app --reload` from `backend/`.
* Health endpoint: passed with `GET http://127.0.0.1:8000/api/v1/health`.
* Runtime: uvicorn started without startup errors; health endpoint returned the expected success envelope.
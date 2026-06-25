# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 003

Sprint Goal: Implement the backend database and Alembic foundation only, without business API features.

Current Tasks:

* [x] Add Alembic configuration under `backend/`.
* [x] Configure Alembic to load existing SQLAlchemy `Base.metadata`.
* [x] Add deterministic database naming conventions.
* [x] Add timestamp mixin/model convention foundation.
* [x] Add placeholder model import registry for future Alembic autogeneration.
* [x] Add database foundation tests.
* [x] Update backend README with migration commands.
* [x] Validate pytest, Alembic load, uvicorn startup, and health endpoint.

Sprint Exit Criteria:

* Alembic is installed and configured.
* SQLAlchemy Base metadata is migration-ready.
* Naming conventions exist for deterministic migrations.
* Backend health endpoint still works.
* Tests pass.
* Documentation is updated.
* No business models or business API features are implemented.

---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress

Authentication: Not Started

API: In Progress

Market Data: Not Started

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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; no business models or migrations yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health and database foundation tests pass; frontend lint/type-check/build validation passes

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |   |-- versions/
|   |   |-- env.py
|   |   `-- script.py.mako
|   |-- app/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |-- core/
|   |   |-- database/
|   |   |-- models/
|   |   |   `-- mixins.py
|   |   |-- schemas/
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

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation now includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, and Alembic migration scaffolding wired to application settings.

The backend intentionally contains no authentication, users, assets, market APIs, analytics, AI, scrapers, notifications, or business logic. Alembic can load the migration environment; actual migration execution is deferred until PostgreSQL credentials are configured.

---

## Current Blockers

* Frontend data workflows are blocked by missing business APIs.
* Database-backed features are blocked by missing business models, migrations, and seed data.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 004 should implement the first real database domain model layer: asset schema/model and initial Alembic migration planning, without exposing business APIs until the data model and migration are validated.

---

## Definition of Done

Sprint 003 is complete because:

* Alembic is configured under `backend/`.
* SQLAlchemy Base metadata is migration-ready.
* Deterministic naming conventions exist.
* Timestamp mixin/model conventions exist.
* Backend health endpoint still works.
* Tests pass.
* Documentation is updated.
* No business features were implemented.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 003 database and Alembic foundation with metadata conventions, mixins, tests, validation, and documentation updates.

---

## Validation Results

* Backend tests: passed with `python -m pytest` from `backend/`.
* Alembic load: passed with `python -m alembic current`; PostgreSQL revision lookup was deferred because local database credentials are not configured.
* Server startup: passed with `python -m uvicorn app.main:app --reload` from `backend/`.
* Health endpoint: passed with `GET http://127.0.0.1:8000/api/v1/health`.
* Runtime: uvicorn started without startup errors; health endpoint returned the expected success envelope.

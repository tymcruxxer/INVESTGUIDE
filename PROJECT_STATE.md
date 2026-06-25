# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 002

Sprint Goal: Build the backend foundation only, without business features.

Current Tasks:

* [x] Create FastAPI backend package under `backend/app`.
* [x] Add environment-based configuration with `pydantic-settings`.
* [x] Add centralized logging.
* [x] Add SQLAlchemy 2.x database base and session factory.
* [x] Add versioned `/api/v1` API router.
* [x] Add `GET /api/v1/health` endpoint.
* [x] Add reusable global response envelope helpers.
* [x] Add global exception handlers.
* [x] Add CORS, request logging, and processing-time middleware.
* [x] Add backend README, `.env.example`, requirements, and health test.
* [x] Validate install, server startup, live health endpoint, and pytest.

Sprint Exit Criteria:

* Backend starts with `python -m uvicorn app.main:app --reload`.
* `GET /api/v1/health` returns the documented success envelope.
* Configuration is environment-based.
* Database base/session infrastructure exists.
* Response envelope helpers exist.
* Logging exists.
* Middleware exists.
* Health test passes with `python -m pytest`.
* No authentication, business APIs, analytics, AI, scrapers, or notifications are implemented.

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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; no models or migrations yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: Backend health test exists and passes; frontend lint/type-check/build validation passes

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |-- core/
|   |   |-- database/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- utils/
|   |   `-- main.py
|   |-- tests/
|   |-- .env.example
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

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is now implemented as a FastAPI application with versioned routing, environment settings, logging, middleware, exception handling, response envelope helpers, SQLAlchemy base/session infrastructure, and a health endpoint.

The backend intentionally contains no authentication, users, assets, market APIs, analytics, AI, scrapers, notifications, or business logic. Database models and migrations are not implemented yet.

---

## Current Blockers

* Frontend data workflows are blocked by missing business APIs.
* Database-backed features are blocked by missing models, migrations, and seed data.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated frontend/backend CI is not implemented.

---

## Next Immediate Task

Sprint 003 should implement the initial database and Alembic foundation: Alembic configuration, migration environment, core SQLAlchemy model conventions, and the first schema/model plan for assets without adding business endpoints beyond foundation-level database setup.

---

## Definition of Done

Sprint 002 is complete because:

* Backend starts successfully.
* Health endpoint works.
* Configuration is environment-based.
* Database base/session layer is initialized.
* Response envelope exists.
* Logging exists.
* Middleware exists.
* Tests pass.
* Documentation is updated.
* No business features were implemented.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 002 backend foundation with FastAPI infrastructure, health endpoint, tests, validation, and documentation updates.

---

## Validation Results

* Dependency install: passed with `python -m pip install -r requirements.txt` from `backend/`.
* Server startup: passed with `python -m uvicorn app.main:app --reload` from `backend/`.
* Health endpoint: passed with `GET http://127.0.0.1:8000/api/v1/health`.
* Backend tests: passed with `python -m pytest` from `backend/`.
* Runtime: uvicorn started without startup errors; health endpoint returned the expected success envelope.

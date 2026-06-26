# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 015

Sprint Goal: Implement a controlled backend submission workflow that can submit scraper output to the backend ingestion endpoint only when explicitly enabled, with OFF as the default and WRITE mode gated by live-mode confirmation.

Current Tasks:

* [x] Added reusable backend submission client.
* [x] Added OFF, DRY_RUN, and WRITE submission modes.
* [x] Added backend submission configuration through `BACKEND_SUBMISSION_MODE`, `BACKEND_URL`, and `BACKEND_API_VERSION`.
* [x] Added `SubmissionReport` for accepted, rejected, duplicate, warning, error, backend timing, and request timing results.
* [x] Added controlled CLI command for backend submission reporting.
* [x] Enforced WRITE downgrade to DRY_RUN unless `SCRAPER_LIVE_ENABLED=true` is also set.
* [x] Added mocked tests for modes, request construction, retry handling, response parsing, and no-network default behavior.
* [x] Updated scraper, backend, project state, and context documentation.

Sprint Exit Criteria:

* Backend submission client exists.
* OFF mode works and is default.
* DRY_RUN mode works through mocked transport.
* WRITE mode requires explicit enablement.
* Backend submission report exists.
* CLI command exists.
* Tests pass.
* No automatic persistence occurs.
* Documentation is updated.
---
## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, read-only news, and internal news ingestion endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: In Progress - fixture-only scraper contracts, placeholders, core scraper infrastructure, `ScraperContext` dependency injection, pipeline utilities, dry-run ingestion orchestration, one opt-in ZSE live announcements scraper, ZSE live validation checklist, backend handoff preview adapter, and controlled backend submission client exist; live fetching is disabled by default and submission defaults to OFF

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

Database: PostgreSQL planned; SQLAlchemy 2.x base/session configured; Alembic configured; asset and news domain models/migrations added; real migration/seed blocked by local PostgreSQL authentication

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, `ScraperContext`, context factory, source registry, source config, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, dry-run ingestion orchestration, backend handoff preview formatting, and controlled backend submission reporting; one opt-in ZSE live scraper exists but is disabled by default; no Playwright, browser automation, scheduler, automatic backend posting, or scraper DB writes yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 98 tests pass

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |-- tests/
|   |-- .env.example
|   |-- alembic.ini
|   |-- README.md
|   `-- requirements.txt
|-- scrapers/
|   |-- base_scraper.py
|   |-- fixtures.py
|   |-- run_dry_ingestion.py
|   |-- news/
|   |-- pipeline/
|   |   |-- asset_linker.py
|   |   |-- deduplicator.py
|   |   |-- ingestion_contract.py
|   |   |-- ingestion_orchestrator.py
|   |   |-- normalizer.py
|   |   `-- source_trust.py
|   |-- rbz/
|   |-- research/
|   |-- tests/
|   |-- vfex/
|   |-- zse/
|   `-- README.md
|-- ai-services/
|-- shared/
|-- infrastructure/
|-- docs/
|-- AGENT.md
|-- PROJECT_STATE.md
|-- context.md
|-- pytest.ini
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository is a modular monorepo scaffold. The frontend foundation is stable. The backend foundation is stable. The database foundation includes SQLAlchemy metadata naming conventions, declarative base, timestamp mixin conventions, model import registry, session factory, and Alembic migration scaffolding wired to application settings.

The asset foundation includes the asset domain model, migration, development seed command, read-only service, and read-only API. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` many-to-many association table, asset-news relationships, read-only service, read-only `/api/v1/news` API, development sample news data, and migrations.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, `ScraperContext` dependency injection, one opt-in ZSE live announcements scraper, ZSE live validation checklist, backend handoff preview adapter, controlled backend submission client, normalization, deduplication, explicit asset linking, backend-compatible ingestion payloads, source trust scoring, and dry-run ingestion orchestration. The dry-run command reports what would be persisted but does not write to any database. The backend ingestion adapter now accepts normalized payloads, validates them, checks duplicates with URL and indexed content-hash lookups, resolves asset relationships, supports DRY_RUN and WRITE modes, and persists news records through article-level transaction boundaries.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The scraper layer contains one opt-in live HTTP scraper for ZSE announcements, disabled by default, plus a controlled backend submission client that defaults to OFF and can use DRY_RUN or explicitly gated WRITE mode. It intentionally contains no browser automation, scheduling, sentiment, embeddings, RAG, or direct database persistence.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* Resolved: dry-run ingestion can now hand normalized payloads to the backend ingestion adapter; persistence is available only through explicit WRITE mode.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 016 should validate the controlled backend submission workflow against a running local backend in DRY_RUN mode, then document any PostgreSQL or backend availability blockers. Do not add schedulers, authentication, AI, frontend integration, or broad multi-source scraping yet.

---

## Definition of Done

Sprint 015 is complete because:

* Source registry, source configuration, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots policy, metrics collector, logger, source metadata, `ScraperContext`, context factory, one opt-in ZSE live announcements scraper, ZSE live validation checklist, backend handoff adapter, handoff preview command, controlled backend submission client, and backend submission command exist.
* Core scraper tests cover registry behavior, environment loading, retry/backoff behavior, rate limiting, HTTP transport injection, robots metadata, metrics, user agents, logging redaction, context creation, factory wiring, source-specific config loading, placeholder scraper context injection, the ZSE live scraper parser/opt-in guard, backend handoff preview behavior, and backend submission mode behavior.
* `python -m pytest` passes from repository root.
* No automated live website requests, Playwright, Selenium, BeautifulSoup dependency, scheduler jobs, AI, sentiment, embeddings, RAG, frontend changes, authentication, or database writes were added.
* Project documentation is updated.

---

## Last Updated

* Date: 2026-06-26
* AI Agent: Codex
* Completed Task: Completed Sprint 015 controlled backend submission workflow foundation.

---

## Validation Results

* Full repository tests: `python -m pytest` passed from repository root, 98 tests passed.
* Handoff preview: `python -m scrapers.run_handoff_preview` printed DRY_RUN JSON for `/api/v1/ingestion/news` without backend submission.
* Backend submission command: `python -m scrapers.run_backend_submission` completed in default OFF mode without contacting a backend.
* Scraper validation: offline tests cover source registry, source config, HTTP abstraction with fake transport, retry policy, rate limiter, user-agent manager, robots policy, metrics collector, scraper logger, `ScraperContext`, `ScraperContextFactory`, the opt-in ZSE live scraper, backend handoff preview adapter, and backend submission client.
* Network safety: live scraper requests are disabled by default; ZSE live scraper tests use saved HTML fixtures and injected fake transports.
* Database safety: scraper infrastructure, ZSE live scraper, and handoff preview do not import backend database sessions and perform no database writes.
* Existing backend validation remains covered by the repository test suite; live PostgreSQL migration/seed/ingestion validation remains blocked by local PostgreSQL authentication.








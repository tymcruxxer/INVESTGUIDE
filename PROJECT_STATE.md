# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 012

Sprint Goal: Build reusable production-grade scraper infrastructure for future live data sources without scraping live websites, using browser automation, adding schedulers, adding AI, or writing to the database.

Current Tasks:

* [x] Created source registry with source metadata, enable/disable controls, category/priority lookup, and uniqueness validation.
* [x] Created environment-driven source configuration.
* [x] Created HTTP client abstraction with injectable transport and retry support.
* [x] Created retry policy with retryable status codes, exceptions, timeout handling, and exponential backoff.
* [x] Created rate limiter with minimum interval, requests-per-minute, cooldown, and burst protection.
* [x] Created user-agent manager with bot, desktop, mobile, and API profiles.
* [x] Created robots policy metadata abstraction without downloading robots.txt.
* [x] Created scraper metrics collector.
* [x] Created scraper lifecycle logger with secret redaction.
* [x] Added source metadata for official, institutional, and financial journalism sources.
* [x] Added offline tests proving no network calls or database writes are required.
* [x] Updated scraper README, project state, and context.

Sprint Exit Criteria:

* Source registry exists.
* HTTP abstraction exists.
* Retry policy exists.
* Rate limiter exists.
* User-agent manager exists.
* Robots policy abstraction exists.
* Metrics collector exists.
* Logger exists.
* Source metadata exists.
* Tests pass.
* No external network calls occur.
* Documentation is updated.
---

## Module Status

Frontend: Stable

Backend: Stable

Database: In Progress - models and migrations exist; live migration execution remains blocked on valid local PostgreSQL credentials

Authentication: Not Started

API: In Progress - health, read-only assets, read-only news, and internal news ingestion endpoints exist

Market Data: In Progress - asset domain/API foundation exists; real market data ingestion not implemented

Scrapers: In Progress - fixture-only scraper contracts, placeholders, core scraper infrastructure, pipeline utilities, and dry-run ingestion orchestration exist; backend ingestion adapter can consume normalized payloads; real fetching not implemented

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

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, source registry, source config, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, and dry-run ingestion orchestration; no live requests, Playwright, browser automation, external calls, scheduler, or DB writes yet

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: RAG/OpenAI/Ollama strategy documented, not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: `python -m pytest` from repository root runs backend and scraper tests; 75 tests pass

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

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, normalization, deduplication, explicit asset linking, backend-compatible ingestion payloads, source trust scoring, and dry-run ingestion orchestration. The dry-run command reports what would be persisted but does not write to any database. The backend ingestion adapter now accepts normalized payloads, validates them, checks duplicates with URL and indexed content-hash lookups, resolves asset relationships, supports DRY_RUN and WRITE modes, and persists news records through article-level transaction boundaries.

The backend intentionally contains no authentication, users, asset/news write routes, analytics, AI, notifications, or frontend integration. The scraper layer intentionally contains no real HTTP fetching, browser automation, scheduling, sentiment, embeddings, RAG, or database persistence.

---

## Current Blockers

* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH.
* Port `8000` still has a persistent listener on PID `4288`; current-app smoke testing can use alternate port `8001` until that local process is cleared.
* Real migration execution is blocked by PostgreSQL authentication failure for the configured local development user.
* Real seed execution is blocked by the same PostgreSQL authentication failure.
* Live database-backed asset/news endpoint success is blocked until PostgreSQL credentials are configured, migrations are applied, and data is seeded/ingested.
* Real scraper fetching is not implemented by design; Sprint 012 added reusable rate limiting, robots metadata, retry, HTTP abstraction, source registry, metrics, and logging infrastructure for future implementation.
* Resolved: dry-run ingestion can now hand normalized payloads to the backend ingestion adapter; persistence is available only through explicit WRITE mode.
* Frontend data workflows are blocked by missing frontend integration and broader business APIs.
* Authentication-dependent features are blocked because auth is not implemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---

## Next Immediate Task

Sprint 013 should implement the first opt-in live scraper using the Sprint 012 infrastructure, starting with one low-risk source and keeping network behavior behind explicit tests/mocks and documented robots/rate-limit review. Do not add AI, scheduling, authentication, frontend integration, or broad multi-source scraping yet.

---

## Definition of Done

Sprint 012 is complete because:

* Source registry, source configuration, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots policy, metrics collector, logger, and source metadata exist.
* Core scraper tests cover registry behavior, environment loading, retry/backoff behavior, rate limiting, HTTP transport injection, robots metadata, metrics, user agents, and logging redaction.
* `python -m pytest` passes from repository root.
* No live website requests, Playwright, Selenium, BeautifulSoup parsing, scheduler jobs, AI, sentiment, embeddings, RAG, frontend changes, authentication, or database writes were added.
* Project documentation is updated.

---

## Last Updated

* Date: 2026-06-25
* AI Agent: Codex
* Completed Task: Completed Sprint 012 production-grade scraper infrastructure foundation.

---

## Validation Results

* Full repository tests: `python -m pytest` passed from repository root, 75 tests passed.
* Scraper core validation: offline tests cover source registry, source config, HTTP abstraction with fake transport, retry policy, rate limiter, user-agent manager, robots policy, metrics collector, and scraper logger.
* Network safety: no live scraper requests are made; HTTP abstraction tests monkeypatch the default transport and use injected fake transports.
* Database safety: scraper core infrastructure does not import backend database sessions and performs no database writes.
* Existing backend validation remains covered by the repository test suite; live PostgreSQL migration/seed/ingestion validation remains blocked by local PostgreSQL authentication.
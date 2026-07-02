# InvestGuide

AI-powered Zimbabwean investment intelligence platform.

## Stack
- Next.js
- FastAPI
- PostgreSQL
- Redis
- Python
- AI/RAG systems

## Architecture
Modular monolith architecture designed for AI-assisted development.

## Documentation
See /docs for:
- PRD
- architecture
- startup blueprint
- technical planning
- AI-agent rules

## Engineering Principles
- modular architecture
- analytics-first
- explainable AI
- responsive fintech UI
- scalable infrastructure
## Local Backend Development

Use the one-command development launcher from the repository root:

```bash
python backend/scripts/dev.py --port 8001
```

The launcher checks Docker, starts the Compose PostgreSQL service, waits for the database, runs backend bootstrap migrations and seed data, then starts FastAPI with Uvicorn.

Useful flags:

```bash
python backend/scripts/dev.py --no-server
python backend/scripts/dev.py --port 8001
python backend/scripts/dev.py --skip-docker
python backend/scripts/dev.py --skip-bootstrap
```

Manual commands remain available when troubleshooting:

```bash
docker compose up -d
python backend/scripts/bootstrap_dev.py
python backend/scripts/check_database.py
```

Health check:

```bash
curl http://127.0.0.1:8001/api/v1/health
```

The Compose stack runs PostgreSQL 16 with a named volume and development-only credentials from `backend/.env.example`. The launcher does not reset databases, delete volumes, enable WRITE ingestion mode, start schedulers, start scrapers, or run live scraping. Do not commit `.env` or hosted database credentials.


## Sprint 023 Integration Validation

Sprint 023 validated the current full-stack flow as far as the local machine allows.

Results:

* Backend starts on port `8001` and `/api/v1/health` returns 200.
* Frontend starts on port `3000` with `NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1`.
* Frontend `/auth/signup`, `/auth/login`, `/onboarding`, and `/dashboard` routes return 200 from the Next.js dev server.
* `python -m pytest` passes with 184 backend/scraper tests.
* `npm.cmd run lint`, `npm.cmd run type-check`, and `npm.cmd run build` pass in `frontend/`.

Current blocker:

* Docker is not installed or not available on PATH on this machine.
* Local PostgreSQL on port `5432` rejects the configured `investguide_user` credentials, so database-backed signup, login, asset retrieval, and investor profile persistence cannot complete locally yet.

Next step: install/enable Docker or correct local PostgreSQL credentials, then rerun the database-backed end-to-end auth/onboarding/profile persistence smoke.

## Sprint 024 Environment Validation

Sprint 024 attempted to complete fully persisted end-to-end validation. The product foundation still cannot persist locally because the machine-level database environment is unavailable.

Results:

* `docker --version`, `docker compose version`, `docker info`, and `docker compose up -d` fail because `docker` is not recognized on PATH.
* `python backend/scripts/bootstrap_dev.py` fails clearly because local PostgreSQL rejects `investguide_user` credentials.
* `python backend/scripts/check_database.py` reports the database unavailable or unreachable with the configured credentials.
* FastAPI starts on port `8001`; `/api/v1/health` returns 200 with `database: unavailable`.
* Signup, login, investor profile, and assets are blocked by PostgreSQL connectivity/credential failure.
* Next.js starts on port `3000`; `/auth/signup`, `/auth/login`, `/onboarding`, and `/dashboard` return 200.
* `python -m pytest`, `npm.cmd run lint`, `npm.cmd run type-check`, and `npm.cmd run build` pass.

No fake storage or database bypass was added. The next step is to install/enable Docker or fix local PostgreSQL credentials, then rerun the persisted end-to-end flow.

## Sprint 025 Product Architecture

Sprint 025 reframed InvestGuide as an AI Financial Intelligence Platform and added long-term product architecture documentation under `docs/product/`.

New product architecture documents:

* `docs/product/product-philosophy.md`
* `docs/product/product-pillars.md`
* `docs/product/ai-capabilities.md`
* `docs/product/personalization.md`
* `docs/product/platform-modules.md`
* `docs/product/user-journey.md`
* `docs/product/analytics-roadmap.md`
* `docs/product/feature-backlog.md`

Guiding principle:

> Every feature must answer one question: Does this help the user make a better financial decision?

Sprint 025 did not implement analytics calculations, AI models, portfolio tools, budgeting tools, recommendations, simulations, roadmaps, or new frontend/backend product features.

## Sprint 026 Analytics Engine Foundation

Sprint 026 adds the backend analytics architecture foundation under `backend/app/analytics/`.

The analytics engine is now the intended single source of truth for future financial intelligence. Future frontend, AI, portfolio, comparison, news intelligence, roadmap, and recommendation modules should consume analytics through this centralized engine rather than calculating metrics independently.

Implemented architecture:

* `AnalyticsContext`
* `AnalyticsResult`
* `BaseAnalytics`
* `AnalyticsRegistry`
* `AnalyticsEngine`
* purpose-only score modules for quality, growth, dividend, value, liquidity, risk, macro, and confidence
* deterministic `AnalyticsExplanation`
* analytics-specific exceptions
* engine and methodology versioning
* `docs/architecture/analytics-engine.md`

Sprint 026 does not implement real financial calculations, PE ratios, DCF, dividend models, portfolio analytics, macro calculations, AI, recommendations, frontend charts, comparisons, or predictions.

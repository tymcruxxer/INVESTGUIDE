# InvestGuide Feature Backlog

This backlog organizes future work by phase and status. It is a planning document, not an implementation command.

Status labels:

* Implemented: exists in the repository now
* In Progress: foundation exists but is incomplete
* Planned: expected in near-term roadmap
* Future: long-term capability

## Phase 1: Foundation

* Implemented: frontend shell, dashboard placeholders, route structure, theme, Zustand, TanStack Query.
* Implemented: backend FastAPI foundation, config, logging, response envelope, health endpoint.
* Implemented: SQLAlchemy/Alembic foundation.
* Implemented: asset model, schemas, migration, seed structure, read-only API.
* Implemented: news model, content hash, read-only API, ingestion adapter foundation.
* Implemented: scraper foundation, dry-run orchestration, handoff preview, controlled submission client.
* Implemented: auth model, JWT signup/login/me, frontend login/signup/onboarding pages.
* In Progress: local PostgreSQL/Docker runtime validation.
* Planned: fix local development database environment.
* Planned: CI validation pipeline.

## Phase 2: Data and Market Intelligence

* Planned: historical price models and ingestion.
* Planned: market data APIs.
* Planned: asset detail API expansion.
* Planned: live ZSE/VFEX/RBZ ingestion after safety review.
* Planned: news ingestion write path after DB validation.
* Planned: source trust dashboards and ingestion monitoring.
* Future: PDF financial report ingestion.
* Future: institutional research ingestion.

## Phase 3: Analytics and Intelligence

* Planned: risk analytics.
* Planned: dividend and income analytics.
* Planned: performance and volatility analytics.
* Planned: macro adjustment analytics.
* Planned: comparison engine.
* Planned: investment score methodology.
* Future: opportunity radar.
* Future: scenario simulations.
* Future: financial health score.

## Phase 4: AI Financial Intelligence Platform

* Planned: RAG knowledge base.
* Planned: AI financial assistant with source grounding.
* Planned: AI news summaries.
* Planned: AI asset explanations.
* Planned: adaptive education.
* Future: AI portfolio intelligence.
* Future: AI roadmaps.
* Future: AI simulations.
* Future: recommendation engine with strict safety boundaries.
* Future: premium intelligence reports.

## Cross-Cutting Backlog

* Planned: development-only system diagnostics endpoint.
* Planned: `backend/scripts/doctor.py` developer verification command.
* Planned: production auth hardening with HTTP-only cookies and refresh tokens.
* Planned: dedicated AuthProvider and future AuthContext.
* Future: RBAC or permissions if product scope requires it.
* Future: subscription and premium gating.
* Future: notifications and alerts.
* Future: deployment monitoring and observability.

## Explicitly Deferred

These should not be implemented until the data, analytics, and safety foundations are mature:

* AI recommendations
* portfolio automation
* live trading or brokerage execution
* payment flows
* social investing
* guaranteed-return language
* unsourced AI claims
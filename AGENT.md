# InvestGuide AI Agent Operating Manual

## Startup Procedure

Before making changes:

1. Read `README.md`.
2. Read `AGENT.md`.
3. Read `PROJECT_STATE.md` if it exists.
4. Read `context.md`.
5. Read all relevant documentation inside `/docs`.
6. Understand the current sprint.
7. Check project health.
8. Review known issues.

## Engineering Rules

* Never change the architecture unless explicitly instructed.
* Never upgrade major framework versions without approval.
* Preserve the modular monorepo architecture.
* Keep TypeScript strict.
* Use reusable components.
* Follow clean architecture principles.
* Preserve existing folder structure.
* Avoid monolithic files.
* Prefer minimal safe changes.
* Explain all architectural decisions.
* Validate all work before finishing.
* Update `PROJECT_STATE.md` after every completed task.
* Update `context.md` after every completed task.

## Protected Decisions

Do not change these without explicit approval:

* Next.js 14.x
* React 18.x
* FastAPI
* PostgreSQL
* TailwindCSS
* Zustand
* TanStack Query
* Framer Motion
* Modular Monorepo
* Analytics-first architecture
* AI explains analytics, not replaces it
* Educational investment platform, not a broker

## Project-Specific Operating Notes

* Build layer-by-layer: data infrastructure, analytics, backend APIs, frontend dashboards, AI orchestration, then advanced features.
* Backend endpoints must use the documented `/api/v1` structure and global response envelope.
* AI responses must be grounded in retrieved/source data, cite sources, acknowledge uncertainty, and include the educational-not-financial-advice positioning.
* Frontend work should remain inside the documented `frontend/` folders and use the existing Tailwind, Zustand, TanStack Query, Framer Motion, and Lucide patterns.
* Backend work should remain inside the documented `backend/` folders and use FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Redis, and clean service boundaries.
* Scrapers must remain modular by source and respect the documented source trust hierarchy.

## Coding Standards

* Keep TypeScript strict and avoid suppressing lint/type errors unless explicitly justified.
* Prefer small, focused modules over monolithic files.
* Use existing project utilities, providers, stores, and service patterns before introducing new abstractions.
* Use TailwindCSS classes and existing theme tokens for frontend styling.
* Keep API contracts aligned with the documented `/api/v1` endpoints and response envelope.
* Avoid hardcoded secrets, credentials, source URLs, or environment-specific values.
* Do not introduce package upgrades, new frameworks, or major dependency changes without explicit approval.

## Validation Requirements

Before completing any implementation or documentation-state task, run all applicable checks:

* Frontend lint: `npm.cmd run lint` from `frontend/`.
* Frontend type-check: `npm.cmd run type-check` from `frontend/`.
* Frontend build: `npm.cmd run build` from `frontend/`.
* Tests: run the relevant test command when a test suite exists.
* Record skipped or unavailable checks explicitly in `PROJECT_STATE.md` and `context.md`.

## Documentation Update Requirements

Every completed task must update:

* `PROJECT_STATE.md` as the current source of truth.
* `context.md` as the historical engineering log.

Documentation updates must distinguish between current state and historical record:

* `PROJECT_STATE.md` should contain only the current software state, active blockers, current sprint, and next immediate task.
* `context.md` should preserve session history and append new entries without deleting prior information.
* `AGENT.md` should contain permanent operating rules only.

## Context Management Rules

* Never begin implementation before reading the startup documents listed above.
* Do not rewrite `context.md`; append session history and update clearly marked current-state sections only when requested.
* Do not remove historical context entries from `context.md`.
* Remove resolved blockers from `PROJECT_STATE.md`, but mark historical issues as resolved in `context.md`.
* Keep `PROJECT_STATE.md`, `context.md`, and `AGENT.md` synchronized after every task.

## Definition of Done

Every task is done only when:

* The requested scope is completed without unrelated code or architecture changes.
* All relevant validation commands pass, or unavailable checks are clearly documented.
* `PROJECT_STATE.md` reflects the current repository state.
* `context.md` has a new session-history entry and updated validation results.
* Any architectural decision or known issue discovered during the work is documented.
* The final response lists files created, files modified, validation results, current health, and the next recommended task.

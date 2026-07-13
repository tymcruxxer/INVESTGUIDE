# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 043

Sprint Goal: Add deterministic Business Intelligence, Industry Intelligence, competitor reasoning, and a Company Deep Dive surface without LLMs, predictions, recommendations, or personalized advice.

Current Tasks:

* [x] Added deterministic backend Business Intelligence Engine.
* [x] Added deterministic Industry Intelligence Engine.
* [x] Added deterministic Competitor Engine.
* [x] Added GET /api/v1/companies/{ticker}/business endpoint.
* [x] Added GET /api/v1/industries/{industry} endpoint.
* [x] Added Company Deep Dive frontend panel on /company/[ticker].
* [x] Added tests for business, industry, competitor, and endpoint behavior.
* [x] Ran Python tests, frontend lint, frontend type-check, and frontend build.
* [x] Updated backend README, frontend README, PROJECT_STATE.md, and context.md.

Sprint Exit Criteria:

* Business Intelligence explains what a company does, how it makes money, key revenue drivers, risks, maturity, competitors, and industry forces.
* Industry endpoint returns description, characteristics, risks, opportunities, companies, Learn Next, and related industries.
* Company page displays a premium Company Deep Dive panel.
* No LLMs, predictions, buy/sell recommendations, alerts, live scraping, portfolio optimization, or personalized advice are added.
* Validation passes.
* Backend tests and frontend lint/type-check/build pass.
---
## Module Status

Frontend: Stable - auth/login/signup pages, onboarding flow, protected shell, polished navigation, backend-connected dashboard, meaningful empty states, asset explorer, asset detail with polished AI Research panel, company page with backend-first CompanyProfile loading and polished Company AI Research panel, canonical DLTA route mapping, explicit Development Preview fallback, comparison page, education guide, settings/account review, and search routing exist

Backend: Stable - FastAPI starts on port 8001, health/auth/profile/assets/companies/news/assessment/research routes work against local Docker PostgreSQL when it is running

Database: Stable Locally - Docker PostgreSQL 16 runs on host port `5433`, migrations apply, seed data loads, and diagnostics report database connected/current

Authentication: In Progress - backend JWT foundation and frontend login/signup/session hydration exist; database connectivity is now available for manual auth validation

API: In Progress - health, auth signup/login/me, investor profile, read-only assets, read-only companies, company profiles, read-only news, asset/company assessments, asset/company research, and internal news ingestion endpoints exist; frontend now consumes assets/news/profile/company APIs where available

Market Data: In Progress - asset domain/API foundation exists and Company Intelligence now links issuers to assets, news, assessments, and persisted-or-preview structured enrichment profiles; real market data ingestion not implemented

Personalization: In Progress - backend investor profile APIs exist and frontend onboarding now captures experience, goals, asset preferences, risk, horizon, planned range, and language preference; no AI recommendations or adaptive dashboards yet

Scrapers: In Progress - fixture-only scraper contracts, core scraper infrastructure, opt-in ZSE live scraper, dry-run orchestration, backend handoff preview, controlled backend submission, and DRY_RUN smoke path exist; live fetching remains disabled by default

Analytics Engine: In Progress - centralized analytics package foundation exists with engine, registry, context, result object, score contracts, explanation layer, exceptions, versioning, docs, and tests; no real calculations yet

AI/RAG: In Progress - deterministic AI Research Engine foundation now includes single-subject research, cross-asset/company comparison, related investment reasoning, and lightweight knowledge graph paths; RAG, chat, embeddings, and LLM integrations are not implemented

Notifications: Not Started

Testing: Stable - root pytest passes backend/scraper tests; frontend lint, type-check, and build pass

Deployment: Not Started

Documentation: Stable - Sprint 043 Business Intelligence documentation added

---

## Current Technology Stack

Frontend: Next.js 14.2.x, React 18.3.x, TypeScript 5.3.x

Backend: Python 3.12+ target; validated on Python 3.13.2, FastAPI, Uvicorn

Database: PostgreSQL 16 for local Docker development, PostgreSQL planned for hosted environments, SQLAlchemy 2.x, Alembic, psycopg 3

Developer Tooling: Docker Compose, `backend/scripts/dev.py`, `backend/scripts/bootstrap_dev.py`, `backend/scripts/check_database.py`

Personalization: SQLAlchemy investor profile model, Pydantic v2 schemas, deterministic backend service for profile CRUD and presentation settings, versioned FastAPI profile endpoints

Scraping: Python dataclass-based scraper contracts, fixture-only placeholder source modules, `ScraperContext`, context factory, HTTP abstraction, retry policy, rate limiter, user-agent manager, robots metadata, metrics, logging, normalization, deduplication, asset linking, source trust scoring, dry-run ingestion orchestration, backend handoff preview formatting, and controlled backend submission reporting

State Management: Zustand, TanStack Query

Styling: TailwindCSS 3.4.x, CSS-variable theme tokens

Animation: Framer Motion 10.x

API Client: Axios 1.7.x

AI: deterministic AI Research Engine foundation implemented without LLMs; comparison, related investment reasoning, and knowledge graph paths are deterministic; RAG/OpenAI/Ollama strategy documented but not implemented

Deployment: Vercel/Railway or Render/Supabase/Upstash planned, not implemented

Testing: frontend lint/type-check/build pass; `python -m pytest` from repository root runs backend and scraper tests with 253 tests passing

---

## Repository Structure

```text
investguide/
|-- frontend/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- api/v1/
|   |   |-- database/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- scripts/
|   |-- tests/
|   |-- .env.example
|   |-- alembic.ini
|   |-- README.md
|   `-- requirements.txt
|-- scrapers/
|-- ai-services/
|-- shared/
|-- infrastructure/
|-- docs/
|-- docker-compose.yml
|-- AGENT.md
|-- PROJECT_STATE.md
|-- context.md
|-- pytest.ini
|-- .gitignore
`-- README.md
```

---

## Current Architecture

The repository remains a modular monorepo. The frontend foundation now includes client-side authentication, onboarding, session hydration, route protection, backend-connected dashboard data, asset exploration, asset detail views, news display, and asset comparison with explicit demo fallback. The backend foundation is stable and includes reproducible local database infrastructure plus a single-command development launcher.

The asset foundation includes the asset model, migration, development seed command, read-only service, and read-only API. Sprint 031 adds Company Intelligence as an issuer-level layer above assets with `companies`, `company_news`, `assets.company_id`, read-only company APIs, company detail frontend page, related assets, related news, and assessment reuse. Sprint 032 adds Company Intelligence Enrichment with `company_profiles`, source transparency, research status, fixture-backed structured facts, and `/companies/{ticker}/profile`. The news intelligence foundation includes the news article model, persisted unique/indexed `content_hash`, `asset_news` relationship, read-only service/API, development sample data, and backend ingestion adapter.

The personalization foundation includes the product personalization vision document, `InvestorProfile` model, Pydantic schemas, Alembic migration, service layer, demo seed data, and authentication-independent create/read/update API endpoints. Authenticated profile requests resolve by `investor_profiles.user_id`; unauthenticated requests use the first-row development fallback only when `APP_ENV=development`.

The scraper foundation includes source-independent contracts, fixture-only source placeholders, reusable core scraper infrastructure, one opt-in ZSE live announcements scraper, backend handoff preview adapter, controlled backend submission client, and operator-run DRY_RUN smoke script. Scrapers do not write directly to the database.

The backend contains a basic JWT authentication foundation and user/profile linkage. The frontend now contains login, signup, onboarding, auth state, and client-side protected navigation. The product intentionally contains no AI recommendation engine, real analytics calculations, notifications, portfolio tracking, watchlists, payments, RBAC, OAuth, MFA, email verification, or production auth hardening.

---

## Current Blockers

* Local non-Docker PostgreSQL still listens on host port `5432`; InvestGuide Docker PostgreSQL intentionally uses host port `5433` to avoid the conflict.
* Resolved for frontend routes: `/company/delta` and `/assets/delta` now map to canonical seeded ticker `DLTA`. Backend API endpoints still expect canonical `DLTA` unless a future alias layer is designed.
* Local PostgreSQL client commands `psql` and `pg_isready` are not available on PATH, but Docker `psql` works inside the `investguide-postgres` container.
* AI recommendations, adaptive dashboards, portfolio tracking, watchlists, payments, live scraping, and schedulers remain intentionally unimplemented.
* Real scraper fetching is implemented only as a disabled-by-default ZSE announcements pattern; broad live scraping remains intentionally unimplemented.
* `docs/ai/ai-agent-rules.md` is empty.
* Dedicated CI is not implemented.

---
## Architectural Backlog

* Future enhancement: introduce an `AuthContext` object after authentication-dependent services begin to grow. It should mirror the existing `ScraperContext` pattern and bundle authenticated user state such as `user`, JWT claims, investor profile, permissions, feature flags, locale, onboarding completion, and future tenant/organization data. Protected services should eventually accept one context object rather than several separate auth-related parameters. This is intentionally not implemented in Sprint 020.
* Future enhancement: move auth orchestration into a dedicated `AuthProvider` once auth behavior grows beyond the current MVP client-side flow. The provider should manage login, logout, hydration, redirects, onboarding status, auth loading state, future session refresh, roles, subscription plans, premium gates, and feature flags, while Zustand stores current state.
* Future production security enhancement: replace localStorage JWT persistence with a stronger auth model after backend database validation is stable. Candidate direction: HTTP-only cookies, refresh tokens, CSRF protection, and silent token refresh. LocalStorage remains acceptable for the MVP and is documented as a limitation.
* Future developer-experience enhancement: add a development-only internal diagnostics endpoint such as `GET /api/v1/system/status` to report database connectivity, migration status, scraper enablement, ingestion mode, environment status, and PostgreSQL/Docker readiness without exposing secrets. This should remain disabled or protected outside development.
* Future developer-experience enhancement: add a lightweight `python backend/scripts/doctor.py` command that checks Docker availability, PostgreSQL connectivity, Alembic revision, required environment variables, seed status, and API health, then prints a simple pass/fail report.
* Future architecture documentation enhancement: add `docs/product/data-flow.md` to explain how information moves through InvestGuide across news ingestion, scraper normalization, deduplication, storage, analytics, AI, frontend delivery, onboarding personalization, portfolio analytics, macro outlooks, education, learning, roadmaps, and financial health.
* Future architecture documentation enhancement: add `docs/architecture/system-map.md` as the one-platform diagram covering frontend, backend, AI layer, analytics engine, scrapers, PostgreSQL, future vector database, future cache, authentication, and background workers.
* Future research architecture enhancement: introduce a canonical `ResearchContext` object before expanding the AI Research Engine further. It should bundle `company`, `asset`, `company_profile`, existing assessment output, future market data, news, metadata, and timestamps so `OpportunityEngine`, `RiskEngine`, `EvidenceEngine`, and `EducationEngine` consume one stable input contract. This mirrors the `ScraperContext` pattern and will make future financial statements, dividends, macro indicators, sector benchmarks, analyst consensus, news intelligence, and LLM-enhanced educational explanations easier to add without changing every engine individually.
* Future analytics architecture enhancement: introduce an AnalyticsPipeline execution layer when analytics modules need dependency ordering, caching, parallel execution, timeout handling, partial failures, execution metrics, or audit logging. This should preserve `AnalyticsEngine` as the orchestration layer while letting execution behavior evolve independently.

---
## Next Immediate Task

Sprint 044 should runtime-smoke `/api/v1/companies/DLTA/business`, `/api/v1/industries/Beverages`, and `/company/delta` against the local PostgreSQL-backed backend, then fix only confirmed data, layout, or UX issues.

---
## Definition of Done

Sprint 043 is complete because the deterministic Business Intelligence Engine, Industry Intelligence Engine, Competitor Engine, read-only business/industry endpoints, Company Deep Dive panel, tests, frontend validation, and documentation updates are complete without adding LLMs, predictions, recommendations, live scraping, alerts, portfolio optimization, or personalized advice.

---
## Last Updated

* Date: 2026-07-13
* AI Agent: Codex
* Completed Task: Completed Sprint 043 deterministic Business Intelligence Engine and Company Deep Dive.
---
## Validation Results

* Tests: `python -m pytest -q` passed, 253 tests, 1 non-blocking pytest cache permission warning.
* Frontend lint: `npm.cmd run lint` passed.
* Frontend type-check: `npm.cmd run type-check` passed.
* Frontend build: `npm.cmd run build` passed, 14 routes generated.
* Runtime route smoke: `/`, `/auth/signup`, `/auth/login`, `/dashboard`, `/assets`, `/assets/delta`, `/company/delta`, `/compare`, `/markets`, `/education`, and `/settings` returned 200 after dev-server compilation.
* Runtime API smoke: warmed `GET /api/v1/compare?asset_a=DLTA&asset_b=TIGZ` passed; warmed `GET /api/v1/companies/DLTA/related` passed with 4 related companies, 6 Learn Next topics, and 10 knowledge graph nodes.
* Runtime note: `GET /api/v1/health` reported `database: unavailable` during this session even though direct relationship endpoints worked; re-run database diagnostics in the next browser QA pass.

---

## Stabilization Update - Authentication and Test Suite

Date: 2026-07-06

Completed:

* Pinned bcrypt to `>=4.0.1,<4.1.0` for compatibility with `passlib==1.7.4`.
* Verified installed versions: `bcrypt==4.0.1`, `passlib==1.7.4`.
* Verified password hashing and verification behavior with bcrypt.
* Hardened route registration tests to inspect only FastAPI route objects that expose `.path`.
* Updated frontend auth API fallback to `http://127.0.0.1:8001/api/v1`.
* Updated signup/login network error handling to show a clear backend-unreachable message.
* Fixed landing page auth navigation from `/auth/register` to `/auth/signup`.
* Updated local CORS defaults to include `http://127.0.0.1:3000`.
* Polished the public frontend palette toward dark navy, slate cards, blue primary actions, teal accent, and high-contrast text.

Validation:

* `python -m pytest -q`: passed before the final no-BOM rewrite with 174 tests passed and 1 non-blocking pytest cache permission warning. Final rerun was blocked by the execution sandbox approval layer.
* Password hash smoke: passed (`hash_password`, valid password verification, invalid password rejection).
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed and generated 14 routes.
* Backend health on `http://127.0.0.1:8001/api/v1/health`: reachable, but reported database unavailable.
* `python backend/scripts/check_database.py`: failed because PostgreSQL on `localhost:5433` timed out.
* `docker compose ps`: failed due Docker Desktop engine API error.

Known Runtime Blocker:

* Manual signup/login cannot be honestly confirmed until Docker/PostgreSQL is reachable again. Backend starts and health responds, but database-backed auth requests cannot complete while PostgreSQL times out.
---

## Stabilization Update - Local CORS

Date: 2026-07-06

Completed:

* Added local frontend fallback origins `http://localhost:3001` and `http://127.0.0.1:3001` to backend CORS configuration.
* Updated `backend/.env`, `backend/.env.example`, and backend CORS defaults.
* Verified `OPTIONS /api/v1/auth/signup` from `Origin: http://localhost:3001` returns `Access-Control-Allow-Origin: http://localhost:3001`.

Validation:

* `python -m pytest -q`: passed, 174 tests passed, 1 non-blocking pytest cache permission warning.
* CORS preflight for signup from `http://localhost:3001`: passed.
---

## Stabilization Update - Permanent CORS/Auth Connectivity Fix

Date: 2026-07-07

Completed:

* Diagnosed CORS/auth connectivity for frontend origin `http://localhost:3001` and backend `http://127.0.0.1:8001`.
* Confirmed `CORS_ORIGINS` is configured in `backend/.env` and parsed into a list of four origins.
* Made backend settings load from an absolute `backend/.env` path instead of a working-directory-relative `.env` path.
* Added startup diagnostics for APP_ENV, masked DATABASE_URL, parsed CORS_ORIGINS, CORSMiddleware installation, and middleware order.
* Confirmed middleware order is `CORSMiddleware` before `RequestLoggingMiddleware` and routers are included after middleware registration.
* Added CORS regression tests for parsing and auth preflight from `http://localhost:3001`.
* Verified signup and login succeed with `Origin: http://localhost:3001`.

Validation:

* Startup logs show APP_ENV `development`, masked PostgreSQL URL on `localhost:5433`, CORS origins as a Python list, CORSMiddleware installed, and middleware order `['CORSMiddleware', 'RequestLoggingMiddleware']`.
* `OPTIONS /api/v1/auth/signup`: HTTP 200, `Access-Control-Allow-Origin: http://localhost:3001`, allowed methods include POST, allowed headers include content-type.
* `OPTIONS /api/v1/auth/login`: HTTP 200 with the same CORS headers.
* Signup smoke: passed.
* Login smoke: passed.
* `python -m pytest -q`: passed, 177 tests passed, 1 non-blocking pytest cache warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.
---

## Sprint 034 Update - World-Class UI/UX Redesign and Auth UX Polish

Date: 2026-07-07

Completed:

* Added cohesive premium design-system utilities for cards, inputs, buttons, badges, success, warning, and error states.
* Redesigned landing page with a premium fintech hero, platform metrics, featured companies, benefit cards, how-it-works cards, and polished CTA/footer.
* Redesigned signup with validation, password visibility, password strength, friendly existing-account messaging, and a dedicated account-created success state before onboarding.
* Redesigned login with premium layout, password visibility, and friendly error handling.
* Polished public layout, sidebar, navbar/search, onboarding surfaces, dashboard cards, roadmap, warning states, and shared page card treatments.
* Preserved existing frontend/backend architecture and API contracts.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed, 177 tests passed, 1 non-blocking pytest cache warning.
* Runtime auth smoke: blocked by PostgreSQL timeout on `localhost:5433`; backend CORS works, but database-backed signup/login cannot complete until local PostgreSQL is reachable.
---

## Sprint 035 Update - Premium Fintech Visual Redesign

Date: 2026-07-07

Completed:

* Refined the InvestGuide visual identity away from muddy/neon accents toward a premium financial palette.
* Normalized global tokens around deep navy background, slate elevated surfaces, professional blue primary actions, emerald success states, amber warnings, red danger, and high-contrast slate text.
* Removed remaining bright cyan/teal, pink/magenta, and yellow visual references from core frontend styling.
* Upgraded primary button styling with subtle blue gradient and stronger premium shadow treatment.
* Refined chart and sentiment color tokens for institutional blue/green/amber/red/slate usage.
* Preserved all routes, backend APIs, authentication logic, data services, and product functionality.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed, 177 tests passed, 1 non-blocking pytest cache warning.
---
## Sprint 036 Real Backend Data Integration Status

Completed:

* Added `frontend/utils/tickers.ts` for deterministic frontend route alias handling.
* Mapped friendly `delta` routes/search results to canonical backend ticker `DLTA`.
* Standardized frontend fallback copy to `Backend unavailable. Showing development preview data.`
* Updated asset detail and company detail pages so backend-empty responses remain empty rather than silently injecting preview rows.
* Preserved Company Profile data-origin labels: `Persisted Backend`, `Development Preview`, and `Unavailable`.

Runtime validation:

* Docker Compose PostgreSQL: running.
* Alembic migration: current at `20260703_0001`.
* Unified seed: completed.
* Database diagnostics: connected, migrations current, seed data present, asset count 9.
* Backend smoke: health, assets, companies, news, `companies/DLTA/profile`, `assets/DLTA/assessment`, signup, login, `/auth/me`, profile POST, and profile GET passed.
* Frontend route smoke: `/auth/signup`, `/auth/login`, `/onboarding`, `/dashboard`, `/assets`, `/assets/delta`, `/company/delta`, `/compare`, and `/markets` returned HTTP 200.
* News note: `/api/v1/news` is reachable but returned 0 persisted articles in the current local database.

Validation:

* `python -m pytest -q`: passed, 228 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
---
## Sprint 037 Product Polish Status

Completed:

* Settings page now presents account identity, investor profile, security status, notifications status, and clear next actions.
* Education page now presents learning paths, featured topics, and an honest curriculum-empty state instead of loading forever.
* Dashboard latest news now shows an empty state when the backend news API is reachable but contains no persisted rows.
* Sidebar navigation now has helper labels, active `aria-current`, better mobile close behavior, and clearer labels.
* Global search now has a no-results state with guidance and a browse-assets action.

Validation:

* `python -m pytest -q`: passed, 228 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* Frontend route smoke: `/`, `/auth/signup`, `/auth/login`, `/onboarding`, `/dashboard`, `/assets`, `/assets/delta`, `/company/delta`, `/compare`, `/markets`, `/education`, and `/settings` returned HTTP 200.
* Backend smoke: `/health`, `/assets`, `/companies`, `/companies/DLTA/profile`, and `/assets/DLTA/assessment` passed.
* Auth/profile persistence smoke: signup, login, profile POST, and profile GET passed.
---

## Sprint 038 AI Research Engine Foundation

Date: 2026-07-10

Completed:

* Added deterministic backend AI Research schema and service composition layer.
* Added independent opportunity, risk, evidence, education, question, summary, and scoring engines under `backend/app/services/intelligence/`.
* Added `GET /api/v1/assets/{ticker}/research` and `GET /api/v1/companies/{ticker}/research`.
* Added process-local research caching keyed by subject type, ticker, updated data, description, market cap, and listing date.
* Added frontend `ResearchAssessment` types and API methods for asset/company research.
* Added reusable `ResearchPanel` and displayed it on `/assets/[ticker]` and `/company/[ticker]`.
* Added tests for research engines, safe payload generation, and research route envelopes.
* Updated backend README and frontend README.

Architecture Decisions:

* AI Research is deterministic, structured, and evidence-based; it does not call OpenAI, Claude, Gemini, local LLMs, embeddings, RAG, or external AI services.
* Future LLM layers must consume and enhance the deterministic research payload rather than replace the evidence engine.
* Research avoids buy/sell wording, price targets, certainty, predictions, and personalized recommendations.
* Existing asset/company assessment endpoints remain backward-compatible.

Validation:

* `python -m pytest -q` from repository root: passed, 235 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known Limitations:

* Research remains rule-based and uses currently available structured fields only.
* No live market prices, financial statements, portfolio context, user-specific recommendations, sentiment, embeddings, or LLM summaries are included.
* The process-local research cache is suitable for the current read-only deterministic foundation; a distributed cache can be considered later if needed.

Recommended Sprint 039:

* Manually browser-test the new research panels against the running local backend, then expand structured inputs or audit logging only if validation shows the current surfaces are stable.
---

## Sprint 039 Research Experience and Runtime Validation

Date: 2026-07-13

Completed:

* Polished the reusable frontend AI Research panel with clearer hierarchy, score cards, semantic tones, evidence prominence, education callouts, ELI18 formatting, clickable suggested-question chips, and source transparency.
* Added `ResearchPanelSkeleton` and `ResearchUnavailable` states.
* Replaced generic research loading/error cards on asset and company pages with research-specific states.
* Smoke-tested backend research, auth, profile, asset, company, and news endpoints against local Docker PostgreSQL.
* Smoke-tested frontend routes on the Next.js dev server.
* Updated backend README and frontend README.

Validation:

* Database diagnostics: connected, migrations current, seed data present, asset count 9.
* Backend smoke: `/health`, `/assets`, `/assets/DLTA`, `/assets/DLTA/research`, `/companies`, `/companies/DLTA`, `/companies/DLTA/research`, `/companies/DLTA/profile`, and `/news` returned 200.
* Auth/profile smoke: signup, login, `/auth/me`, profile POST, and profile GET passed with valid onboarding values.
* Frontend route smoke: `/`, `/auth/signup`, `/auth/login`, `/onboarding`, `/dashboard`, `/assets`, `/assets/delta`, `/company/delta`, `/compare`, `/markets`, `/education`, and `/settings` returned 200 after dev-server warmup.
* `python -m pytest -q`: passed, 235 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Performance Observations:

* `/assets/DLTA/research` returned 200 and measured approximately 45ms from the operator smoke command; backend logs recorded approximately 9ms for the request after startup.
* `/companies/DLTA/research` returned 200 and measured approximately 354ms from the operator smoke command; backend logs recorded approximately 140ms for the request.
* Frontend first route hits were slower due Next.js dev-server compilation; warmed routes returned normally.

Known Limitations:

* Full visual browser QA with screenshots across desktop, tablet, and mobile remains recommended; this session used local route/API smoke checks and server logs.
* Research remains deterministic and rule-based with currently available structured fields only.

Recommended Sprint 040:

* Run interactive browser QA with screenshots across desktop/tablet/mobile for the polished research cards and core user journeys, then fix only confirmed responsive, console, hydration, or visual defects.




## Sprint 042 News Intelligence Engine

Sprint 042 adds deterministic news understanding to the existing news foundation. The backend now exposes `GET /api/v1/news/{id}/research`, powered by `app/services/intelligence/news_engine.py`.

Implemented:

* Rule-based event classification for Earnings, Dividend, Expansion, Acquisition, Regulatory, Management, Product Launch, Partnership, Litigation, Macro Economy, Exchange, Commodity, Currency, and Market Update.
* Importance scoring with Low, Medium, and High labels plus explicit reasons.
* Evidence reporting with source quality, data completeness, confidence, data used, and missing data.
* Related company, sector, asset type, educational topic, Learn Next, and knowledge graph outputs.
* Frontend News Intelligence panel in the dashboard latest-news section.
* TypeScript API/types for `NewsResearch`.

Architecture decisions:

* News Intelligence remains deterministic and evidence-based.
* It explains context and learning paths only; it does not infer future prices, generate buy/sell advice, call LLMs, run sentiment models, or personalize advice.
* Process-local caching is used for unchanged article research payloads.

Validation:

* `python -m pytest -q`: passed, 247 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Classification is keyword/rule-based and depends on currently stored article fields.
* Related company detection is limited by existing company/news/asset links and text matches.
* No live scraping, sentiment analysis, LLM summaries, alerts, recommendations, or portfolio actions are implemented.

Recommended Sprint 043:

* Add persisted news seed/runtime data for meaningful manual demo validation, then smoke-test `/api/v1/news/{id}/research` and the dashboard News Intelligence panel against real PostgreSQL-backed articles.




## Sprint 043 Business Intelligence Engine and Company Deep Dive

Sprint 043 adds deterministic business understanding to the Company Intelligence layer. The backend now exposes `GET /api/v1/companies/{ticker}/business` and `GET /api/v1/industries/{industry}`.

Implemented:

* Business Intelligence Engine for business summary, business model, revenue drivers, competitive position, industry position, maturity, geographic exposure, operational risks, educational notes, and graph expansion.
* Industry Intelligence Engine for descriptions, typical characteristics, common risks, common opportunities, economic sensitivity, cyclical/defensive profile, companies, Learn Next, and related industries.
* Competitor Engine for direct competitors, similar businesses, and related businesses with explicit relationship reasons.
* Company Deep Dive frontend panel on `/company/[ticker]`.
* Frontend API/types for Business Intelligence and Industry Intelligence.
* Tests covering business, industry, competitor, company business endpoint, and industry endpoint behavior.

Architecture decisions:

* Business Intelligence remains deterministic and evidence-based.
* It uses persisted company metadata, CompanyProfile fields, related assets, deterministic industry profiles, and competitor scoring.
* Missing facts are marked as unavailable instead of fabricated.
* Competitor links are educational research paths, not recommendations.
* No LLMs, predictions, buy/sell recommendations, alerts, live scraping, portfolio optimization, or personalized advice were added.

Validation:

* `python -m pytest -q`: passed, 253 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Industry profiles are deterministic starter profiles and do not yet cover every possible industry in depth.
* Competitor reasoning is limited to currently seeded companies and structured metadata.
* No frontend component test runner exists; Company Deep Dive rendering is validated by TypeScript and production build.

Recommended Sprint 044:

* Runtime-smoke `/api/v1/companies/DLTA/business`, `/api/v1/industries/Beverages`, and `/company/delta` against local PostgreSQL-backed data, then fix only confirmed data, responsive layout, or UX issues.



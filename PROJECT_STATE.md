# InvestGuide Project State

## Project Summary

* InvestGuide is an AI-powered Zimbabwean investment intelligence platform for ZSE, VFEX, REIT, macroeconomic, news, sentiment, personalization, and analytics-driven educational decision support.
* Current version: v0.1.0-alpha.

---

## Current Sprint

Sprint Number: Sprint 046

Sprint Goal: Add deterministic Dividend Intelligence with persisted dividend records, development-only fixture isolation, read-only APIs, company-page UI, future ingestion contracts, and runtime validation.

Current Tasks:

* [x] Ran Docker/PostgreSQL runtime validation.
* [x] Applied Alembic migration head `20260713_0002`.
* [x] Ran unified manual seed workflow with financial statement fixtures.
* [x] Smoke-tested `GET /api/v1/companies/DLTA/financials`.
* [x] Smoke-tested `GET /api/v1/companies/DLTA/financial-health`.
* [x] Route-smoke tested `/company/delta` against the Next.js dev server.
* [x] Added `ALLOW_DEVELOPMENT_DATA` environment guard.
* [x] Blocked development seed commands outside allowed development mode.
* [x] Added verified-over-development financial data precedence.
* [x] Added safe development-data cleanup dry-run/confirm workflow.
* [x] Added future ZSE/VFEX ingestion contract scaffolding.
* [x] Added tests for production guard, precedence, cleanup, empty data, and partial data transparency.
* [x] Ran Python tests, frontend lint, frontend type-check, and frontend build.
* [x] Updated backend README, frontend README, PROJECT_STATE.md, and context.md.

Sprint Exit Criteria:

* Financial endpoints pass PostgreSQL runtime smoke tests.
* Company Financial Dashboard route compiles and serves.
* Empty and partial financial-data states are honest.
* Development seeds are explicitly blocked in production.
* Development data cannot silently override verified data.
* Production financial reads exclude development rows.
* Safe development-data cleanup workflow exists and defaults to dry-run.
* Future verified source ingestion contracts exist.
* Validation passes.
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

Documentation: Stable - Sprint 046 Dividend Intelligence documentation added

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

Testing: frontend lint/type-check/build pass; `python -m pytest` from repository root runs backend and scraper tests with 280 tests passing

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

Sprint 046 should resolve stale local backend port listeners or standardize dev-server port discovery, then perform full browser QA for the Company Financial Dashboard with screenshots and fix only confirmed runtime, layout, or data-transparency issues.
---
## Definition of Done

Sprint 045 is complete because PostgreSQL runtime validation, financial endpoint smoke tests, Company Financial Dashboard route smoke, production development-data guard, verified-over-development precedence, safe cleanup workflow, future ingestion contracts, tests, frontend validation, and documentation updates are complete without adding live integrations, scraping, predictions, recommendations, alerts, watchlists, portfolio optimization, or personalized advice.
---
## Last Updated

* Date: 2026-07-13
* AI Agent: Codex
* Completed Task: Completed Sprint 046 Dividend Intelligence Engine and verified dividend data foundation.
---
## Validation Results

* Tests: `python -m pytest -q` passed, 280 tests, 1 non-blocking pytest cache permission warning.
* Frontend lint: `npm.cmd run lint` passed.
* Frontend type-check: `npm.cmd run type-check` passed.
* Frontend build: `npm.cmd run build` passed, 14 routes generated.
* Runtime route smoke: `/`, `/auth/signup`, `/auth/login`, `/dashboard`, `/assets`, `/assets/delta`, `/company/delta`, `/compare`, `/markets`, `/education`, and `/settings` returned 200 after dev-server compilation.
* Runtime API smoke: warmed `GET /api/v1/compare?asset_a=DLTA&asset_b=TIGZ` passed; warmed `GET /api/v1/companies/DLTA/related` passed with 4 related companies, 6 Learn Next topics, and 10 knowledge graph nodes.
* Runtime note: database diagnostics passed at revision `20260713_0002`. Port `8001` was occupied by a stale listener during Sprint 045, so financial endpoint smoke ran on port `8010`.

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



---

## Sprint 044 Financial Intelligence Engine

Sprint 044 adds deterministic financial statement understanding to the Company Intelligence layer.

Implemented:

* Persisted `income_statements`, `balance_sheets`, and `cash_flow_statements` models.
* Alembic migration `20260713_0002_create_financial_statements.py`.
* Duplicate-aware manual financial statement seed runner.
* Unified manual seed workflow now includes financial statements.
* Deterministic Financial Intelligence Engine for financial health, revenue, profitability, liquidity, leverage, cash flow, growth, stability, ratios, trends, educational summaries, ELI18 explanations, and transparency.
* `GET /api/v1/companies/{ticker}/financials`.
* `GET /api/v1/companies/{ticker}/financial-health`.
* Reusable Company Financial Dashboard components on `/company/[ticker]`.
* Backend tests for ratios, trend analysis, financial health, missing data, and endpoint envelopes.

Architecture Decisions:

* Financial Intelligence remains deterministic and evidence-based.
* Development financial fixtures are explicitly marked with `is_development_data` and source metadata.
* Ratio outputs include value, interpretation, why it matters, and educational explanation.
* Financial Health labels are educational assessments, not investment recommendations.
* Missing data and uncertainty are first-class parts of every financial payload.
* No LLMs, predictions, buy/sell recommendations, alerts, live scraping, portfolio optimization, watchlists, or personalized advice were added.

Validation:

* `python -m pytest -q`: passed, 260 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known Limitations:

* Financial seed data is development fixture data, not verified production filings.
* The ratio engine is deterministic and educational; it does not perform valuation, forecasting, or investment recommendation.
* Runtime smoke against local PostgreSQL-backed seed data is recommended for Sprint 045.

Recommended Sprint 045:

* Runtime-smoke financial endpoints and the Company Financial Dashboard against local PostgreSQL, then improve data transparency or UX only where real runtime validation reveals issues.


---

## Sprint 045 Financial Runtime Validation and Development Data Isolation

Sprint 045 validates the Financial Intelligence feature against local PostgreSQL and hardens the boundary between development fixtures and future verified production data.

Implemented:

* `ALLOW_DEVELOPMENT_DATA` backend setting.
* Central development data guard in `app/database/development_data_guard.py`.
* Production guard calls inside development seed functions and seed CLI entrypoints.
* Financial statement service precedence: verified rows win; development rows are returned only when fixture policy permits them.
* Safe cleanup command `python -m app.database.cleanup_development_data` with dry-run default and explicit `--confirm` deletion.
* Future verified ingestion contract package under `app/services/ingestion/`.
* Honest financial empty state on `/company/[ticker]` when no financial statement rows exist.
* Tests for fixture policy, production blocking, financial precedence, production exclusion, empty/partial financial outputs, and cleanup behavior.

Runtime Validation:

* `docker compose up -d`: PostgreSQL running.
* `python -m alembic upgrade head`: migrated to `20260713_0002`.
* `python -m app.database.seed`: completed after migration was rerun sequentially.
* `python backend/scripts/check_database.py`: connected, migrations current, current revision `20260713_0002`, seed data present, asset count 9.
* `GET /api/v1/companies/DLTA/financials`: passed on `http://127.0.0.1:8010`.
* `GET /api/v1/companies/DLTA/financial-health`: passed on `http://127.0.0.1:8010`.
* `/company/delta`: returned HTTP 200 from Next.js dev server.

Port Note:

* Requested backend port `8001` was occupied by a stale/unresolvable local listener during this session. Runtime financial smoke used clean port `8010` and this deviation is documented rather than hidden.

Validation:

* `python -m pytest -q`: passed, 268 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known Limitations:

* Financial rows are still development fixture data and not verified ZSE/VFEX filings.
* Future ingestion contracts are scaffolded only; no live source integration or scraper was added.
* Full visual browser QA with screenshots is still recommended.

Recommended Sprint 046:

* Resolve stale local port listeners or standardize dev-server port discovery, then perform full browser QA of the financial dashboard and fix only confirmed runtime, responsive, or transparency defects.


---

## Sprint 046 Direction Update

Sprint 046 should build the reusable verified data pipeline framework, not live ZSE/VFEX connectors.

Target architecture:

External Source -> Normalizer -> Validator -> Importer -> Database -> Research Engines -> Frontend

Scope guidance:

* Build source-agnostic pipeline contracts.
* Support future ZSE, VFEX, CSV imports, annual reports, APIs, and manual admin uploads through the same workflow.
* Keep frontend and research engines insulated from source-specific ingestion details.
* Do not implement live connectors until the pipeline framework is stable.

Recommended Sprint 046:

* Implement the reusable verified data pipeline framework with normalizer, validator, importer, audit/source metadata, and tests using local fixtures only.

---

## Sprint 046 Dividend Intelligence Engine

Sprint 046 adds deterministic Dividend Intelligence and persisted dividend data foundations.

Implemented:

* `dividends` table.
* `corporate_actions` table.
* Dividend and corporate-action ORM models and relationships.
* Manual development dividend seed runner.
* Unified development seed support for dividends.
* Production-safe dividend fixture isolation using the existing development-data guard.
* Safe cleanup reporting/deletion support for dividend fixtures.
* Dividend Intelligence Engine for status, history, yield availability, payout ratio, cash payout ratio, growth, consistency, sustainability, risks, education, ELI18, transparency, and learning topics.
* Read-only APIs: `GET /api/v1/companies/{ticker}/dividends` and `GET /api/v1/companies/{ticker}/dividend-intelligence`.
* Company page Dividend Intelligence section.
* Future source-agnostic ingestion contracts for dividends and corporate actions.

Runtime validation:

* Docker PostgreSQL running.
* Alembic current at `20260714_0002`.
* Manual seed passed.
* Database diagnostics passed.
* Dividend endpoints passed on backend port `8011`.
* `/company/delta` returned HTTP 200.

Validation:

* `python -m pytest -q`: passed, 280 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

Known limitations:

* Dividend fixture values are development-only sample data and not verified ZSE/VFEX records.
* Dividend yield remains unavailable until verified reference price data exists.
* No live ZSE/VFEX integrations, scraping, predictions, recommendations, alerts, watchlists, portfolio optimization, or personalized advice were added.

Recommended Sprint 047:

* Build the reusable verified data pipeline framework: External Source -> Normalizer -> Validator -> Importer -> Database -> Research Engines -> Frontend. Use local fixtures only and keep live ZSE/VFEX connectors out of scope.

---

## Sprint 047 Verified Data Pipeline Framework

Sprint 047 builds the reusable verified-data ingestion framework without adding live connectors, scraping, public ingestion APIs, AI, recommendations, predictions, portfolio features, watchlists, alerts, or frontend product changes.

Implemented:

* Source-agnostic ingestion contracts for source metadata, verification status, import modes, normalized records, validation issues, import results, and pipeline results.
* Local JSON and CSV source adapters with checksum, record count, dataset version, and development-data metadata.
* Normalization helpers for tickers, exchanges, currencies, dates, datetimes, decimals, URLs, company names, statement periods, dividend types, corporate action types, whitespace, and UTF-8 BOM handling.
* Runtime normalizers, validators, and importers for companies, income statements, dividends, and news.
* Normalized contracts for companies, assets, company profiles, income statements, balance sheets, cash flow statements, dividends, corporate actions, news, and market snapshots.
* `IngestionPipeline` orchestration: source adapter -> normalizer -> validator -> importer -> audit.
* `IngestionRegistry` mapping supported entities to their components.
* CLI entry point: `python -m app.services.ingestion.cli`.
* Audit persistence through `ingestion_runs` and Alembic migration `20260715_0001_create_ingestion_runs.py`.
* Local development/test ingestion fixtures for companies, CSV companies, income statements, dividends, and news.
* Tests for local source adapters, registry wiring, dry-run behavior, audit rows, strict rejection, idempotent lenient imports, and compatibility with existing financial/dividend intelligence engines.
* Architecture documentation in `docs/architecture/data-ingestion-pipeline.md`.

Architecture Decisions:

* The ingestion pipeline is the canonical future path for ZSE, VFEX, CSV, JSON, annual reports, APIs, manual curation, and admin uploads.
* Dry-run remains the default and does not write entity rows, but audit rows are recorded for traceability.
* Development fixture imports require the existing development-data policy for non-dry-run modes.
* Verified/non-development data must not be overwritten by lower-quality development fixture rows.
* Frontend contracts remain unchanged; UI and intelligence engines consume persisted backend data through existing APIs.
* Missing parent references in lenient imports are skipped and reported as warnings; strict validation remains available for all-or-nothing batches.

Runtime Validation:

* `docker compose up -d`: PostgreSQL container running.
* `python -m alembic upgrade head`: migrated to `20260715_0001`.
* `python -m alembic current`: `20260715_0001 (head)`.
* Company dry-run fixture import: passed, 2 valid records, duplicate-aware update plan.
* Income statement dry-run fixture import: passed, 2 valid records.
* Company lenient fixture import: passed, 2 updates.
* Income statement lenient fixture import: passed, 2 updates.
* Dividend lenient fixture import: passed, 1 insert and 1 update after fixture alignment.
* News lenient fixture import: passed, 2 inserts.
* `python -m app.database.seed`: passed.
* `python scripts/check_database.py`: connected, migrations current, seed data present, asset count 9.
* Backend smoke on `http://127.0.0.1:8012`: health, financial health, dividend intelligence, and news endpoints passed.

Validation:

* `python -m pytest -q`: passed, 236 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known Limitations:

* Runtime importers are implemented for companies, income statements, dividends, and news only; other normalized contracts are ready but not persisted until their models/importers are needed.
* Source adapters are local JSON/CSV only; no live ZSE/VFEX connector, scraper, external API, scheduler, or admin UI exists.
* Fixture data remains development/test data and is not verified production financial information.
* Audit rows store run summaries and source metadata, not raw source documents.

Recommended Sprint 048:

* Add verified balance sheet and cash flow pipeline importers using the same framework, then runtime-smoke financial intelligence with all three statement types imported through the pipeline before any live source work begins.

---

## Sprint 048 Verified Data Ingestion Framework Completion

Sprint 048 completes the backend verified data ingestion framework coverage for the current InvestGuide intelligence stack.

Status: Complete

Implemented:

* Asset ingestion normalizer, validator, importer, and fixture coverage.
* Company Profile ingestion normalizer, validator, importer, and fixture coverage.
* Balance Sheet ingestion normalizer, validator, importer, and fixture coverage.
* Cash Flow Statement ingestion normalizer, validator, importer, and fixture coverage.
* Corporate Action ingestion normalizer, validator, importer, and fixture coverage.
* Market Snapshot model, Alembic migration, service, importer, validator, and fixture coverage.
* Ingestion registry coverage for all current entities: companies, assets, company profiles, income statements, balance sheets, cash flow statements, dividends, corporate actions, news, and market snapshots.
* Dividend Intelligence now uses the latest acceptable persisted market snapshot as a reference-price source when available.

Architecture decisions:

* The source-agnostic ingestion pipeline remains the canonical path for future ZSE, VFEX, CSV, JSON, annual report, API, and manual curation imports.
* Frontend contracts remain unchanged and do not branch on source-specific ingestion details.
* Dry-run remains safe by default; lenient imports valid rows and records rejected rows; strict mode rejects the full batch when validation fails.
* Verified/non-development rows remain protected from lower-quality development fixture overwrites.
* Corporate-action fixture ingestion maps only to the current persisted `CorporateAction` schema; future richer action fields require a separate model/migration decision.

Runtime validation:

* Docker PostgreSQL running.
* Alembic migrated to `20260715_0002 (head)`.
* Database diagnostics passed with seed data present and asset count 9.
* Dry-run and lenient imports passed for assets, company profiles, balance sheets, cash flow statements, corporate actions, and market snapshots.
* Backend smoke passed for company profile, financials, financial health, dividend intelligence, asset assessment, assets, and news.
* Frontend route smoke passed for `/company/delta`, `/assets/delta`, `/compare`, and `/dashboard`.

Validation:

* `python -m pytest -q`: passed, 240 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed after separate rerun; initial concurrent run raced with build-generated `.next/types` regeneration.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Source adapters remain local JSON/CSV only.
* No live ZSE/VFEX connector, scraper, scheduler, public ingestion endpoint, or admin upload UI exists yet.
* Fixture rows remain development/test data and are not verified production financial information.
* Corporate action persistence is intentionally limited to the existing model fields.

Recommended Sprint 049:

* Build operator-facing ingestion diagnostics and data quality reports, or begin one controlled live-source adapter only after the pipeline can clearly report source health, rejection reasons, and import provenance.

---

## Sprint 049 Ingestion Operations, Data Quality, and Provenance Dashboard

Status: Complete

Implemented:

* Record-level `IngestionRecordIssue` persistence with safe summaries only.
* Alembic migration `20260715_0003_add_ingestion_record_issues.py`.
* Stable deterministic issue codes for validation, import, rejection, and database write failures.
* Data-quality scoring for completeness, validity, provenance, freshness, consistency, and overall quality.
* Central freshness targets.
* Source-health summaries.
* Entity-level data-quality summaries.
* Company-level data-quality reports and deterministic operator recommendations.
* Development-data visibility in quality summaries and internal dashboard.
* Internal read-only APIs under `/api/v1/internal`.
* Internal operations dashboard at `/internal/data-operations`.
* Internal run detail page at `/internal/data-operations/runs/[id]`.
* Diagnostics CLI under `python -m app.services.ingestion.diagnostics`.
* Safe CSV/JSON rejected-record export.
* Operations documentation in `docs/operations/data-quality-and-ingestion-operations.md`.

Architecture decisions:

* Internal operations are read-only and development/debug guarded until admin roles exist.
* Issue rows store concise safe summaries, not raw source documents or secrets.
* Quality scoring is operational data quality, not financial health or investment scoring.
* Development fixtures are visible and explicitly penalized in production-readiness scoring.
* No live connector, scraper, scheduler, public ingestion endpoint, AI, prediction, or recommendation was added.

Runtime validation:

* Docker PostgreSQL running.
* Alembic current at `20260715_0003 (head)`.
* Generated successful dry-run, successful lenient, warning/rejection, and failed strict ingestion runs.
* Diagnostics CLI passed for runs, sources, quality, company `DLTA`, and CSV issue export.
* Database diagnostics passed.
* Internal API smoke passed on backend port `8014`.
* Internal frontend pages returned HTTP 200 on port `3021`.

Validation:

* `python -m pytest -q`: passed, 247 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 15 routes generated.

Known limitations:

* Internal access uses development/debug protection because admin roles do not exist yet.
* No live ZSE/VFEX connector, scheduler, external API, scraping, or public ingestion write path exists.
* Quality scoring is deterministic and heuristic; it should evolve as verified live data and admin workflows mature.

Recommended Sprint 050:

* Add admin-role protection for internal operations or implement one controlled live-source adapter only after operator access, source health, issue reporting, and provenance review are accepted.

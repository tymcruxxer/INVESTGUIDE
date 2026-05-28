INVESTGUIDE
Technical Planning Document
System Architecture, Engineering Blueprint & Implementation Strategy

Field	Detail
Document Type	Technical Planning Document
Founder	Spencer Jaka
Version	1.0
Primary Stack	Next.js · FastAPI · PostgreSQL · Redis · Python
Architecture	Modular Monolith (MVP) → Microservices (Scale)
AI Strategy	RAG + Open-source LLMs + OpenAI API
Deployment	Vercel · Railway/Render · Supabase · Upstash Redis
 
1. System Architecture Overview
Architecture Principle
InvestGuide uses a modular, service-oriented architecture designed for scalability, maintainability, AI-assisted development, independent module deployment, and future regional expansion. Responsibilities are separated into distinct layers to avoid tightly coupled systems.

1.1 High-Level System Layers
Layer	Responsibility	Key Technologies
Frontend Presentation	UI, dashboards, charts, AI chat interface	Next.js, TailwindCSS, shadcn/ui, Recharts
Backend API	Business logic, analytics, auth, AI orchestration	FastAPI, Python, JWT, Pydantic
Data Intelligence	Market data, scraping, sentiment, macro ingestion	BeautifulSoup, Playwright, Scrapy, Pandas
Analytics Engine	Scoring, rankings, volatility, macro adjustments	Python, NumPy, Pandas
AI Interpretation	Summarization, recommendations, conversational AI	OpenAI API, RAG, LangChain/custom
Data Storage	Persistent storage, caching, historical data	PostgreSQL, Redis, S3/R2
Infrastructure & DevOps	Deployment, monitoring, scheduling, CI/CD	Docker, GitHub Actions, Sentry

1.2 Intelligence Pipeline Flow
Market Data Collection
        +
News Aggregation
        +
Macroeconomic Data
        +
Institutional Research
        ↓
Normalization Pipeline
        ↓
Analytics Engine
        ↓
Sentiment Engine
        ↓
Recommendation Engine
        ↓
RAG Retrieval Layer
        ↓
AI Interpretation Layer
        ↓
Frontend Intelligence Delivery

 
2. Technology Stack
2.1 Frontend Stack
Technology	Purpose	Rationale	Version Target
Next.js (App Router)	Primary framework	SSR, performance, routing	Latest stable
TypeScript	Type safety	Prevents runtime errors at scale	5.x
TailwindCSS	Styling	Utility-first, dark mode support	3.x
shadcn/ui	Component system	Accessible, customizable, Radix-based	Latest
Recharts	Primary charting	React-native charts, performant	Latest
Chart.js	Secondary charting	Flexible for complex visualizations	Latest
D3.js	Advanced viz (future)	Complex custom analytics charts	Latest
Zustand	State management	Lightweight, simple API	Latest
TanStack Query	Data fetching/caching	Server state, background refetch	v5
React Hook Form	Forms	Performant form handling	Latest
Zod	Validation	Type-safe schema validation	Latest
Framer Motion	Animations	Premium motion for fintech feel	Latest

2.2 Backend Stack
Technology	Purpose	Rationale	Version Target
FastAPI	Primary API framework	Async, fast, Python ecosystem	Latest
SQLAlchemy	ORM	Powerful, migration-friendly	2.x
Alembic	DB migrations	Schema version control	Latest
Pydantic	Data validation	Type-safe request/response schemas	v2
python-jose	JWT tokens	Secure authentication tokens	Latest
passlib + bcrypt	Password hashing	Industry-standard security	Latest
APScheduler	Job scheduling (MVP)	Simpler than Celery for MVP	Latest
Celery	Job scheduling (future)	Distributed task processing	Latest
BeautifulSoup	HTML scraping	Lightweight structured parsing	4.x
Playwright	Dynamic scraping	JS-rendered content support	Latest
Pandas + NumPy	Data processing	Analytics and data manipulation	Latest
pdfplumber / PyMuPDF	PDF extraction	Financial report processing	Latest

2.3 Database & Infrastructure Stack
Technology	Purpose	Provider	Notes
PostgreSQL	Primary relational DB	Supabase / Neon	All structured data
Redis	Caching layer	Upstash Redis	API, AI, session caching
pgvector (future)	Vector search	PostgreSQL extension	RAG embeddings
Weaviate (future)	Vector DB alternative	Cloud or self-hosted	Semantic search
AWS S3 / R2	File storage	Cloudflare R2 preferred	PDFs, reports, logos
Vercel	Frontend hosting	Vercel	Next.js optimized
Railway / Render	Backend hosting	Railway preferred	FastAPI container
GitHub Actions	CI/CD	GitHub	Automated pipelines
Docker	Containerization	Local + production	All services
Sentry	Error monitoring	Sentry.io	Frontend + backend
PostHog	Analytics	PostHog	User behavior tracking
Better Stack	Uptime monitoring	Better Stack	API health

 
3. Repository & Folder Structure
3.1 Monorepo Architecture
Monorepo Rationale
Monorepo architecture enables easier AI-agent coordination, shared typing, centralized architecture documentation, and simpler deployment. All services live in one repository with clear module boundaries.

3.2 High-Level Repository Structure
/investguide
    /frontend          ← Next.js application
    /backend           ← FastAPI application
    /ai-services       ← AI/RAG orchestration
    /scrapers          ← Data ingestion pipeline
    /shared            ← Shared types and utilities
    /docs              ← Architecture documentation
    /infrastructure    ← Docker, CI/CD configs

3.3 Frontend Structure
/frontend
    /app               ← Next.js App Router pages
    /components        ← Reusable UI components
    /features          ← Feature-based modules
      /dashboard
      /markets
      /stocks
      /vfex
      /reits
      /news
      /sentiment
      /ai-assistant
      /macroeconomics
      /education
    /hooks             ← Custom React hooks
    /services          ← API client layer
    /store             ← Zustand state stores
    /types             ← TypeScript type definitions
    /utils             ← Helper functions
    /styles            ← Global styles

3.4 Backend Structure
/backend
    /api               ← FastAPI route definitions
    /services          ← Business logic services
    /analytics         ← Analytics engine modules
    /models            ← SQLAlchemy database models
    /schemas           ← Pydantic request/response schemas
    /database          ← DB connection and session management
    /jobs              ← Scheduled background jobs
    /core              ← Auth, config, middleware
    /utils             ← Shared utilities
    /tests             ← Pytest test suite

3.5 AI Services Structure
/ai-services
    /prompts           ← System prompt templates
    /rag               ← RAG pipeline components
    /embeddings        ← Embedding generation
    /summaries         ← AI summary generators
    /agents            ← AI agent orchestration

3.6 Scrapers Structure
/scrapers
    /zse               ← ZSE data scrapers
    /vfex              ← VFEX data scrapers
    /rbz               ← RBZ macroeconomic data
    /zimstat           ← ZIMSTAT indicators
    /news              ← Financial journalism scrapers
    /research          ← Institutional research scrapers

 
4. Database Architecture
4.1 Database Design Philosophy
The database supports historical analysis, time-series intelligence, macroeconomic contextualization, AI retrieval systems, sentiment analysis, and future predictive systems. PostgreSQL is the primary relational database; Redis provides caching; pgvector (future) enables semantic search.

4.2 Core Database Entities
USERS
users
  - id                    UUID / serial primary key
  - full_name             VARCHAR
  - email                 VARCHAR UNIQUE
  - password_hash         VARCHAR
  - auth_provider         VARCHAR (email / google)
  - subscription_plan     VARCHAR (free / premium)
  - risk_profile          VARCHAR (conservative / moderate / aggressive)
  - experience_level      VARCHAR (beginner / intermediate / advanced)
  - preferred_investments JSONB
  - created_at            TIMESTAMP
  - updated_at            TIMESTAMP

ASSETS
assets
  - id                    SERIAL PRIMARY KEY
  - ticker                VARCHAR UNIQUE
  - company_name          VARCHAR
  - exchange              VARCHAR (ZSE / VFEX)
  - sector                VARCHAR
  - industry              VARCHAR
  - asset_type            VARCHAR (equity / REIT / bond)
  - currency              VARCHAR (ZWG / USD)
  - description           TEXT
  - logo_url              VARCHAR
  - official_website      VARCHAR
  - market_cap            NUMERIC
  - listing_date          DATE
  - status                VARCHAR (active / suspended)
  - created_at            TIMESTAMP

HISTORICAL_PRICES
historical_prices
  - id                    SERIAL PRIMARY KEY
  - asset_id              INTEGER FK → assets.id
  - date                  DATE
  - open_price            NUMERIC
  - high_price            NUMERIC
  - low_price             NUMERIC
  - close_price           NUMERIC
  - adjusted_close        NUMERIC
  - volume                BIGINT
  - currency              VARCHAR
  - created_at            TIMESTAMP
  INDEX: (asset_id, date)

NEWS_ARTICLES
news_articles
  - id                    SERIAL PRIMARY KEY
  - source_name           VARCHAR
  - source_url            VARCHAR
  - article_title         VARCHAR
  - article_content       TEXT
  - summary               TEXT
  - publication_date      TIMESTAMP
  - author                VARCHAR
  - category              VARCHAR
  - sentiment_status      VARCHAR (pending / processed)
  - created_at            TIMESTAMP

SENTIMENT_ANALYSIS
sentiment_analysis
  - id                    SERIAL PRIMARY KEY
  - article_id            INTEGER FK → news_articles.id
  - asset_id              INTEGER FK → assets.id
  - sentiment_score       NUMERIC (-1.0 to +1.0)
  - sentiment_label       VARCHAR (positive / neutral / negative)
  - confidence_score      NUMERIC (0.0 to 1.0)
  - model_used            VARCHAR
  - processed_at          TIMESTAMP

MACROECONOMIC_INDICATORS
macroeconomic_indicators
  - id                    SERIAL PRIMARY KEY
  - indicator_name        VARCHAR (inflation / exchange_rate / interest_rate)
  - indicator_value       NUMERIC
  - indicator_unit        VARCHAR (%, rate, index)
  - source                VARCHAR (RBZ / ZIMSTAT)
  - reporting_date        DATE
  - category              VARCHAR
  - created_at            TIMESTAMP

AI_SUMMARIES
ai_summaries
  - id                    SERIAL PRIMARY KEY
  - asset_id              INTEGER FK → assets.id
  - summary_type          VARCHAR (company / market / sector)
  - summary_content       TEXT
  - model_used            VARCHAR
  - generated_at          TIMESTAMP
  - expiration_time       TIMESTAMP

4.3 Key Database Relationships
Relationship	Type	Purpose
users → watchlists	One-to-many	Each user tracks multiple assets
assets → historical_prices	One-to-many	Each asset has full price history
assets → dividends	One-to-many	Each asset has dividend history
assets ↔ news_articles	Many-to-many (via junction)	Articles linked to multiple assets
news_articles → sentiment_analysis	One-to-many	Multiple sentiment models per article
assets → ai_summaries	One-to-many	Multiple summary types per asset

4.4 Redis Caching Key Strategy
asset:{ticker}:summary          → AI summary (TTL: 6 hours)
asset:{ticker}:prices            → Recent price data (TTL: 1 hour)
asset:{ticker}:sentiment         → Sentiment aggregate (TTL: 2 hours)
macro:overview                   → Macro snapshot (TTL: 1 hour)
news:latest                      → News feed (TTL: 15 minutes)
recommendations:{risk_profile}   → Recommendation set (TTL: 3 hours)

 
5. API Architecture & Contracts
5.1 API Design Principles
•	RESTful APIs for MVP; GraphQL consideration for future flexibility
•	Versioned endpoints: /api/v1/ (MVP), /api/v2/ (future)
•	Consistent response envelope across all endpoints
•	Pagination, filtering, and search on all list endpoints
•	Redis caching on frequently requested endpoints

5.2 Global Response Structure
// Success Response
{
  "success": true,
  "message": "Assets retrieved successfully",
  "data": {},
  "meta": { "page": 1, "limit": 20, "total": 200, "has_next": true }
}
 
// Error Response
{
  "success": false,
  "message": "Invalid ticker symbol",
  "error_code": "INVALID_TICKER",
  "details": {}
}

5.3 Core API Endpoints
Module	Method	Endpoint	Description
Auth	POST	/api/v1/auth/register	User registration
Auth	POST	/api/v1/auth/login	Login + JWT tokens
Auth	POST	/api/v1/auth/refresh	Refresh access token
Users	GET	/api/v1/users/me	Current user profile
Users	PATCH	/api/v1/users/preferences	Update user preferences
Assets	GET	/api/v1/assets	List all assets (paginated, filtered)
Assets	GET	/api/v1/assets/{ticker}	Asset detail
Assets	GET	/api/v1/assets/{ticker}/prices	Historical price data
Assets	GET	/api/v1/assets/{ticker}/dividends	Dividend history
Assets	GET	/api/v1/assets/{ticker}/sentiment	Sentiment analysis
Assets	GET	/api/v1/assets/{ticker}/analytics	Analytics scores
Assets	GET	/api/v1/assets/{ticker}/ai-summary	AI-generated summary
Assets	GET	/api/v1/assets/{ticker}/news	Asset-specific news
News	GET	/api/v1/news	Global news feed
Research	GET	/api/v1/research/reports	Research reports
Sentiment	GET	/api/v1/sentiment/trends	Market sentiment trends
Analytics	GET	/api/v1/recommendations	Personalized recommendations
Macro	GET	/api/v1/macro/overview	Macro snapshot
Macro	GET	/api/v1/macro/inflation	Inflation history
AI	POST	/api/v1/ai/chat	AI assistant conversation
Watchlists	GET	/api/v1/watchlists	User watchlist
Watchlists	POST	/api/v1/watchlists	Add to watchlist
Alerts	GET	/api/v1/alerts	User alerts
Alerts	POST	/api/v1/alerts	Create alert
Search	GET	/api/v1/search	Global search

5.4 API Security
Security Layer	Implementation	Scope
JWT Authentication	python-jose, Bearer tokens, refresh rotation	All authenticated endpoints
Rate Limiting	Middleware, Redis-backed counters	AI: 20/min, Search: 60/min
Input Validation	Pydantic schemas, strict typing	All request bodies
CORS Protection	FastAPI CORS middleware, whitelist origins	All endpoints
Password Security	bcrypt hashing, strength requirements	Auth endpoints
Feature Gating	Subscription middleware, entitlement checks	Premium endpoints

 
6. Data Ingestion & Scraping Architecture
6.1 Scraping Pipeline Flow
Scheduler Trigger (APScheduler)
        ↓
Source Fetch (requests / Playwright)
        ↓
HTML / PDF Parsing (BeautifulSoup / pdfplumber)
        ↓
Content Extraction (source-specific parsers)
        ↓
Normalization (tickers, dates, currencies, names)
        ↓
Deduplication (title similarity + semantic hash)
        ↓
Sentiment Processing (VADER → FinBERT)
        ↓
Embedding Generation (BGE / E5 embeddings)
        ↓
Database Storage (PostgreSQL)
        ↓
AI Summary Generation (cached to ai_summaries)

6.2 Data Sources by Tier
Tier	Source	Type	Frequency
Tier 1 — Official	ZSE	Market data	Daily
Tier 1 — Official	VFEX	Market data	Daily
Tier 1 — Official	RBZ	Macro indicators	Daily/Weekly
Tier 1 — Official	ZIMSTAT	Economic data	Weekly
Tier 2 — Institutional	IH Securities	Research reports	As published
Tier 2 — Institutional	MMC Capital	Research reports	As published
Tier 2 — Institutional	Old Mutual Investment	Research reports	As published
Tier 3 — Journalism	Financial Gazette	News articles	Every 15–30 min
Tier 3 — Journalism	NewsDay Business	News articles	Every 15–30 min
Tier 3 — Journalism	Herald Business	News articles	Every 15–30 min

6.3 Scheduled Job Frequencies
Job	Frequency
Market data ingestion (ZSE/VFEX prices)	Daily — post-market close
Financial news scraping	Every 15–30 minutes
Macroeconomic indicator updates (RBZ)	Daily
ZIMSTAT economic data	Weekly
AI summary regeneration	Every 6 hours
Sentiment recalculation	Every 2 hours
Recommendation engine recalculation	Every 3 hours
Redis cache refresh	Per TTL (see caching section)

 
7. Analytics Engine
7.1 Analytics Categories & Formulas
Performance Analytics
CAGR = ((End Value / Begin Value) ^ (1 / Years)) - 1
Rolling Return (N days) = (Close[today] - Close[today-N]) / Close[today-N]
Max Drawdown = (Trough Value - Peak Value) / Peak Value

Risk Scoring
Volatility = Standard Deviation of Daily Returns (annualized)
Annualized Volatility = Daily Volatility × sqrt(252)
Risk Level: Low (<15%), Moderate (15-30%), High (30-50%), Speculative (>50%)

Recommendation Scoring Formula
Final Score =
  (Performance Score  × 0.25)
+ (Risk Score         × 0.20)
+ (Sentiment Score    × 0.20)
+ (Macro Adjustment   × 0.15)
+ (Dividend Stability × 0.20)
 
Score range: 0–100
Thresholds: Strong (>75) | Moderate (50–75) | Caution (<50)

7.2 Macroeconomic Adjustment Logic
Macro Condition	Effect	Adjusted Weight
High inflation (>30%)	Favors USD assets, VFEX, exporters	Increase VFEX weight, decrease ZWG assets
Rising gold prices	Favors mining stocks, gold-linked companies	Increase mining sector score
Currency instability	Increases defensive demand, USD preference	Increase USD-denominated asset score
High interest rates	Favors money market, fixed income	Adjust equity vs fixed income balance
Stable macro environment	Standard weighting applies	Default weights maintained

7.3 Sentiment Scoring System
Sentiment Score Range: -1.0 (Extremely Negative) to +1.0 (Extremely Positive)
 
MVP Model: VADER + TextBlob
Advanced Model: FinBERT (financial domain-specific)
 
Aggregate Sentiment =
  (Article Sentiment × 0.40)
+ (Institutional Outlook × 0.35)
+ (Market Momentum × 0.25)
 
Confidence Score: 0.0 – 1.0 (model certainty indicator)

 
8. AI & RAG Architecture
8.1 AI System Philosophy
Core AI Principle
AI exists to explain, summarize, contextualize, and educate. It does NOT replace analytics. Analytics drive intelligence; AI communicates it. Responses must always be grounded in retrieved data — never hallucinated.

8.2 RAG Pipeline
User Question
        ↓
Context Retrieval (vector search on embeddings)
        ↓
Relevant Documents Retrieved (ranked by recency + relevance + source trust)
        ↓
Analytics Injection (live scores, metrics, macro data)
        ↓
Structured Prompt Construction
        ↓
LLM Response Generation (OpenAI / local model via Ollama)
        ↓
Validation Layer (hallucination check, ticker verification)
        ↓
Frontend Response (streaming)

8.3 AI Model Strategy
Stage	Model	Provider
MVP Development	Qwen / DeepSeek / Gemma (open-source)	Ollama (local)
MVP Production	OpenAI GPT-4o-mini / Claude Haiku	API — cost-efficient
Premium Features	OpenAI GPT-4o / Claude Sonnet	API — higher capability
Future Local	Fine-tuned FinBERT for sentiment	Self-hosted
Embeddings	BGE / E5 / Nomic embeddings	Ollama or API

8.4 Master AI System Prompt
You are InvestGuide AI, an AI-powered Zimbabwean investment intelligence assistant.
 
Your role:
- Explain investment concepts clearly
- Summarize financial intelligence using retrieved context
- Contextualize macroeconomic conditions
- Provide balanced, educational investment insights
- Simplify financial analysis for all experience levels
 
You are NOT:
- A guaranteed prediction engine
- A speculative trading advisor
- A financial advisor promising returns
 
Always:
- Explain reasoning transparently
- Acknowledge uncertainty when data is incomplete
- Reference supporting analytics and sentiment data
- Avoid definitive profit claims
- Prioritize education and explainability
 
Use the provided context, analytics, and macroeconomic data to generate
grounded, accurate, and helpful responses.

8.5 AI Validation Layer
Check Type	Method	Action on Failure
Ticker verification	Cross-reference against assets table	Flag or reject response
Metric range check	Verify values within realistic bounds	Flag uncertain output
Source grounding	Require retrieved context references	Prompt for retrieval before response
Certainty language	Detect absolute claims	Inject uncertainty qualifier
Hallucination detection	Compare claims to retrieved documents	Require source citation

 
9. Development Phases & Implementation
9.1 Development Priority Order
Strategic Principle
Build layer-by-layer, NOT feature-by-feature. Data infrastructure must precede analytics, which must precede AI. Dashboards built on top of structured intelligence — never before it.

Priority	Layer	Rationale
1	Data Infrastructure	Everything else depends on reliable data
2	Analytics Systems	Intelligence before interfaces
3	Backend APIs	Contracts before frontend consumption
4	Frontend Dashboards	UI built on real data and real APIs
5	AI Orchestration	AI added after analytics are proven
6	Advanced Features	Personalization, alerts, premium features last

9.2 Phase-by-Phase Delivery
Phase	Focus	Key Deliverables	Success Criteria
1	Foundation	FastAPI, PostgreSQL, auth, Next.js setup, Docker, CI/CD	Frontend + backend deployed, DB connected, auth working
2	Market Data	Asset DB, historical prices, market APIs, dashboard foundations	Live market data displayed, assets searchable, charts functional
3	News Pipeline	Scrapers, normalization, deduplication, news dashboard	News ingestion automated, articles linked to assets
4	Analytics	Risk scoring, performance analytics, recommendation engine	Analytics visible on asset pages, rankings functional
5	AI Systems	Sentiment engine, AI assistant, RAG pipeline, AI summaries	AI assistant operational, grounded summaries functional
6	Personalization	Watchlists, alerts, preference-aware dashboards	Personalized experience fully operational
7	Premium	Premium subscriptions, advanced analytics, portfolio tracking	Revenue model activated

 
10. AI-Agent Development System
10.1 AI-Agent Engineering Rules
•	Never prompt: "Build the whole app." — Always define isolated modules with clear interfaces
•	Every coding prompt must include: objective, context, technical constraints, expected outputs, validation requirements
•	All AI-generated code must follow strict folder structure, naming conventions, and modular boundaries
•	Review all generated code manually before committing
•	Maintain centralized architecture documentation that AI agents always receive as context

10.2 Master AI-Agent Context Prompt
You are building InvestGuide, an AI-powered Zimbabwean investment
intelligence platform focused on ZSE, VFEX, REITs, macroeconomic
intelligence, and AI-powered investment explanations.
 
Tech Stack:
Frontend: Next.js App Router, TypeScript, TailwindCSS, shadcn/ui,
          Zustand, React Query
Backend:  FastAPI, PostgreSQL, SQLAlchemy, Redis, Python
 
Architecture: Modular monolith, service-oriented modules,
              feature-based frontend organization
 
Engineering Principles:
- Type safety throughout
- Modularity and clean architecture
- Production-grade patterns
- Responsive design with dark/light mode
- AI-agent-friendly structure
 
Rules:
- Analytics drive intelligence; AI explains it
- Avoid hardcoded logic and monolithic files
- Use reusable components and scalable folder structures
- Follow /backend, /frontend, /scrapers, /ai-services structure

10.3 Module Prompt Template
Objective:
  [What this module does]
 
Context:
  [How it fits into InvestGuide's architecture]
 
Requirements:
  [Specific functionality list]
 
Technical Constraints:
  - Follow InvestGuide backend/frontend architecture
  - Modular monolith structure
  - Type-safe code (TypeScript / Pydantic)
  - Production-ready patterns
 
Expected Output:
  [List of expected files / components / APIs]
 
Validation:
  [Testing expectations and success criteria]

 
11. Testing Strategy
11.1 Testing Framework
Layer	Tools	Test Coverage
Frontend	Playwright, Cypress	Responsiveness, navigation, charts, dark/light mode
Backend	Pytest	API endpoints, analytics, auth, database logic
AI Systems	Custom evaluation suite	Hallucination rates, groundedness, consistency
Scrapers	Pytest + fixture data	Extraction reliability, deduplication, parser failures
Integration	End-to-end Playwright	Full user journey testing

12. Infrastructure & Deployment
12.1 Deployment Architecture
Service	Provider	Notes
Frontend	Vercel	Next.js optimized, global CDN
Backend API	Railway / Render	FastAPI container, auto-scaling
Database	Supabase / Neon PostgreSQL	Managed postgres, point-in-time recovery
Redis Cache	Upstash Redis	Serverless Redis, per-request billing
File Storage	Cloudflare R2	PDFs, reports, logos — zero egress fees
AI (Dev)	Ollama (local)	Free, fast iteration
AI (Prod)	OpenAI API / Groq / Together AI	Hybrid based on cost/performance
Monitoring	Sentry + PostHog + Better Stack	Errors, analytics, uptime

12.2 CI/CD Pipeline
On Pull Request:
  → Lint frontend (ESLint, TypeScript check)
  → Lint backend (flake8, mypy)
  → Run backend tests (Pytest)
  → Build Docker images
 
On Merge to Main:
  → Run full test suite
  → Build and push Docker images
  → Deploy frontend to Vercel
  → Deploy backend to Railway/Render
  → Run smoke tests
  → Alert on failure (Sentry)

InvestGuide Technical Planning Document v1.0 — Confidential — Spencer Jaka

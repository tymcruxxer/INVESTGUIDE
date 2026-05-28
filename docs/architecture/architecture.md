INVESTGUIDE
AI Agent Master Blueprint
Complete Product, Business & Technical Reference for AI-Assisted Development

Field	Detail
Document Type	AI Agent Master Blueprint — Combined Reference
Founder	Spencer Jaka
Platform	InvestGuide
Version	1.0
Scope	PRD + Startup Blueprint + Technical Planning Document
Primary Use	AI-agent context document for full-stack development
Architecture	Modular Monolith (MVP) → Microservices at Scale
Core Stack	Next.js · FastAPI · PostgreSQL · Redis · Python · OpenAI API
Markets	ZSE · VFEX · REITs · Macroeconomic Intelligence

⚠ IMPORTANT FOR AI AGENT
THIS IS THE MASTER DOCUMENT FOR AI-ASSISTED DEVELOPMENT. Every coding session should begin by providing this document as context. It contains the complete architecture, feature specifications, database schemas, API contracts, prompt templates, and engineering rules that all AI agents must follow. Do not deviate from the folder structures, naming conventions, or module boundaries defined herein.
 
PART 1
Product Definition & Strategy

1.1 Platform Overview
What InvestGuide Is
InvestGuide is an AI-powered Zimbabwean investment intelligence and analytics platform. It helps retail investors, young professionals, diaspora investors, SMEs, and beginner market participants make informed investment decisions using quantitative analytics, macroeconomic intelligence, financial news aggregation, institutional research synthesis, AI-powered explanations, and interactive dashboards.

InvestGuide IS	InvestGuide IS NOT
Investment intelligence platform	A brokerage or trading platform
Financial analytics platform	An automated trading bot
Market research assistant	A get-rich-quick platform
AI-powered decision-support system	A licensed financial advisor
Educational investment platform	A speculative prediction engine

1.2 Vision & Mission
Vision
To become Zimbabwe's leading AI-powered investment intelligence platform that empowers ordinary citizens to make smarter, data-driven financial decisions.

Mission
InvestGuide exists to bridge the gap between institutional-grade financial intelligence and everyday Zimbabwean investors by transforming fragmented market information into understandable, actionable insights.

1.3 Target Users
User Segment	Profile	Primary Needs
Young Professionals	Salaried employees, beginner investors	Wealth building, passive income, education
Diaspora Investors	Zimbabweans abroad with USD income	VFEX insights, USD investment opportunities
SME Owners	Business owners, treasury management	Capital preservation, inflation protection
Beginner Retail	First-time investors, limited literacy	Simple explanations, educational guidance
Education Users	Students, universities, business schools	Simplified analysis, market visualization

1.4 Investment Coverage
•	Zimbabwe Stock Exchange (ZSE) — Delta, Econet, CBZ, Innscor, Hippo Valley, Simbisa
•	Victoria Falls Stock Exchange (VFEX) — Seed Co International, Caledonia Mining, Padenga
•	REITs — Tigere REIT, First Mutual REIT
•	Money market products, government bonds, treasury bills (future phases)
•	Alternative investments — gold-backed products, ETFs (long-term)

1.5 MVP Scope
Included in MVP	Excluded from MVP
ZSE equities explorer	Automated trading / broker execution
VFEX equities explorer	Payment systems / financial transactions
REIT intelligence hub	Advanced ML prediction models
Market dashboards + charts	Mobile applications (web-first)
Financial news aggregation	Social investing features
AI-generated summaries	Blockchain functionality
Sentiment analysis engine	Portfolio automation
Macroeconomic indicators	Multi-language support (Phase 1)
Educational content hub	Live brokerage integrations

1.6 Core Platform Principles
Principle	Statement	Implementation
Context-Aware	Raw numbers without economic context are insufficient	Every metric displayed with macro context
Explainability	Users must understand WHY recommendations exist	Score breakdowns on all outputs
Transparency	Explain data, factors, and uncertainty	Source attribution and confidence indicators
Education-First	Platform prioritizes understanding over speculation	Beginner layers on every complex feature
Data-Driven	Supports informed investing, not emotional investing	Analytics-driven recommendations, not hype

 
PART 2
Feature Specifications & UX Design

2.1 Application Structure
Area	Pages / Modules
Public	Landing page, About, Pricing, Market News preview, Login/Register
Authenticated	Dashboard, Asset Explorer (ZSE/VFEX/REIT), Asset Detail Pages, AI Assistant, Macro Dashboard, Alerts, Watchlists, Educational Hub

2.2 Design Language
Attribute	Dark Mode	Light Mode
Background Primary	#050816 (deep black)	#F8FAFC
Background Secondary	#0F172A (charcoal)	#FFFFFF
Card Background	#111827	#FFFFFF
Border	#1F2937	#E2E8F0
Primary Accent	Electric blue	Electric blue
Positive	Emerald green	Emerald green
Negative	Soft red	Soft red

•	Primary Font: Inter (fallback: SF Pro, Geist, system-ui)
•	Animation Library: Framer Motion — smooth, subtle, purposeful only
•	Charts: Recharts (primary), Chart.js (secondary), D3.js (advanced future)
•	Component System: shadcn/ui + custom fintech components
•	Responsive: Mobile (<640px), Tablet (640–1024px), Desktop (1024px+), Ultra-wide (1600px+)

2.3 Main Dashboard Specification
Section	Content	Purpose
Market Overview	ZSE/VFEX performance, inflation, exchange rates, top movers	Immediate market pulse
AI Insights Feed	AI-generated summaries of market conditions and sector movements	Contextual intelligence
Watchlist Overview	User-tracked assets with sentiment and AI updates	Personalized monitoring
Investment Opportunities	Personalized recommendations by risk profile	Actionable guidance
Market News Feed	Aggregated financial news, analyst commentary	Real-time intelligence

2.4 Asset Detail Page Specification
•	Header: company name, ticker, current price, daily change, sentiment badge, risk level
•	Interactive price chart with inflation-adjusted overlays and dividend markers
•	AI Summary Card — plain-language analysis with uncertainty acknowledgment
•	Sentiment Intelligence — positive/negative %, institutional outlook, news trend
•	Key Metrics grid — market cap, dividend yield, volatility, liquidity, momentum score
•	News & Research aggregation — broker commentary, journalism, company announcements
•	Macroeconomic Exposure — inflation sensitivity, currency exposure, sector risk
•	Comparison Suggestions — similar assets, competitor comparisons
•	Educational Layer — explains metrics for beginner users

2.5 AI Assistant Specification
AI Assistant Role
The AI assistant is an intelligent research analyst, investment educator, and financial interpreter. It explains, summarizes, and contextualizes. It is NOT a hype chatbot, speculative trading guru, or prediction machine. Every response must cite data sources and acknowledge uncertainty.

Example supported queries:
•	"What are the best REITs for passive income?"
•	"Compare VFEX mining stocks"
•	"How does inflation affect banking stocks?"
•	"Which sectors benefit from USD strength?"
•	"Explain dividend yield in simple terms"

2.6 Onboarding Flow
Step	Screen	Options
1	Risk Tolerance	Conservative / Moderate / Aggressive
2	Investment Interests	ZSE stocks / VFEX / REITs / Passive income / Growth / Dividends
3	Financial Goals	Wealth building / Passive income / Inflation protection / USD exposure
4	Experience Level	Beginner / Intermediate / Advanced

 
PART 3
Technical Architecture & Stack

3.1 Architecture Overview
Architecture Principle
Modular, service-oriented architecture. Responsibilities separated into distinct layers — no tightly coupled systems. MVP uses modular monolith; microservices at scale. Build layer-by-layer: Data → Analytics → APIs → Frontend → AI.

Layer	Responsibility	Key Technologies
Frontend	UI, dashboards, charts, AI chat	Next.js, TailwindCSS, shadcn/ui, Recharts
Backend API	Business logic, analytics, auth, AI orchestration	FastAPI, Python, JWT, Pydantic
Data Intelligence	Scraping, macro ingestion, sentiment	BeautifulSoup, Playwright, Pandas
Analytics Engine	Scoring, rankings, volatility, macro adjustments	Python, NumPy, Pandas
AI Interpretation	Summarization, recommendations, conversational AI	OpenAI API, RAG, custom orchestration
Data Storage	Persistent storage, caching, historical data	PostgreSQL, Redis, S3/R2
Infrastructure	Deployment, monitoring, scheduling, CI/CD	Docker, GitHub Actions, Sentry

3.2 Full Technology Stack
Frontend
Technology	Purpose	Why	Target Version
Next.js (App Router)	Framework	SSR, performance, routing	Latest stable
TypeScript	Type safety	Prevents runtime errors	5.x
TailwindCSS	Styling	Utility-first, dark mode	3.x
shadcn/ui	Components	Accessible, Radix-based	Latest
Recharts	Primary charts	React-native charts	Latest
Chart.js	Secondary charts	Complex visualizations	Latest
D3.js	Advanced viz	Custom analytics charts	Latest
Zustand	State	Lightweight state management	Latest
TanStack Query	Data fetching	Server state, caching	v5
Framer Motion	Animations	Premium fintech motion	Latest
Zod	Validation	Type-safe schema validation	Latest

Backend
Technology	Purpose	Why	Target Version
FastAPI	API framework	Async, fast, Python ecosystem	Latest
SQLAlchemy	ORM	Powerful, migration-friendly	2.x
Alembic	DB migrations	Schema version control	Latest
Pydantic v2	Validation	Type-safe schemas	v2
python-jose	JWT	Secure auth tokens	Latest
passlib + bcrypt	Password hashing	Industry standard security	Latest
APScheduler	Job scheduling (MVP)	Simpler than Celery	Latest
Celery	Jobs (future)	Distributed tasks	Latest
BeautifulSoup	HTML scraping	Structured parsing	4.x
Playwright	Dynamic scraping	JS-rendered content	Latest
Pandas + NumPy	Data processing	Analytics	Latest
pdfplumber/PyMuPDF	PDF extraction	Financial reports	Latest

Infrastructure
Technology	Purpose	Provider	Notes
PostgreSQL	Primary DB	Supabase / Neon	All structured data
Redis	Cache	Upstash	AI, API, session caching
Vercel	Frontend hosting	Vercel	Next.js optimized
Railway / Render	Backend hosting	Railway preferred	FastAPI container
Cloudflare R2	File storage	Cloudflare	PDFs, reports, logos
Docker	Containers	Local + production	All services
GitHub Actions	CI/CD	GitHub	Automated pipelines
Sentry	Error tracking	Sentry.io	Frontend + backend
PostHog	Analytics	PostHog	User behavior
Better Stack	Uptime	Better Stack	API health monitoring

 
PART 4
Repository & Folder Structure

⚠ IMPORTANT FOR AI AGENT
AI AGENTS MUST FOLLOW THESE FOLDER STRUCTURES EXACTLY. Never create files outside these paths. Never merge modules that should be separate. Never create monolithic files. All code must follow the modular structure below.

4.1 Monorepo Root
/investguide
    /frontend          ← Next.js App Router application
    /backend           ← FastAPI Python application
    /ai-services       ← AI/RAG orchestration layer
    /scrapers          ← Data ingestion pipeline
    /shared            ← Shared TypeScript types / utilities
    /docs              ← Architecture and API documentation
    /infrastructure    ← Docker, CI/CD, deployment configs

4.2 Frontend Structure
/frontend
    /app                        ← Next.js App Router pages
      /dashboard
      /markets
      /assets/[ticker]
      /ai-assistant
      /news
      /education
      /macro
      /watchlists
      /alerts
      /auth/login
      /auth/register
    /components                 ← Reusable UI components only
      /ui                       ← shadcn/ui components
      /charts                   ← Chart wrapper components
      /layout                   ← AppShell, Sidebar, Navbar
      /common                   ← Shared components
    /features                   ← Feature-based business logic
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
    /hooks                      ← Custom React hooks
    /services                   ← API client functions
    /store                      ← Zustand state stores
    /types                      ← TypeScript type definitions
    /utils                      ← Helper functions
    /styles                     ← Global CSS

4.3 Backend Structure
/backend
    /api                        ← FastAPI route definitions
      /v1
        /auth.py
        /assets.py
        /news.py
        /sentiment.py
        /analytics.py
        /macro.py
        /ai.py
        /watchlists.py
        /alerts.py
        /search.py
    /services                   ← Business logic (one file per domain)
      /auth_service.py
      /asset_service.py
      /news_service.py
      /sentiment_service.py
      /analytics_service.py
      /macro_service.py
      /ai_service.py
    /analytics                  ← Analytics engine modules
      /performance.py
      /risk.py
      /dividends.py
      /momentum.py
      /recommendation.py
      /macro_adjustment.py
    /models                     ← SQLAlchemy ORM models
      /user.py
      /asset.py
      /price.py
      /dividend.py
      /news_article.py
      /sentiment.py
      /macro_indicator.py
      /ai_summary.py
      /watchlist.py
    /schemas                    ← Pydantic schemas
    /database                   ← DB connection and session
    /jobs                       ← Scheduled background jobs
    /core                       ← Auth, config, middleware, settings
    /utils                      ← Shared utilities
    /tests                      ← Pytest test suite

4.4 AI Services Structure
/ai-services
    /prompts                    ← System prompt templates
      /system_prompt.py
      /rag_prompt.py
      /summary_prompt.py
    /rag                        ← RAG pipeline components
      /retriever.py
      /context_builder.py
      /validator.py
    /embeddings                 ← Embedding generation
      /generator.py
    /summaries                  ← AI summary generators
      /asset_summary.py
      /market_summary.py
      /macro_summary.py
    /agents                     ← AI orchestration

4.5 Scrapers Structure
/scrapers
    /base_scraper.py            ← Abstract base scraper class
    /zse
      /market_scraper.py
      /announcements_scraper.py
    /vfex
      /market_scraper.py
    /rbz
      /macro_scraper.py
    /zimstat
      /indicators_scraper.py
    /news
      /financial_gazette.py
      /newsday_business.py
      /herald_business.py
    /research
      /ih_securities.py
      /mmc_capital.py
    /pipeline
      /normalizer.py
      /deduplicator.py
      /pdf_extractor.py

 
PART 5
Database Architecture & Schemas

5.1 Core Entity Schemas
USERS
users
  id                    SERIAL PRIMARY KEY
  full_name             VARCHAR(255)
  email                 VARCHAR(255) UNIQUE NOT NULL
  password_hash         VARCHAR(255)
  auth_provider         VARCHAR(50)   -- email | google
  subscription_plan     VARCHAR(50)   -- free | premium
  risk_profile          VARCHAR(50)   -- conservative | moderate | aggressive
  experience_level      VARCHAR(50)   -- beginner | intermediate | advanced
  preferred_investments JSONB
  created_at            TIMESTAMP DEFAULT NOW()
  updated_at            TIMESTAMP DEFAULT NOW()

ASSETS
assets
  id                    SERIAL PRIMARY KEY
  ticker                VARCHAR(20) UNIQUE NOT NULL
  company_name          VARCHAR(255) NOT NULL
  exchange              VARCHAR(20)   -- ZSE | VFEX
  sector                VARCHAR(100)
  industry              VARCHAR(100)
  asset_type            VARCHAR(50)   -- equity | REIT | bond
  currency              VARCHAR(10)   -- ZWG | USD
  description           TEXT
  logo_url              VARCHAR(500)
  official_website      VARCHAR(500)
  market_cap            NUMERIC(20, 2)
  listing_date          DATE
  status                VARCHAR(20)   -- active | suspended
  created_at            TIMESTAMP DEFAULT NOW()
  INDEX: ticker, exchange, sector, asset_type

HISTORICAL_PRICES
historical_prices
  id                    SERIAL PRIMARY KEY
  asset_id              INTEGER REFERENCES assets(id)
  date                  DATE NOT NULL
  open_price            NUMERIC(15, 4)
  high_price            NUMERIC(15, 4)
  low_price             NUMERIC(15, 4)
  close_price           NUMERIC(15, 4)
  adjusted_close        NUMERIC(15, 4)
  volume                BIGINT
  currency              VARCHAR(10)
  created_at            TIMESTAMP DEFAULT NOW()
  UNIQUE: (asset_id, date)
  INDEX: (asset_id, date DESC)     ← critical for time-series queries

NEWS_ARTICLES
news_articles
  id                    SERIAL PRIMARY KEY
  source_name           VARCHAR(255)
  source_url            VARCHAR(1000)
  article_title         VARCHAR(500)
  article_content       TEXT
  summary               TEXT
  publication_date      TIMESTAMP
  author                VARCHAR(255)
  category              VARCHAR(100)  -- markets | macro | company | research
  sentiment_status      VARCHAR(50)   -- pending | processed
  content_hash          VARCHAR(64)   ← for deduplication
  created_at            TIMESTAMP DEFAULT NOW()
  INDEX: publication_date, sentiment_status, content_hash

SENTIMENT_ANALYSIS
sentiment_analysis
  id                    SERIAL PRIMARY KEY
  article_id            INTEGER REFERENCES news_articles(id)
  asset_id              INTEGER REFERENCES assets(id)
  sentiment_score       NUMERIC(4, 3)  -- -1.000 to +1.000
  sentiment_label       VARCHAR(20)    -- positive | neutral | negative
  confidence_score      NUMERIC(4, 3)  -- 0.000 to 1.000
  model_used            VARCHAR(100)   -- VADER | TextBlob | FinBERT
  processed_at          TIMESTAMP DEFAULT NOW()

MACROECONOMIC_INDICATORS
macroeconomic_indicators
  id                    SERIAL PRIMARY KEY
  indicator_name        VARCHAR(100)  -- inflation | exchange_rate | interest_rate | gold_price
  indicator_value       NUMERIC(15, 4)
  indicator_unit        VARCHAR(50)   -- % | rate | index | USD
  source                VARCHAR(100)  -- RBZ | ZIMSTAT
  reporting_date        DATE
  category              VARCHAR(100)  -- monetary | fiscal | commodity
  created_at            TIMESTAMP DEFAULT NOW()
  INDEX: (indicator_name, reporting_date DESC)

AI_SUMMARIES
ai_summaries
  id                    SERIAL PRIMARY KEY
  asset_id              INTEGER REFERENCES assets(id)
  summary_type          VARCHAR(50)   -- company | market | sector | macro
  summary_content       TEXT
  model_used            VARCHAR(100)
  generated_at          TIMESTAMP DEFAULT NOW()
  expiration_time       TIMESTAMP     ← TTL: 6 hours default
  INDEX: (asset_id, summary_type, expiration_time)

WATCHLISTS & ALERTS
watchlists
  id                    SERIAL PRIMARY KEY
  user_id               INTEGER REFERENCES users(id)
  asset_id              INTEGER REFERENCES assets(id)
  created_at            TIMESTAMP DEFAULT NOW()
  UNIQUE: (user_id, asset_id)
 
alerts
  id                    SERIAL PRIMARY KEY
  user_id               INTEGER REFERENCES users(id)
  asset_id              INTEGER REFERENCES assets(id)
  alert_type            VARCHAR(50)   -- price_change | sentiment | dividend | macro
  threshold             NUMERIC(10, 2)
  is_active             BOOLEAN DEFAULT TRUE
  triggered_at          TIMESTAMP
  created_at            TIMESTAMP DEFAULT NOW()

5.2 Key Relationships
Relationship	Type	Notes
users → watchlists	One-to-many	Users track multiple assets
assets → historical_prices	One-to-many	Full OHLCV price history
assets → dividends	One-to-many	Dividend payment history
assets ↔ news_articles	Many-to-many (article_asset_relationships junction)	Articles linked to multiple assets
news_articles → sentiment_analysis	One-to-many	Multiple model scores per article
assets → ai_summaries	One-to-many	Multiple summary types cached per asset

5.3 Redis Cache Key Strategy
asset:{ticker}:summary          TTL: 6 hours   → AI summary
asset:{ticker}:prices            TTL: 1 hour    → Recent OHLCV data
asset:{ticker}:sentiment         TTL: 2 hours   → Sentiment aggregate
asset:{ticker}:analytics         TTL: 3 hours   → Analytics scores
macro:overview                   TTL: 1 hour    → Macro snapshot
news:latest                      TTL: 15 min    → News feed
recommendations:{risk_profile}   TTL: 3 hours   → Recommendation sets

 
PART 6
API Contracts & Communication Architecture

6.1 Global Response Envelope
// All endpoints return this consistent structure
 
// SUCCESS
{
  "success": true,
  "message": "Assets retrieved successfully",
  "data": { ... },
  "meta": { "page": 1, "limit": 20, "total": 200, "has_next": true }
}
 
// ERROR
{
  "success": false,
  "message": "Invalid ticker symbol",
  "error_code": "INVALID_TICKER",
  "details": { ... }
}

6.2 Complete Endpoint Reference
Module	Method	Endpoint	Auth Required
Auth	POST	/api/v1/auth/register	No
Auth	POST	/api/v1/auth/login	No
Auth	POST	/api/v1/auth/refresh	No
Users	GET	/api/v1/users/me	Yes
Users	PATCH	/api/v1/users/preferences	Yes
Assets	GET	/api/v1/assets	No
Assets	GET	/api/v1/assets/{ticker}	No
Assets	GET	/api/v1/assets/{ticker}/prices	No
Assets	GET	/api/v1/assets/{ticker}/dividends	No
Assets	GET	/api/v1/assets/{ticker}/sentiment	No
Assets	GET	/api/v1/assets/{ticker}/analytics	No
Assets	GET	/api/v1/assets/{ticker}/ai-summary	Yes
Assets	GET	/api/v1/assets/{ticker}/news	No
News	GET	/api/v1/news	No
Research	GET	/api/v1/research/reports	No
Sentiment	GET	/api/v1/sentiment/trends	No
Analytics	GET	/api/v1/recommendations	Yes
Macro	GET	/api/v1/macro/overview	No
Macro	GET	/api/v1/macro/inflation	No
AI	POST	/api/v1/ai/chat	Yes
Watchlists	GET	/api/v1/watchlists	Yes
Watchlists	POST	/api/v1/watchlists	Yes
Watchlists	DELETE	/api/v1/watchlists/{id}	Yes
Alerts	GET	/api/v1/alerts	Yes
Alerts	POST	/api/v1/alerts	Yes
Alerts	DELETE	/api/v1/alerts/{id}	Yes
Search	GET	/api/v1/search?q={query}	No

6.3 Key Request/Response Examples
POST /api/v1/auth/login
// Request
{ "email": "user@example.com", "password": "securePassword" }
 
// Response
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiJ9...",
    "user": { "id": 1, "full_name": "Spencer Jaka", "risk_profile": "moderate" }
  }
}

GET /api/v1/assets/{ticker}/analytics
// Response
{
  "success": true,
  "data": {
    "volatility": 0.22,
    "dividend_consistency": 0.85,
    "momentum_score": 0.78,
    "risk_level": "Moderate",
    "recommendation_score": 82,
    "score_breakdown": {
      "performance": 78,
      "risk": 85,
      "sentiment": 80,
      "macro_adjustment": 75,
      "dividend_stability": 90
    },
    "explanation": "Strong dividend consistency and moderate volatility..."
  }
}

POST /api/v1/ai/chat
// Request
{
  "message": "What are good REITs for passive income?",
  "conversation_id": "uuid-string"
}
 
// Response (streaming)
{
  "success": true,
  "data": {
    "response": "Tigere REIT currently demonstrates strong dividend...",
    "sources_used": ["market_data", "sentiment_analysis", "institutional_research"],
    "confidence": "moderate",
    "disclaimer": "This is educational analysis, not financial advice."
  }
}

6.4 Rate Limiting Strategy
Endpoint Category	Rate Limit
AI assistant endpoints	20 requests/minute per user
Search endpoints	60 requests/minute per user
Market data endpoints	120 requests/minute per user
Authentication endpoints	10 attempts/minute per IP
General API endpoints	200 requests/minute per user

 
PART 7
Analytics Engine & AI Architecture

7.1 Analytics Engine
Recommendation Scoring Formula
Final Score (0–100) =
  (Performance Score  × 0.25)   ← CAGR, rolling returns, drawdown
+ (Risk Score         × 0.20)   ← Volatility, liquidity, downside
+ (Sentiment Score    × 0.20)   ← News + institutional + market momentum
+ (Macro Adjustment   × 0.15)   ← Inflation, exchange rate, interest rate
+ (Dividend Stability × 0.20)   ← Consistency, growth, sustainability
 
Thresholds:
  Strong Opportunity: Score > 75
  Moderate Opportunity: Score 50–75
  Caution Required: Score < 50

Key Analytics Formulas
CAGR = ((End Value / Begin Value) ^ (1 / Years)) - 1
Annualized Volatility = Daily_StdDev × sqrt(252)
Risk Levels: Low (<15%) | Moderate (15-30%) | High (30-50%) | Speculative (>50%)
 
Sentiment Score Range: -1.0 (Extremely Negative) → +1.0 (Extremely Positive)
Sentiment Aggregate = (Article × 0.40) + (Institutional × 0.35) + (Momentum × 0.25)
 
Macro Adjustments:
  High Inflation (>30%) → Increase VFEX/USD asset weighting
  Rising Gold Prices    → Increase mining sector scores
  Currency Instability  → Increase USD-denominated preference

7.2 RAG Pipeline Architecture
User Question
        ↓
Context Retrieval (vector search on embeddings)
        ↓
Documents Ranked by: recency × relevance × source trust
        ↓
Analytics Injection (live scores, metrics, macro snapshot)
        ↓
Prompt Construction:
  [System Instructions]
  [Retrieved Context]
  [Analytics Data]
  [Macroeconomic Context]
  [User Question]
        ↓
LLM Generation (OpenAI / Ollama local)
        ↓
Validation Layer:
  - Ticker verification (cross-ref assets table)
  - Metric range check (realistic bounds)
  - Certainty language detection
  - Source grounding requirement
        ↓
Frontend Response (streaming text)

7.3 Master AI System Prompt
You are InvestGuide AI, an AI-powered Zimbabwean investment intelligence assistant.
 
YOUR ROLE:
- Explain investment concepts clearly and accessibly
- Summarize financial intelligence using retrieved context only
- Contextualize macroeconomic conditions and their investment implications
- Provide balanced, educational investment insights
- Simplify financial analysis for all experience levels
 
YOU ARE NOT:
- A guaranteed prediction engine
- A speculative trading advisor
- A financial advisor promising returns
 
ALWAYS:
- Explain your reasoning transparently
- Acknowledge uncertainty when data is incomplete or conflicting
- Reference supporting analytics and sentiment data
- Use phrases like "data suggests", "sentiment indicates", "historically"
- Avoid definitive profit or loss claims
- Include: "This is educational analysis, not financial advice."
 
DATA AVAILABLE TO YOU:
- Quantitative analytics scores and breakdowns
- Sentiment analysis (news + institutional)
- Macroeconomic indicators (inflation, exchange rates, rates)
- Retrieved financial documents and research
- Company metadata and historical performance

7.4 AI Model Strategy
Stage	Model	Notes
Development (local)	Qwen / DeepSeek / Gemma via Ollama	Free, fast iteration, no API costs
MVP Production	OpenAI GPT-4o-mini / Claude Haiku	Cost-efficient production API
Premium Features	OpenAI GPT-4o / Claude Sonnet	Higher capability for premium tier
Embeddings	BGE / E5 / Nomic	Via Ollama locally or API
Sentiment (future)	FinBERT fine-tuned	Financial domain-specific NLP

 
PART 8
Data Ingestion & Scraping Pipeline

8.1 Scraping Pipeline Flow
Scheduler Trigger (APScheduler job)
        ↓
Source Fetch (requests / Playwright for JS-rendered pages)
        ↓
HTML / PDF Parsing (BeautifulSoup / pdfplumber / PyMuPDF)
        ↓
Content Extraction (source-specific parsers — isolated per source)
        ↓
Normalization:
  - Ticker symbols standardized
  - Dates standardized to ISO format
  - Currencies unified (ZWG / USD)
  - Company names normalized
  - HTML cleaned and stripped
        ↓
Deduplication:
  - Title similarity hash (content_hash field)
  - Semantic similarity check
  - Publication timestamp comparison
        ↓
Sentiment Processing (VADER → FinBERT pipeline)
        ↓
Embedding Generation (for RAG retrieval)
        ↓
Database Storage (PostgreSQL)
        ↓
AI Summary Generation (queued, cached to ai_summaries table)

8.2 Data Sources & Frequencies
Tier	Source	Data Type	Frequency
Tier 1 — Official	ZSE	Market prices, volumes	Daily post-market
Tier 1 — Official	VFEX	USD market data	Daily post-market
Tier 1 — Official	RBZ	Inflation, exchange rates, policy	Daily
Tier 1 — Official	ZIMSTAT	GDP, economic indicators	Weekly
Tier 2 — Institutional	IH Securities	Research reports, analyst notes	As published
Tier 2 — Institutional	MMC Capital	Market research, reports	As published
Tier 2 — Institutional	Old Mutual Zimbabwe	Investment research	As published
Tier 3 — Journalism	Financial Gazette	News articles	Every 15–30 min
Tier 3 — Journalism	NewsDay Business	News articles	Every 15–30 min
Tier 3 — Journalism	Herald Business	News articles	Every 15–30 min

8.3 Scheduled Job Frequencies
Background Job	Schedule
ZSE/VFEX market data ingestion	Daily — 30 min after market close
Financial news scraping (all sources)	Every 15 minutes
RBZ macroeconomic data	Daily at 08:00
ZIMSTAT economic indicators	Weekly on Monday at 06:00
AI summary regeneration	Every 6 hours
Sentiment recalculation on new articles	Every 2 hours
Recommendation engine recalculation	Every 3 hours
Redis cache warm-up (top assets)	Every hour

 
PART 9
Development Roadmap & Build Order

⚠ IMPORTANT FOR AI AGENT
CRITICAL BUILD ORDER: Build layer-by-layer, NOT feature-by-feature. Data infrastructure MUST precede analytics. Analytics MUST precede AI. Dashboards are built on real data and real APIs — never before them.

9.1 Priority Order
Priority	Layer
1 — First	Data infrastructure (DB, models, ingestion)
2 — Second	Analytics systems (scoring, calculations)
3 — Third	Backend APIs (endpoints, schemas, auth)
4 — Fourth	Frontend dashboards (built on real APIs)
5 — Fifth	AI orchestration (after analytics proven)
6 — Sixth	Advanced features (personalization, alerts, premium)

9.2 Phase-by-Phase Delivery Plan
Phase	Focus	Key Deliverables	Success Criteria
Phase 1	Foundation	FastAPI + PostgreSQL + JWT auth + Next.js setup + Docker + CI/CD	Frontend + backend deployed, DB connected, auth working
Phase 2	Market Data	Asset DB seed, historical prices, market APIs, dashboard skeleton, basic charts	Live data displayed, search works, charts render
Phase 3	News Pipeline	All scrapers built, normalization, deduplication, article-asset links, news dashboard	News auto-ingested, no duplicates, linked to assets
Phase 4	Analytics	Risk scoring, CAGR, volatility, dividend analysis, recommendation engine	Analytics on asset pages, recommendation rankings live
Phase 5	AI Systems	Sentiment pipeline, AI assistant, RAG, streaming responses, AI summaries	AI assistant answers questions with grounded responses
Phase 6	Personalization	Watchlists, alerts, onboarding, preference-aware dashboards	Personalized experience fully operational
Phase 7	Premium	Subscription system, premium gating, advanced features, broker integrations	Revenue model activated

9.3 Sprint Structure
Recommended sprint duration: 1–2 weeks per sprint.
Sprint Stage	Activity	Output
Planning	Define feature, write architecture notes, create prompt specs	Clear feature specification
AI-Agent Prompting	Generate module with constrained, scoped prompts	Generated code scaffold
Human Review	Review architecture consistency, modularity, typing	Reviewed and corrected code
Refactoring	Clean up generated code, enforce conventions	Production-quality module
Testing	Write and run Pytest/Playwright tests	Tested, passing module
Deployment	Commit, push, CI/CD pipeline runs	Deployed to staging/production

 
PART 10
AI-Agent Prompt Library & Engineering Rules

10.1 Golden Rules for AI-Agent Development
RULE
NEVER prompt: "Build this however you want." ALWAYS enforce: folder structure, naming conventions, typing, modularity, and architecture boundaries.

RULE
NEVER generate huge systems in one prompt. ALWAYS define isolated modules with clear interfaces, expected outputs, and constraints.

RULE
ALWAYS review ALL generated code manually before committing. AI agents amplify good architecture and magnify bad architecture.

10.2 Master Context Prompt (Use at Start of Every Session)
You are building InvestGuide, an AI-powered Zimbabwean investment
intelligence platform focused on: Zimbabwe Stock Exchange (ZSE),
Victoria Falls Stock Exchange (VFEX), REITs, macroeconomic intelligence,
financial analytics, and AI-powered investment explanations.
 
TECH STACK:
Frontend: Next.js App Router, TypeScript, TailwindCSS, shadcn/ui,
          Zustand, TanStack Query, Framer Motion, Recharts
Backend:  FastAPI, Python, PostgreSQL, SQLAlchemy, Alembic, Redis,
          Pydantic v2, JWT (python-jose), passlib+bcrypt
 
ARCHITECTURE: Modular monolith (MVP). Feature-based frontend organization.
Service-oriented backend modules.
 
FOLDER STRUCTURE RULES:
- Backend: /api /services /analytics /models /schemas /database /jobs /core /utils /tests
- Frontend: /app /components /features /hooks /services /store /types /utils
- Scrapers: /zse /vfex /rbz /zimstat /news /research /pipeline
- AI: /prompts /rag /embeddings /summaries /agents
 
ENGINEERING PRINCIPLES:
- Type safety throughout (TypeScript + Pydantic)
- Modular, clean architecture — no monolithic files
- Production-grade patterns only
- Responsive design with dark/light mode support
- Analytics drive intelligence; AI explains it — never fabricates
- Avoid hardcoded logic; use config and reusable components
 
CRITICAL RULES:
- Never create files outside the defined folder structure
- Never merge modules that should be separate
- Always use the global API response envelope
- All authenticated endpoints require JWT middleware
- All AI responses must include source grounding and disclaimers

10.3 Module Prompt Template
OBJECTIVE:
  [What this specific module does]
 
CONTEXT:
  [How it fits into InvestGuide's architecture — which layer, which service]
 
REQUIREMENTS:
  - [Specific functional requirement 1]
  - [Specific functional requirement 2]
  - [Specific functional requirement 3]
 
TECHNICAL CONSTRAINTS:
  - Follow InvestGuide modular monolith backend architecture
  - Output files must go in: [specific path]
  - Use SQLAlchemy ORM (not raw SQL)
  - Use Pydantic v2 schemas for all request/response models
  - Use async/await throughout
  - Include structured logging
  - Include retry handling where appropriate
 
EXPECTED OUTPUT:
  - [file1.py] — [what it contains]
  - [file2.py] — [what it contains]
  - [test_file.py] — [test coverage]
 
VALIDATION:
  - All endpoints must return the global response envelope
  - Tests must cover happy path + error cases
  - No hardcoded values — use config/env variables

10.4 Key Prompt Templates
FastAPI Backend Module
Build a [module name] service for InvestGuide.
 
Requirements:
- async FastAPI routes
- SQLAlchemy ORM with PostgreSQL
- Pydantic v2 schemas for request/response
- Redis caching for [specific endpoints]
- JWT authentication middleware on protected routes
- Structured logging with context
- Retry handling on external calls
 
Output:
- /backend/api/v1/[module].py         (routes)
- /backend/services/[module]_service.py (business logic)
- /backend/models/[model].py           (SQLAlchemy model)
- /backend/schemas/[module].py         (Pydantic schemas)
- /backend/tests/test_[module].py      (Pytest tests)
 
Constraints:
- Follow InvestGuide folder structure exactly
- Use global response envelope on all endpoints
- No raw SQL — SQLAlchemy ORM only
- Type-safe throughout

Next.js Frontend Feature
Build a [feature name] page/component for InvestGuide.
 
Tech Stack:
- Next.js App Router with TypeScript
- TailwindCSS for styling
- shadcn/ui components
- Recharts for data visualization
- Framer Motion for animations
- TanStack Query for data fetching
 
Design Requirements:
- Dark mode primary (deep blacks, charcoal, electric blue accents)
- Light mode (clean whites, minimal)
- Mobile-responsive (mobile-first)
- Premium fintech aesthetics — Bloomberg-inspired
- Loading states with skeleton loaders
- Empty states with helpful guidance
 
Output:
- /frontend/app/[path]/page.tsx         (page component)
- /frontend/features/[feature]/         (feature module)
- /frontend/components/[component].tsx  (reusable components)
 
Constraints:
- No inline styles — TailwindCSS classes only
- All components must be typed with TypeScript
- Reusable components only — no duplicated UI logic
- Dark/light mode must work via Tailwind dark: prefix

Scraper Module
Build a [source name] scraper for InvestGuide.
 
Requirements:
- Extends BaseScaper class from /scrapers/base_scraper.py
- Source-specific parsing logic
- Retry handling on network failures
- Deduplication via content_hash
- Normalization of: company names, tickers, dates, currencies
- Article-to-asset linking
 
Output:
- /scrapers/[category]/[source_name].py  (scraper)
- /scrapers/pipeline/normalizer.py update (if needed)
- Test fixtures for parsing validation
 
Constraints:
- Respect robots.txt
- Max request frequency: 1 request per 2 seconds per domain
- Use Playwright only if JS rendering is required
- Use BeautifulSoup for static HTML

10.5 Debugging & Refactoring Prompts
Refactoring Prompt
Refactor this InvestGuide module according to engineering standards.
 
Requirements:
- Improve modularity (break up any files >300 lines)
- Reduce code duplication
- Improve TypeScript/Pydantic type safety
- Separate business logic from presentation
- Maintain all existing functionality
 
Do NOT:
- Change the folder structure
- Introduce breaking API changes
- Remove features
 
Provide:
- Explanation of what was improved and why
- Updated code following InvestGuide conventions

Bug Fix Prompt
Debug and fix this InvestGuide issue.
 
Requirements:
- Identify the root cause clearly
- Implement the minimal safe fix
- Preserve architecture consistency
- Avoid introducing regressions
 
Also provide:
- Preventative improvements
- Test case to prevent regression

 
PART 11
Security, Compliance & Trust Architecture

11.1 Legal Positioning
Platform Classification
InvestGuide is an AI-powered investment intelligence and education platform. It is NOT a licensed broker, automated investment advisor, portfolio manager, or guaranteed-return service. This classification must be maintained in all user-facing copy, AI responses, and marketing.

Avoid	Use Instead
"Guaranteed returns"	"May suit income-focused investors"
"Best stock to buy now"	"Data suggests strong momentum"
"You will profit"	"Historically resilient to macro pressure"
"AI predicts markets"	"Market sentiment indicates"
"Safe investment"	"Based on available information"

11.2 Standard Disclaimers
// Display on all recommendation areas:
"InvestGuide provides educational investment intelligence and analytics.
This platform does not provide licensed financial advice.
Always conduct independent research before investing."
 
// AI assistant response footer:
"This is educational analysis, not financial advice.
Data based on: [sources used]. Always verify with independent research."

11.3 Security Requirements
Security Layer	Implementation	Scope
JWT Authentication	python-jose, RS256, refresh token rotation	All authenticated endpoints
Password Security	bcrypt hashing, min 8 chars, complexity required	Registration and password change
Rate Limiting	Redis-backed, per-user counters	All endpoints (see limits above)
Input Validation	Pydantic v2 strict mode, Zod on frontend	All request bodies
CORS	Whitelist only known frontend origins	All API endpoints
AI Prompt Safety	Input sanitization, injection prevention	AI chat endpoint
Secrets Management	Environment variables, no hardcoded keys	All services
Feature Gating	Server-side subscription check middleware	Premium endpoints

11.4 Source Trust Hierarchy
Tier	Sources	Usage
Tier 1 — Official	ZSE, VFEX, RBZ, ZIMSTAT	Highest trust — cited as authoritative
Tier 2 — Institutional	IH Securities, MMC Capital, Old Mutual	High trust — cited with attribution
Tier 3 — Journalism	Financial Gazette, NewsDay Business	Moderate — summarized with care
Tier 4 — General	Community sources, general publications	Low — marked clearly, used cautiously

11.5 AI Safety Rules
•	Never allow AI to guarantee profits or promise specific returns
•	Never allow AI to fabricate financial data, analyst opinions, or price targets
•	Always require source grounding — AI must only reference retrieved context
•	Require confidence indicators on all AI-generated outputs
•	Validate all ticker symbols against the assets table before including in responses
•	Include disclaimer on every AI assistant response

 
PART 12
Final Engineering Principles & Quick Reference

12.1 Absolute Engineering Principles
Principle 1
Data quality matters more than AI sophistication. A platform with reliable data and no AI is more valuable than a platform with brilliant AI and unreliable data.

Principle 2
Analytics should drive intelligence. AI should explain it, never fabricate it. Every AI response must be grounded in retrieved, structured data.

Principle 3
Modular systems scale better than tightly coupled systems. AI agents amplify good architecture and magnify bad architecture.

Principle 4
Context-aware financial intelligence is the platform's core differentiator. Zimbabwe's macroeconomic environment requires specialized interpretation that generic platforms cannot provide.

Principle 5
Trust is the platform's greatest long-term asset. Explainability, transparency, and honesty compound faster than hype. Never compromise trust for engagement.

12.2 Quick Reference — Key Numbers & Thresholds
Parameter	Value
Recommendation Score: Strong	> 75 / 100
Recommendation Score: Moderate	50 – 75 / 100
Recommendation Score: Caution	< 50 / 100
Risk Level: Low Volatility	< 15% annualized
Risk Level: Moderate Volatility	15% – 30% annualized
Risk Level: High Volatility	30% – 50% annualized
Risk Level: Speculative	> 50% annualized
Sentiment: Strongly Positive	> 0.5
Sentiment: Positive	0.1 – 0.5
Sentiment: Neutral	-0.1 – 0.1
Sentiment: Negative	-0.5 – -0.1
Sentiment: Strongly Negative	< -0.5
AI Summary TTL (Redis)	6 hours
Price Data TTL (Redis)	1 hour
News Feed TTL (Redis)	15 minutes
AI Chat Rate Limit	20 requests/minute/user
Chunk Size for RAG Embeddings	500–1000 tokens

12.3 Pre-Production Checklist
Category	Checklist Item	Status
Infrastructure	Monitoring (Sentry) enabled	Before launch
Infrastructure	PostgreSQL backups configured	Before launch
Infrastructure	Redis persistence configured	Before launch
Infrastructure	CI/CD pipeline tested	Before launch
Security	JWT secrets rotated for production	Before launch
Security	All secrets in environment variables (no hardcodes)	Before launch
Security	Rate limiting tested and active	Before launch
Security	CORS whitelist set to production domains only	Before launch
AI Systems	Hallucination safeguards tested	Before launch
AI Systems	Source grounding verified on all responses	Before launch
AI Systems	Disclaimer present on all AI outputs	Before launch
Performance	Redis caching active on all cacheable endpoints	Before launch
Performance	Database indexes verified (ticker, date, sentiment)	Before launch
UX	Dark/light mode tested on all pages	Before launch
UX	Mobile responsiveness verified (<640px)	Before launch
Legal	Disclaimers visible on all recommendation areas	Before launch
Legal	Platform NOT positioned as financial advisor	Before launch

InvestGuide AI Agent Master Blueprint v1.0 — Confidential — Spencer Jaka — All 18 Sections Included

# Financial Statement Intelligence

Sprint 052 introduces deterministic Financial Statement Intelligence for InvestGuide.

## Purpose

Financial Statement Intelligence turns structured income statement, balance sheet, and cash flow records into explainable financial research sections. It helps users understand business performance without implying predictions, certainty, buy/sell advice, or personalized financial advice.

## Data Flow

```
Verified or development financial statements
        |
        v
Financial statement service
        |
        v
Financial Statement Intelligence Engine
        |
        v
Company APIs
        |
        v
Company page Financial Intelligence section
```

## Statements

The engine consumes:

* Income statements
* Balance sheets
* Cash flow statements

Each statement row supports company ownership, reporting period, fiscal year, currency, source metadata, provenance, verification status, timestamps, and development/live data flags.

## Engine Sections

The deterministic engine returns:

* Revenue analysis
* Profitability analysis
* Liquidity analysis
* Leverage analysis
* Cash flow analysis
* Earnings quality analysis

Each section includes:

* headline
* value
* trend
* explanation
* evidence
* confidence
* provenance
* why it matters
* Explain Like I'm 18
* Learn Next topics

## Provenance

Every response carries source transparency:

* source
* reporting period
* verification status
* last updated
* development-data flag
* confidence
* methodology version

Development data must be labelled as Development Preview. Production-facing records should come from verified imports or validated manual imports.

## APIs

* `GET /api/v1/companies/{ticker}/financial-statements`
* `GET /api/v1/companies/{ticker}/financial-intelligence`

The endpoints reuse existing company routing and response envelopes.

## Frontend

The company page renders a Financial Statement Intelligence panel using backend data. It shows cards for each deterministic section, source transparency, confidence, Learn Next topics, and the not-financial-advice boundary.

## Constraints

The engine does not implement:

* AI or LLM calls
* price predictions
* buy/sell recommendations
* personalized advice
* live source connectors
* portfolio optimization

## Future Roadmap

Future sprints may add verified import adapters, historical statement coverage, annual report parsing, statement restatement handling, richer benchmarking, and AI-assisted explanations that consume this deterministic output without replacing it.

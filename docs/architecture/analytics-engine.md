# Analytics Engine Architecture

Sprint 026 establishes the InvestGuide Analytics Engine Foundation. The analytics engine is the single source of truth for financial intelligence. Future frontend pages, AI systems, portfolio tools, comparison views, news intelligence, roadmaps, and recommendation modules must consume analytics from this centralized engine rather than calculating metrics independently.

This document describes architecture only. Sprint 026 does not implement real financial calculations.

## Purpose

The analytics engine exists to:

* centralize all metric and score calculation contracts
* standardize result shape, confidence, warnings, methodology, and versioning
* make future AI outputs grounded in structured analytics
* prevent duplicated calculations across modules
* preserve methodology transparency
* allow score changes to be versioned and tested

## Core Flow

```text
Asset / Context Data
        |
        v
AnalyticsContext
        |
        v
AnalyticsRegistry
        |
        v
AnalyticsEngine
        |
        v
AnalyticsResult[]
        |
        +--> Frontend
        +--> AI Intelligence Layer
        +--> Portfolio Intelligence
        +--> Comparison Engine
        +--> News Intelligence
        +--> Roadmaps
```

## Package Structure

```text
backend/app/analytics/
|-- __init__.py
|-- base.py
|-- confidence.py
|-- context.py
|-- dividend.py
|-- engine.py
|-- exceptions.py
|-- explanation.py
|-- growth.py
|-- liquidity.py
|-- macro.py
|-- quality.py
|-- registry.py
|-- result.py
|-- risk.py
|-- scores.py
|-- valuation.py
`-- version.py
```

## AnalyticsContext

`AnalyticsContext` is the input envelope for all analytics modules. It currently supports optional:

* asset
* historical prices
* news
* macro data
* financial statements
* user profile
* metadata

These fields are optional because the current repository does not yet implement all data sources. Future modules should enrich this context rather than invent parallel inputs.

## BaseAnalytics

Every analytics module must inherit from `BaseAnalytics` and implement:

* `calculate()`
* `validate()`
* `metadata()`
* `explanation()`
* `planned_inputs()`

Sprint 026 modules return purpose-only `AnalyticsResult` objects with warnings that real calculations are not implemented yet.

## AnalyticsResult

Every analytics result returns a standard object containing:

* `metric_name`
* `value`
* `confidence`
* `methodology`
* `inputs_used`
* `warnings`
* `timestamp`
* `version`

Future APIs and AI systems should consume this shape directly.

## Registry

`AnalyticsRegistry` owns metric registration. It supports:

* `register()`
* `unregister()`
* `calculate()`
* `calculate_all()`
* `metadata()`

Future modules should register analytics in one place, then consume them through the engine.

## Engine

`AnalyticsEngine` receives an `AnalyticsContext`, executes registered analytics, aggregates results, collects warnings, and returns structured output with engine and methodology versions.

## Current Score Modules

Sprint 026 establishes architecture for:

* Quality Score
* Growth Score
* Dividend Score
* Value Score
* Liquidity Score
* Risk Score
* Macro Score
* Confidence Score

Each module documents purpose, inputs, methodology, and future calculation notes. None performs real financial scoring yet.

## Explanation Layer

`AnalyticsExplanation` is deterministic and template-based. It is not AI. It gives future frontend and AI modules safe plain-language text to use before an LLM interprets analytics.

## Versioning

The package exposes:

* `ENGINE_VERSION`
* `METHODOLOGY_VERSION`

Future score changes must update methodology versioning and tests so downstream AI, dashboards, and reports can identify which methodology produced each result.

## Exceptions

Analytics exceptions include:

* `AnalyticsError`
* `MissingDataError`
* `ValidationError`
* `CalculationError`
* `UnknownMetricError`

These keep analytics failures explicit and separate from API, database, and AI failures.

## Future Roadmap

1. Add historical price data models and context builders.
2. Add real risk, volatility, liquidity, and return calculations.
3. Add dividend and REIT distribution analytics.
4. Add macro adjustment inputs from RBZ/ZIMSTAT sources.
5. Add confidence scoring based on data completeness and source trust.
6. Expose read-only analytics APIs for frontend consumption.
7. Feed analytics results into AI/RAG prompts.
8. Build comparison and portfolio intelligence on top of engine outputs.
9. Introduce an `AnalyticsPipeline` execution layer once analytics modules require dependency ordering, caching, parallel execution, timeout handling, partial failure management, execution metrics, or audit logging. This should keep `AnalyticsEngine` focused on orchestration while allowing execution mechanics to evolve independently.

## Non-Goals

Sprint 026 does not implement:

* PE calculations
* DCF
* dividend models
* portfolio analytics
* macro calculations
* recommendations
* predictions
* AI interpretation
* frontend charts
* comparison UI
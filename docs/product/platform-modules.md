# Platform Modules Roadmap

This document defines future InvestGuide modules. It is architecture only; it does not implement these modules.

## Investment Intelligence

Purpose: research ZSE, VFEX, REITs, bonds, money markets, and alternatives.

Primary users: retail investors, diaspora investors, income investors, advanced researchers.

Dependencies: assets, market data, analytics, news, macro context.

Current status: asset model and read-only asset API foundation exist.

Future roadmap: price history, asset pages, scores, comparisons, outlooks.

## Portfolio Intelligence

Purpose: track holdings, allocation, risk, income, and goal alignment.

Primary users: investors with holdings or watchlists.

Dependencies: auth, profiles, assets, prices, analytics.

Current status: not started.

Future roadmap: holdings model, allocation views, performance, risk, AI explanations.

## Budgeting

Purpose: help users understand cash flow and investment capacity.

Primary users: beginners, young professionals, households.

Dependencies: user profile, planning module, privacy controls.

Current status: not started.

Future roadmap: income/expense categories, budget health, AI education.

## Savings

Purpose: support emergency funds, goal savings, and habit formation.

Primary users: beginners, families, young professionals.

Dependencies: planning profile, financial health module.

Current status: not started.

Future roadmap: savings goals, progress tracking, education prompts.

## Debt

Purpose: help users understand debt burden and repayment tradeoffs.

Primary users: households, SME owners, planning users.

Dependencies: financial profile, risk education.

Current status: not started.

Future roadmap: debt inventory, repayment scenarios, affordability education.

## Retirement

Purpose: support long-horizon planning and compounding education.

Primary users: long-term investors and families.

Dependencies: goals, horizon, savings, portfolio, simulations.

Current status: not started.

Future roadmap: retirement roadmap, contribution scenarios, inflation-aware planning.

## Emergency Fund

Purpose: help users evaluate liquidity and resilience before investing.

Primary users: beginners, conservative investors, households.

Dependencies: savings and financial health inputs.

Current status: not started.

Future roadmap: emergency fund target ranges, readiness education.

## SME Intelligence

Purpose: help SME owners interpret cash preservation, macro risk, and business treasury choices.

Primary users: entrepreneurs and business owners.

Dependencies: macro data, money market/bond modules, education.

Current status: not started.

Future roadmap: SME cash planning, inflation protection, working-capital intelligence.

## News Intelligence

Purpose: aggregate, normalize, deduplicate, link, and explain investment news.

Primary users: all investors and researchers.

Dependencies: scraper pipeline, news model, asset linking, source trust.

Current status: news model/API, scraper foundation, dry-run and handoff flows exist.

Future roadmap: live ingestion, sentiment, summaries, source-grounded AI.

## Knowledge Base

Purpose: store trusted educational and research content for retrieval.

Primary users: AI assistant, learners, researchers.

Dependencies: content ingestion, tagging, embeddings, source trust.

Current status: not started.

Future roadmap: RAG corpus, document ingestion, citations.

## Learning Platform

Purpose: structured financial education and skill progression.

Primary users: beginners, students, intermediate learners.

Dependencies: personalization, education content, learning progress.

Current status: education pages exist only as frontend foundation.

Future roadmap: lessons, quizzes, adaptive paths, certificates.

## Financial Health

Purpose: summarize resilience, readiness, and financial gaps.

Primary users: planning users, beginners, households.

Dependencies: profile, savings, debt, emergency fund, portfolio.

Current status: not started.

Future roadmap: financial health score, explanations, improvement roadmap.

## Roadmaps

Purpose: create long-term step-by-step financial and learning plans.

Primary users: all authenticated users.

Dependencies: personalization, financial health, learning platform.

Current status: not started.

Future roadmap: AI-generated educational roadmaps and milestone tracking.

## Simulators

Purpose: explore hypothetical scenarios safely.

Primary users: learners, planners, advanced users.

Dependencies: analytics, historical data, assumptions engine.

Current status: not started.

Future roadmap: inflation, compounding, drawdown, dividend reinvestment, savings scenarios.

## Comparison Engine

Purpose: compare assets, products, strategies, and tradeoffs.

Primary users: investors researching alternatives.

Dependencies: assets, analytics, profiles, education.

Current status: not started.

Future roadmap: asset comparisons, REIT comparisons, ZSE/VFEX comparison, risk-income-growth views.

## Opportunity Radar

Purpose: surface research candidates and changing conditions.

Primary users: active researchers and premium users.

Dependencies: analytics, news, macro, profiles.

Current status: not started.

Future roadmap: watchlist signals, score changes, macro-triggered research prompts.
# InvestGuide AI Capabilities Roadmap

This document defines the future AI capabilities of InvestGuide. It is an architecture document only. No AI systems are implemented by this document.

AI must explain analytics, not replace them. AI must be grounded in source data, respect uncertainty, and preserve the educational-not-advisory boundary.

## AI Financial Assistant

Purpose: conversational research and education assistant for financial questions.

Inputs: user question, investor profile, asset data, macro context, news, analytics, education level.

Outputs: grounded explanations, comparisons, summaries, next research steps, educational links.

Safety: cite sources, avoid financial advice, reject profit guarantees, disclose uncertainty.

Future notes: should use RAG over trusted internal data and structured analytics outputs.

## AI News Intelligence

Purpose: summarize and contextualize financial news, announcements, analyst reports, and macro publications.

Inputs: normalized news articles, source trust tier, linked assets, publication date, content hash, macro tags.

Outputs: summaries, affected assets, key risks, confidence, source attribution, relevance explanations.

Safety: distinguish official facts from commentary, never fabricate events, show source trust.

Future notes: build after scraper ingestion and news storage are reliable.

## AI Portfolio Intelligence

Purpose: explain portfolio exposure, concentration, risk, income, and goal alignment.

Inputs: holdings, asset metadata, prices, dividends, risk metrics, user goals, horizon.

Outputs: portfolio summary, exposure breakdowns, educational warnings, diversification context.

Safety: avoid trade instructions; phrase as analysis and research prompts.

Future notes: requires portfolio model, price history, and analytics engine.

## AI Roadmaps

Purpose: generate financial learning and planning roadmaps.

Inputs: investor profile, goals, current knowledge, savings range, horizon, preferred asset types.

Outputs: step-by-step learning/research plans, milestones, suggested modules.

Safety: roadmaps are educational plans, not financial plans from a licensed advisor.

Future notes: should integrate with learning progress and financial health modules.

## AI Financial Health

Purpose: explain a user's financial readiness and resilience across savings, debt, emergency fund, investments, and goals.

Inputs: user-entered financial profile, goals, savings, debt, emergency fund, portfolio exposure.

Outputs: plain-language health explanation, strengths, gaps, education priorities.

Safety: avoid judgmental language and avoid exact advice; show assumptions and data gaps.

Future notes: requires user-controlled financial profile and privacy controls.

## AI Learning Engine

Purpose: adapt education to the user's experience level, mistakes, goals, and product behavior.

Inputs: profile, completed lessons, quiz results, viewed assets, AI questions, education focus.

Outputs: next lessons, explanations, practice prompts, glossary suggestions.

Safety: do not manipulate behavior or push investment activity; optimize for understanding.

Future notes: should be transparent and allow users to reset personalization signals.

## AI Simulations

Purpose: help users explore scenarios such as inflation changes, dividend reinvestment, portfolio drawdowns, or savings plans.

Inputs: scenario parameters, historical data, macro assumptions, asset metrics.

Outputs: scenario narratives, charts, assumptions, sensitivity explanations.

Safety: clearly label simulations as hypothetical and not predictions.

Future notes: requires analytics engine and scenario calculation layer before AI narration.

## AI Explain Like I Am 18

Purpose: simplify complex financial concepts without being patronizing.

Inputs: concept, current context, user level, relevant examples.

Outputs: simple explanation, analogy, example, what to watch out for.

Safety: preserve accuracy while simplifying; avoid false certainty.

Future notes: should be available across asset pages, analytics, news, and assistant responses.

## AI Risk Analysis

Purpose: explain risk drivers at asset, sector, macro, and portfolio levels.

Inputs: volatility, liquidity, drawdown, concentration, currency exposure, macro indicators, news.

Outputs: risk summary, drivers, mitigations to research, metric explanations.

Safety: do not label assets as safe; explain relative and conditional risk.

Future notes: requires mature risk analytics and historical data.

## AI Recommendation Engine

Purpose: help users discover research candidates aligned with goals and profile.

Inputs: investor profile, asset universe, scores, constraints, risk metrics, news, macro context.

Outputs: research suggestions, comparison sets, explanation of fit and tradeoffs.

Safety: must not issue buy/sell commands; must show methodology, uncertainty, and alternatives.

Future notes: implement only after analytics, data quality, profile ownership, and compliance language are mature.
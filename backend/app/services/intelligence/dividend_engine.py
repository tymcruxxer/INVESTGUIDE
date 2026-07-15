"""Deterministic Dividend Intelligence Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

ENGINE_VERSION = "1"
METHODOLOGY_VERSION = "1"


@dataclass(frozen=True)
class DividendIntelligenceBundle:
    """Structured dividend inputs for one company."""

    company: Any
    dividends: tuple[Any, ...] = ()
    income_statements: tuple[Any, ...] = ()
    cash_flow_statements: tuple[Any, ...] = ()
    reference_price: float | None = None
    price_date: str | None = None


def clear_dividend_cache() -> None:
    """Clear process-local dividend intelligence cache."""
    _build_dividend_intelligence_cached.cache_clear()


def build_dividend_intelligence(
    company: Any,
    *,
    dividends: list[Any] | tuple[Any, ...] | None = None,
    income_statements: list[Any] | tuple[Any, ...] | None = None,
    cash_flow_statements: list[Any] | tuple[Any, ...] | None = None,
    reference_price: float | None = None,
    price_date: str | None = None,
) -> dict[str, Any]:
    """Build deterministic Dividend Intelligence from structured records."""
    company_payload = _company_snapshot(company)
    dividend_payloads = tuple(_dividend_snapshot(row) for row in dividends or [])
    income_payloads = tuple(_statement_snapshot(row, ("fiscal_year", "net_profit", "currency", "source_name", "is_development_data", "updated_at")) for row in income_statements or [])
    cash_payloads = tuple(_statement_snapshot(row, ("fiscal_year", "operating_cash_flow", "free_cash_flow", "currency", "source_name", "is_development_data", "updated_at")) for row in cash_flow_statements or [])
    return _build_dividend_intelligence_cached(company_payload, dividend_payloads, income_payloads, cash_payloads, reference_price, price_date)


@lru_cache(maxsize=256)
def _build_dividend_intelligence_cached(
    company: tuple[tuple[str, Any], ...],
    dividends: tuple[tuple[tuple[str, Any], ...], ...],
    income_statements: tuple[tuple[tuple[str, Any], ...], ...],
    cash_flow_statements: tuple[tuple[tuple[str, Any], ...], ...],
    reference_price: float | None,
    price_date: str | None,
) -> dict[str, Any]:
    company_data = dict(company)
    dividend_rows = sorted([dict(item) for item in dividends], key=lambda row: (row.get("fiscal_year") or 0, row.get("payment_date") or ""), reverse=True)
    incomes = sorted([dict(item) for item in income_statements], key=lambda row: row.get("fiscal_year") or 0, reverse=True)
    cash_flows = sorted([dict(item) for item in cash_flow_statements], key=lambda row: row.get("fiscal_year") or 0, reverse=True)

    annual_totals = _annual_dividend_totals(dividend_rows)
    status = _dividend_status(dividend_rows, annual_totals)
    history = _history_analysis(dividend_rows, annual_totals)
    yield_payload = _yield_analysis(annual_totals, reference_price, price_date)
    payout = _payout_ratio(annual_totals, incomes)
    cash_payout = _cash_payout_ratio(annual_totals, cash_flows)
    growth = _growth_analysis(annual_totals)
    consistency = _consistency_assessment(annual_totals)
    sustainability = _sustainability_assessment(payout, cash_payout, growth, consistency, dividend_rows, incomes, cash_flows)
    risks = _risk_factors(payout, cash_payout, growth, consistency, dividend_rows, incomes, cash_flows, reference_price)
    transparency = _transparency(dividend_rows, incomes, cash_flows)

    return {
        "ticker": company_data.get("ticker"),
        "company_name": company_data.get("name"),
        "dividend_status": status,
        "dividend_history": history,
        "dividend_yield": yield_payload,
        "payout_ratio": payout,
        "cash_payout_ratio": cash_payout,
        "dividend_growth": growth,
        "dividend_consistency": consistency,
        "dividend_coverage": _coverage_summary(payout, cash_payout),
        "sustainability_assessment": sustainability,
        "key_risks": risks,
        "educational_summary": _educational_summary(status, sustainability),
        "explain_like_im_18": _eli18(status),
        "data_transparency": transparency,
        "suggested_learning_topics": ["Dividends", "Payout Ratio", "Cash Flow", "Dividend Yield", "Income Investing"],
        "knowledge_graph": _dividend_graph(company_data),
        "generated_at": datetime.now(UTC).isoformat(),
        "engine_version": ENGINE_VERSION,
        "methodology_version": METHODOLOGY_VERSION,
    }


def _annual_dividend_totals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    years: dict[int, dict[str, Any]] = {}
    for row in rows:
        year = row.get("fiscal_year")
        dps = _number(row.get("dividend_per_share"))
        amount = _number(row.get("total_dividend_amount"))
        if year is None:
            continue
        item = years.setdefault(int(year), {"fiscal_year": int(year), "annual_dividend_per_share": 0.0, "total_dividend_amount": 0.0, "record_count": 0, "currency": row.get("currency")})
        item["record_count"] += 1
        if dps is not None:
            item["annual_dividend_per_share"] += dps
        if amount is not None:
            item["total_dividend_amount"] += amount
    return sorted(years.values(), key=lambda item: item["fiscal_year"], reverse=True)


def _dividend_status(rows: list[dict[str, Any]], annual_totals: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [] if rows else ["persisted dividend records"]
    if not rows:
        label = "Dividend Data Unavailable"
        explanation = "No persisted dividend records are available for this company yet. Missing platform data is not proof that the company has never paid a dividend."
        confidence = "Low"
    elif len(annual_totals) == 1:
        label = "Limited Dividend History"
        explanation = "Only one fiscal-year dividend period is available, so InvestGuide cannot establish a long-term pattern."
        confidence = "Low"
    elif _is_consecutive([item["fiscal_year"] for item in annual_totals]) and len(annual_totals) >= 2:
        label = "Consistent Dividend History"
        explanation = "Available records show dividend payments across consecutive fiscal years."
        confidence = "Medium"
    else:
        label = "Irregular Dividend Payer"
        explanation = "Available records do not show a clean consecutive pattern, or the record set has gaps."
        confidence = "Medium"
    return {
        "label": label,
        "explanation": explanation,
        "evidence_used": [f"{len(rows)} dividend record(s)", f"{len(annual_totals)} fiscal year(s) with calculable records"],
        "missing_data": missing,
        "confidence": confidence,
    }


def _history_analysis(rows: list[dict[str, Any]], annual_totals: list[dict[str, Any]]) -> dict[str, Any]:
    periods = [
        {
            "fiscal_year": row.get("fiscal_year"),
            "dividend_type": row.get("dividend_type"),
            "dividend_per_share": _number(row.get("dividend_per_share")),
            "currency": row.get("currency"),
            "announcement_date": row.get("announcement_date"),
            "record_date": row.get("record_date"),
            "ex_dividend_date": row.get("ex_dividend_date"),
            "payment_date": row.get("payment_date"),
            "total_dividend_amount": _number(row.get("total_dividend_amount")),
        }
        for row in rows
    ]
    return {
        "periods": periods,
        "annual_totals": annual_totals,
        "periods_available": len(periods),
        "missing_periods": _missing_years(annual_totals),
        "trend_label": _simple_total_trend(annual_totals),
        "methodology": "Annual totals add available dividend-per-share records by fiscal year. Missing records are not treated as zero unless a source explicitly says no dividend was paid.",
    }


def _yield_analysis(annual_totals: list[dict[str, Any]], reference_price: float | None, price_date: str | None) -> dict[str, Any]:
    latest = annual_totals[0] if annual_totals else None
    dps = _number(latest.get("annual_dividend_per_share")) if latest else None
    if dps is None or dps == 0:
        return _unavailable_metric("Dividend yield", ["annual dividend per share"], "Dividend yield compares annual dividends with a reference share price.")
    if reference_price is None or reference_price <= 0:
        return _unavailable_metric("Dividend yield", ["current or relevant reference price"], "InvestGuide does not use fake or stale prices to calculate dividend yield.")
    value = dps / reference_price
    return {
        "status": "Available",
        "value": round(value, 4),
        "price_date": price_date,
        "dividend_period_used": latest.get("fiscal_year"),
        "interpretation": "Dividend yield shows income received relative to the reference share price, but it is not a guarantee of future income.",
        "limitations": ["Reference price context can change.", "Future dividends depend on company decisions and financial conditions."],
        "educational_explanation": "If a share paid 5 cents in dividends and trades at $1, the historical yield is 5%. That does not mean next year's dividend will be the same.",
    }


def _payout_ratio(annual_totals: list[dict[str, Any]], incomes: list[dict[str, Any]]) -> dict[str, Any]:
    latest = annual_totals[0] if annual_totals else None
    if not latest:
        return _unavailable_metric("Dividend payout ratio", ["total dividends"], "Payout ratio compares dividends with net profit.")
    income = _match_year(incomes, latest["fiscal_year"])
    total = _number(latest.get("total_dividend_amount"))
    net_profit = _number(income.get("net_profit")) if income else None
    if total is None:
        return _unavailable_metric("Dividend payout ratio", ["total dividend amount"], "Dividend per share alone cannot always produce a company-level payout ratio.")
    if net_profit is None:
        return _unavailable_metric("Dividend payout ratio", ["net profit for the dividend period"], "Payout ratio needs profit and dividend totals for the same period.")
    if net_profit <= 0:
        return {
            "status": "Not Meaningful",
            "value": None,
            "period": latest["fiscal_year"],
            "interpretation": "Net profit is zero or negative, so a payout percentage would be misleading.",
            "why_it_matters": "Dividends are easier to evaluate when profits are positive and comparable with distributions.",
            "missing_inputs": [],
            "limitations": ["Negative profit can reflect unusual periods, accounting effects, or real business pressure."],
        }
    value = total / net_profit
    return _ratio_metric("Dividend payout ratio", value, latest["fiscal_year"], "Shows what portion of net profit was distributed as dividends.")


def _cash_payout_ratio(annual_totals: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> dict[str, Any]:
    latest = annual_totals[0] if annual_totals else None
    if not latest:
        return _unavailable_metric("Cash payout ratio", ["total dividends"], "Cash payout ratio compares dividends with operating cash flow.")
    cash = _match_year(cash_flows, latest["fiscal_year"])
    total = _number(latest.get("total_dividend_amount"))
    operating_cash_flow = _number(cash.get("operating_cash_flow")) if cash else None
    if total is None:
        return _unavailable_metric("Cash payout ratio", ["total dividend amount"], "Cash coverage needs total dividend amount.")
    if operating_cash_flow is None:
        return _unavailable_metric("Cash payout ratio", ["operating cash flow for the dividend period"], "Cash coverage needs operating cash flow.")
    if operating_cash_flow <= 0:
        return {
            "status": "Not Meaningful",
            "value": None,
            "period": latest["fiscal_year"],
            "interpretation": "Operating cash flow is zero or negative, so cash payout coverage is not meaningful.",
            "why_it_matters": "Dividends are paid with cash, not accounting profit alone.",
            "missing_inputs": [],
            "limitations": ["One weak cash-flow period may not describe the whole business cycle."],
        }
    return _ratio_metric("Cash payout ratio", total / operating_cash_flow, latest["fiscal_year"], "Shows what portion of operating cash flow was paid as dividends.")


def _growth_analysis(annual_totals: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(annual_totals, key=lambda item: item["fiscal_year"])
    growth_values = []
    for previous, current in zip(ordered, ordered[1:]):
        previous_value = _number(previous.get("annual_dividend_per_share"))
        current_value = _number(current.get("annual_dividend_per_share"))
        if previous_value and current_value is not None:
            growth_values.append({"from": previous["fiscal_year"], "to": current["fiscal_year"], "growth": round((current_value - previous_value) / previous_value, 4)})
    if not growth_values:
        trend = "Insufficient Data"
        explanation = "At least two comparable fiscal years are needed for dividend growth analysis."
        confidence = "Low"
    elif all(item["growth"] > 0.02 for item in growth_values):
        trend = "Increasing"
        explanation = "Available dividend-per-share records increased across comparable periods."
        confidence = "Medium"
    elif all(abs(item["growth"]) <= 0.02 for item in growth_values):
        trend = "Stable"
        explanation = "Available dividend-per-share records stayed broadly similar across periods."
        confidence = "Medium"
    elif all(item["growth"] < -0.02 for item in growth_values):
        trend = "Declining"
        explanation = "Available dividend-per-share records declined across comparable periods."
        confidence = "Medium"
    else:
        trend = "Irregular"
        explanation = "Available dividend-per-share records moved in mixed directions."
        confidence = "Medium"
    return {"annual_growth": growth_values, "compound_annual_growth_rate": None, "trend_label": trend, "explanation": explanation, "confidence": confidence, "missing_years": _missing_years(annual_totals)}


def _consistency_assessment(annual_totals: list[dict[str, Any]]) -> dict[str, Any]:
    years = [item["fiscal_year"] for item in annual_totals]
    if len(years) < 2:
        label = "Insufficient Data"
    elif _is_consecutive(years):
        label = "Consistent"
    else:
        label = "Irregular"
    return {
        "label": label,
        "periods_available": len(years),
        "consecutive_periods": _is_consecutive(years) if years else False,
        "amount_variability": _amount_variability(annual_totals),
        "missing_periods": _missing_years(annual_totals),
        "explanation": "Consistency checks available fiscal years, consecutive records, and whether dividend amounts vary significantly. Missing platform records are not treated as skipped dividends.",
    }


def _sustainability_assessment(payout: dict[str, Any], cash_payout: dict[str, Any], growth: dict[str, Any], consistency: dict[str, Any], dividends: list[dict[str, Any]], incomes: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> dict[str, Any]:
    score = 0
    evidence = []
    missing = []
    for metric, label in ((payout, "profit payout ratio"), (cash_payout, "cash payout ratio")):
        value = metric.get("value")
        if value is None:
            missing.append(label)
        elif value <= 0.75:
            score += 2
            evidence.append(f"{label.title()} appears below 75% from available records.")
        elif value <= 1:
            score += 1
            evidence.append(f"{label.title()} appears elevated but below 100% from available records.")
        else:
            evidence.append(f"{label.title()} appears above 100% from available records.")
    if consistency["label"] == "Consistent":
        score += 1
        evidence.append("Available dividend records are consecutive.")
    if growth["trend_label"] in {"Increasing", "Stable"}:
        score += 1
        evidence.append("Available dividend-per-share trend is not declining.")
    if not dividends:
        label = "Insufficient Evidence"
    elif missing and score < 3:
        label = "Insufficient Evidence"
    elif score >= 5:
        label = "Well Covered by Available Evidence"
    elif score >= 3:
        label = "Moderately Covered"
    elif score >= 1:
        label = "Weakly Covered"
    else:
        label = "Not Meaningful"
    return {
        "score": score,
        "label": label,
        "supporting_evidence": evidence or ["Dividend sustainability evidence is limited."],
        "risks": [],
        "missing_data": missing + _missing_statement_sets(incomes, cash_flows),
        "confidence": "Low" if missing or len(dividends) < 2 else "Medium",
        "methodology": "Combines historical dividend records, payout ratio, cash payout ratio, growth, consistency, and available financial statement evidence. This is educational history, not a prediction.",
    }


def _risk_factors(payout: dict[str, Any], cash_payout: dict[str, Any], growth: dict[str, Any], consistency: dict[str, Any], dividends: list[dict[str, Any]], incomes: list[dict[str, Any]], cash_flows: list[dict[str, Any]], reference_price: float | None) -> list[dict[str, str]]:
    risks = []
    if not dividends:
        risks.append({"risk": "No persisted dividend history", "why_it_matters": "InvestGuide cannot assess dividend behavior without records."})
    if payout.get("value") is not None and payout["value"] > 1:
        risks.append({"risk": "Dividends above net profit", "why_it_matters": "A payout above profit may require reserves, borrowing, or unusual cash sources."})
    if cash_payout.get("value") is not None and cash_payout["value"] > 1:
        risks.append({"risk": "Dividends above operating cash flow", "why_it_matters": "Cash coverage matters because dividends are paid with cash."})
    if growth["trend_label"] == "Declining":
        risks.append({"risk": "Declining dividend-per-share trend", "why_it_matters": "Declines can indicate lower distributions or changing company priorities."})
    if consistency["label"] in {"Irregular", "Interrupted", "Insufficient Data"}:
        risks.append({"risk": "Limited or irregular record", "why_it_matters": "A short or uneven record lowers confidence in historical pattern analysis."})
    if reference_price is None:
        risks.append({"risk": "Unavailable reference price", "why_it_matters": "Dividend yield cannot be calculated without a reliable share price."})
    if not incomes or not cash_flows:
        risks.append({"risk": "Incomplete financial statements", "why_it_matters": "Profit and cash flow help explain whether historical dividends were covered."})
    if any(row.get("is_development_data") for row in dividends):
        risks.append({"risk": "Development-only evidence", "why_it_matters": "Sample fixture records are useful for testing the product but are not verified ZSE or VFEX filings."})
    return risks


def _coverage_summary(payout: dict[str, Any], cash_payout: dict[str, Any]) -> dict[str, Any]:
    return {
        "profit_coverage": payout,
        "cash_coverage": cash_payout,
        "summary": "Dividend coverage is strongest when both profit and operating cash flow can be compared with dividend payments.",
    }


def _transparency(dividends: list[dict[str, Any]], incomes: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [*dividends, *incomes, *cash_flows]
    return {
        "data_sources": sorted({row.get("source_name") for row in rows if row.get("source_name")}) or ["No dividend source is available."],
        "available_periods": sorted({str(row.get("fiscal_year")) for row in rows if row.get("fiscal_year")}, reverse=True),
        "missing_data": _missing_statement_sets(incomes, cash_flows) + ([] if dividends else ["dividend history"]),
        "development_data": any(row.get("is_development_data") for row in rows),
        "evidence_used": [f"{len(dividends)} dividend record(s)", f"{len(incomes)} income statement period(s)", f"{len(cash_flows)} cash flow period(s)"],
        "methodology": "Deterministic historical dividend, payout, cash coverage, growth, and consistency checks from persisted structured rows.",
        "not_advice": "Dividend Intelligence is educational analysis, not financial advice, not a buy/sell signal, and not a prediction that future dividends will be paid.",
        "engine_version": ENGINE_VERSION,
        "methodology_version": METHODOLOGY_VERSION,
    }


def _educational_summary(status: dict[str, Any], sustainability: dict[str, Any]) -> str:
    return f"Dividend Intelligence reviews historical payments, profit coverage, cash coverage, and consistency. Status is {status['label']}; sustainability is {sustainability['label']} based on available evidence. Future dividends remain dependent on company decisions and financial conditions."


def _eli18(status: dict[str, Any]) -> str:
    return f"A dividend is when a company shares part of its profits with investors. {status['label']} means InvestGuide looked at the records it has, but those records do not promise that the company will pay dividends again."


def _dividend_graph(company: dict[str, Any]) -> dict[str, Any]:
    ticker = company.get("ticker") or "Company"
    nodes = [
        {"id": ticker, "label": company.get("name") or ticker, "type": "Company"},
        {"id": "profitability", "label": "Profitability", "type": "Financial Concept"},
        {"id": "operating-cash-flow", "label": "Operating Cash Flow", "type": "Financial Metric"},
        {"id": "dividend-coverage", "label": "Dividend Coverage", "type": "Financial Concept"},
        {"id": "dividend-sustainability", "label": "Dividend Sustainability", "type": "Financial Intelligence"},
        {"id": "income-investing", "label": "Income Investing", "type": "Learning Topic"},
    ]
    edges = [
        {"from": ticker, "to": "profitability", "relationship": "generates"},
        {"from": "profitability", "to": "operating-cash-flow", "relationship": "should convert into"},
        {"from": "operating-cash-flow", "to": "dividend-coverage", "relationship": "helps fund"},
        {"from": "dividend-coverage", "to": "dividend-sustainability", "relationship": "informs"},
        {"from": "dividend-sustainability", "to": "income-investing", "relationship": "helps explain"},
    ]
    return {"nodes": nodes, "edges": edges}


def _ratio_metric(name: str, value: float, period: int, why: str) -> dict[str, Any]:
    return {
        "status": "Available",
        "value": round(value, 4),
        "period": period,
        "interpretation": _ratio_interpretation(value),
        "why_it_matters": why,
        "missing_inputs": [],
        "limitations": ["One ratio should not be interpreted alone.", "Future dividends remain uncertain."],
    }


def _unavailable_metric(name: str, missing_inputs: list[str], explanation: str) -> dict[str, Any]:
    return {
        "status": "Unavailable",
        "value": None,
        "period": None,
        "interpretation": f"{name} is unavailable because required inputs are missing.",
        "why_it_matters": explanation,
        "missing_inputs": missing_inputs,
        "limitations": ["Missing InvestGuide data is not proof that the metric does not exist elsewhere."],
    }


def _ratio_interpretation(value: float) -> str:
    if value <= 0.5:
        return "Lower historical payout from available evidence. This may leave more profit or cash retained in the business."
    if value <= 0.85:
        return "Moderate historical payout from available evidence."
    if value <= 1:
        return "Elevated historical payout from available evidence."
    return "Above 100% from available evidence, which requires careful context and may not be sustainable every period."


def _simple_total_trend(annual_totals: list[dict[str, Any]]) -> str:
    growth = _growth_analysis(annual_totals)
    return growth["trend_label"]


def _amount_variability(annual_totals: list[dict[str, Any]]) -> str:
    values = [_number(item.get("annual_dividend_per_share")) for item in annual_totals if _number(item.get("annual_dividend_per_share")) is not None]
    if len(values) < 2:
        return "Insufficient Data"
    return "Varied" if max(values) > min(values) * 1.25 else "Low Variation"


def _is_consecutive(years: list[int]) -> bool:
    if len(years) < 2:
        return False
    ordered = sorted(set(years))
    return all(next_year - year == 1 for year, next_year in zip(ordered, ordered[1:]))


def _missing_years(annual_totals: list[dict[str, Any]]) -> list[int]:
    years = sorted({item["fiscal_year"] for item in annual_totals})
    if len(years) < 2:
        return []
    expected = set(range(years[0], years[-1] + 1))
    return sorted(expected.difference(years))


def _match_year(rows: list[dict[str, Any]], fiscal_year: int) -> dict[str, Any] | None:
    return next((row for row in rows if row.get("fiscal_year") == fiscal_year), None)


def _missing_statement_sets(incomes: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> list[str]:
    missing = []
    if not incomes:
        missing.append("income statements")
    if not cash_flows:
        missing.append("cash flow statements")
    return missing


def _dividend_snapshot(row: Any) -> tuple[tuple[str, Any], ...]:
    fields = (
        "id",
        "company_id",
        "asset_id",
        "announcement_date",
        "record_date",
        "ex_dividend_date",
        "payment_date",
        "fiscal_year",
        "dividend_type",
        "dividend_per_share",
        "currency",
        "shares_outstanding",
        "total_dividend_amount",
        "source_name",
        "source_type",
        "source_url",
        "imported_at",
        "verified_at",
        "is_development_data",
        "updated_at",
    )
    return tuple(sorted((field, _json_value(getattr(row, field, None))) for field in fields))


def _statement_snapshot(row: Any, fields: tuple[str, ...]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted((field, _json_value(getattr(row, field, None))) for field in fields))


def _company_snapshot(company: Any) -> tuple[tuple[str, Any], ...]:
    fields = ("ticker", "name", "sector", "industry", "country")
    return tuple(sorted((field, _json_value(getattr(company, field, None))) for field in fields))


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (int, float, bool, str)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

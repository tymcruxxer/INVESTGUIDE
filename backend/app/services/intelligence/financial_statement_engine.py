"""Deterministic Financial Statement Intelligence Engine."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from app.services.intelligence.financial_engine import (
    ENGINE_VERSION as BASE_FINANCIAL_ENGINE_VERSION,
    METHODOLOGY_VERSION as BASE_FINANCIAL_METHODOLOGY_VERSION,
    analyze_trends,
    assess_financial_health,
    calculate_ratios,
)

ENGINE_VERSION = "1"
METHODOLOGY_VERSION = "1"


def clear_financial_statement_intelligence_cache() -> None:
    """Clear process-local statement intelligence cache."""
    _build_cached.cache_clear()


def build_financial_statement_intelligence(
    company: Any,
    *,
    income_statements: list[Any] | tuple[Any, ...] | None = None,
    balance_sheets: list[Any] | tuple[Any, ...] | None = None,
    cash_flow_statements: list[Any] | tuple[Any, ...] | None = None,
) -> dict[str, Any]:
    """Translate structured statements into explainable deterministic intelligence."""
    company_payload = _company_snapshot(company)
    income_payloads = tuple(_statement_snapshot(row) for row in income_statements or [])
    balance_payloads = tuple(_statement_snapshot(row) for row in balance_sheets or [])
    cash_payloads = tuple(_statement_snapshot(row) for row in cash_flow_statements or [])
    return _build_cached(company_payload, income_payloads, balance_payloads, cash_payloads)


@lru_cache(maxsize=256)
def _build_cached(
    company: tuple[tuple[str, Any], ...],
    income_statements: tuple[tuple[tuple[str, Any], ...], ...],
    balance_sheets: tuple[tuple[tuple[str, Any], ...], ...],
    cash_flow_statements: tuple[tuple[tuple[str, Any], ...], ...],
) -> dict[str, Any]:
    company_data = dict(company)
    incomes = sorted([dict(row) for row in income_statements], key=lambda row: row.get("fiscal_year") or 0, reverse=True)
    balances = sorted([dict(row) for row in balance_sheets], key=lambda row: row.get("fiscal_year") or 0, reverse=True)
    cash_flows = sorted([dict(row) for row in cash_flow_statements], key=lambda row: row.get("fiscal_year") or 0, reverse=True)

    latest_income = incomes[0] if incomes else {}
    latest_balance = balances[0] if balances else {}
    latest_cash = cash_flows[0] if cash_flows else {}
    ratios = calculate_ratios(latest_income, latest_balance, latest_cash)
    trends = analyze_trends(incomes, balances, cash_flows)
    health = assess_financial_health(ratios, trends, latest_income, latest_balance, latest_cash)
    missing_fields = _missing_fields(latest_income, latest_balance, latest_cash)
    coverage = _coverage(incomes, balances, cash_flows)
    evidence = _evidence(incomes, balances, cash_flows)
    confidence = _confidence(evidence["statement_count"], len(missing_fields), health["uncertainty"])
    provenance = _provenance([*incomes, *balances, *cash_flows], confidence)

    return {
        "ticker": company_data.get("ticker"),
        "company_name": company_data.get("name"),
        "statement_coverage": coverage,
        "available_reporting_periods": _available_periods([*incomes, *balances, *cash_flows]),
        "missing_fields": missing_fields,
        "sections": {
            "revenue": _revenue_section(latest_income, trends, confidence, provenance),
            "profitability": _profitability_section(ratios, trends, confidence, provenance),
            "liquidity": _liquidity_section(ratios, latest_balance, confidence, provenance),
            "leverage": _leverage_section(ratios, latest_balance, confidence, provenance),
            "cash_flow": _cash_flow_section(ratios, trends, latest_cash, confidence, provenance),
            "earnings_quality": _earnings_quality_section(incomes, cash_flows, trends, missing_fields, confidence, provenance),
        },
        "evidence": {
            "confidence": confidence,
            "confidence_reason": _confidence_reason(confidence, evidence["statement_count"], len(missing_fields)),
            "data_used": evidence["data_used"],
            "missing_data": missing_fields,
        },
        "educational_layer": {
            "why_financial_statements_matter": "Financial statements connect sales, profits, assets, debt, and cash so investors can understand business quality instead of relying on headlines.",
            "learn_next": _learn_next(missing_fields),
            "explain_like_im_18": "Think of financial statements like a school report card for a business: income shows what it earned, the balance sheet shows what it owns and owes, and cash flow shows whether real money came in.",
        },
        "transparency": {
            **provenance,
            "methodology": "Deterministic ratio, trend, missing-data, and evidence checks from persisted structured financial statement rows.",
            "not_advice": "This is educational financial statement intelligence, not a buy/sell recommendation, price prediction, or earnings forecast.",
            "engine_version": ENGINE_VERSION,
            "methodology_version": METHODOLOGY_VERSION,
            "base_financial_engine_version": BASE_FINANCIAL_ENGINE_VERSION,
            "base_financial_methodology_version": BASE_FINANCIAL_METHODOLOGY_VERSION,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _revenue_section(income: dict[str, Any], trends: list[dict[str, Any]], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    trend = _find_trend(trends, "Revenue")
    revenue = _number(income.get("revenue"))
    return _section(
        headline="Revenue is unavailable." if revenue is None else f"Latest revenue is {_compact_money(revenue)}.",
        value=revenue,
        trend=trend["direction"],
        explanation=trend["explanation"],
        evidence=[trend["why_it_matters"], _period_evidence(income)],
        confidence=confidence,
        provenance=provenance,
        why_it_matters="Revenue shows whether customers are buying enough from the business before costs are deducted.",
        eli18="Revenue is the money customers paid the company before expenses.",
        learn_next=["Revenue", "Revenue Growth", "Business Model"],
    )


def _profitability_section(ratios: list[dict[str, Any]], trends: list[dict[str, Any]], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    net_margin = _ratio(ratios, "Net Margin")
    operating_margin = _ratio(ratios, "Operating Margin")
    trend = _find_trend(trends, "Net Profit")
    return _section(
        headline=f"Net margin is {_percent(net_margin['value'])}." if net_margin["value"] is not None else "Profit margins are unavailable.",
        value=net_margin["value"],
        trend=trend["direction"],
        explanation="Profitability compares sales with what remains after costs.",
        evidence=[net_margin["interpretation"], operating_margin["interpretation"], trend["explanation"]],
        confidence=confidence,
        provenance=provenance,
        why_it_matters="A company can grow sales and still struggle if too little becomes profit.",
        eli18="Profit margin is how many cents of each dollar of sales are left after costs.",
        learn_next=["Profit Margins", "Operating Profit", "Net Profit"],
    )


def _liquidity_section(ratios: list[dict[str, Any]], balance: dict[str, Any], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    current_ratio = _ratio(ratios, "Current Ratio")
    quick_ratio = _ratio(ratios, "Quick Ratio")
    working_capital = _subtract(balance.get("current_assets"), balance.get("current_liabilities"))
    return _section(
        headline=f"Current ratio is {_ratio_value(current_ratio['value'])}." if current_ratio["value"] is not None else "Liquidity evidence is unavailable.",
        value=current_ratio["value"],
        trend="Point-in-time",
        explanation="Liquidity checks whether near-term assets can cover near-term obligations.",
        evidence=[current_ratio["interpretation"], quick_ratio["interpretation"], f"Working capital: {_compact_money(working_capital)}"],
        confidence=confidence,
        provenance=provenance,
        why_it_matters="Weak liquidity can force a company to borrow, sell assets, or delay payments.",
        eli18="Liquidity asks whether the company has enough near-term resources to pay near-term bills.",
        learn_next=["Working Capital", "Current Ratio", "Quick Ratio"],
    )


def _leverage_section(ratios: list[dict[str, Any]], balance: dict[str, Any], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    debt_to_equity = _ratio(ratios, "Debt-to-Equity")
    debt_ratio = _ratio(ratios, "Debt Ratio")
    return _section(
        headline=f"Debt-to-equity is {_ratio_value(debt_to_equity['value'])}." if debt_to_equity["value"] is not None else "Leverage evidence is unavailable.",
        value=debt_to_equity["value"],
        trend="Point-in-time",
        explanation="Leverage shows how much borrowing supports the company compared with shareholder capital and assets.",
        evidence=[debt_to_equity["interpretation"], debt_ratio["interpretation"]],
        confidence=confidence,
        provenance=provenance,
        why_it_matters="Debt can help a company grow, but too much debt can increase financial pressure.",
        eli18="Leverage is how much the company depends on borrowed money.",
        learn_next=["Debt", "Debt-to-Equity", "Capital Structure"],
    )


def _cash_flow_section(ratios: list[dict[str, Any]], trends: list[dict[str, Any]], cash: dict[str, Any], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    operating_cash = _number(cash.get("operating_cash_flow"))
    free_cash = _number(cash.get("free_cash_flow"))
    trend = _find_trend(trends, "Operating Cash Flow")
    cash_ratio = _ratio(ratios, "Operating Cash Flow Ratio")
    return _section(
        headline=f"Operating cash flow is {_compact_money(operating_cash)}." if operating_cash is not None else "Cash flow evidence is unavailable.",
        value=operating_cash,
        trend=trend["direction"],
        explanation=trend["explanation"],
        evidence=[cash_ratio["interpretation"], f"Free cash flow: {_compact_money(free_cash)}"],
        confidence=confidence,
        provenance=provenance,
        why_it_matters="Cash flow shows whether accounting profit is turning into spendable cash.",
        eli18="Cash flow is the real money moving through the business.",
        learn_next=["Cash Flow", "Free Cash Flow", "Cash Conversion"],
    )


def _earnings_quality_section(incomes: list[dict[str, Any]], cash_flows: list[dict[str, Any]], trends: list[dict[str, Any]], missing_fields: list[str], confidence: str, provenance: dict[str, Any]) -> dict[str, Any]:
    latest_income = incomes[0] if incomes else {}
    latest_cash = cash_flows[0] if cash_flows else {}
    net_profit = _number(latest_income.get("net_profit"))
    operating_cash = _number(latest_cash.get("operating_cash_flow"))
    conversion = None if net_profit in (None, 0) or operating_cash is None else operating_cash / net_profit
    revenue_trend = _find_trend(trends, "Revenue")
    profit_trend = _find_trend(trends, "Net Profit")
    cash_trend = _find_trend(trends, "Operating Cash Flow")
    evidence = [
        f"Cash conversion: {_ratio_value(conversion)}",
        f"Revenue trend: {revenue_trend['direction']}",
        f"Profit trend: {profit_trend['direction']}",
        f"Cash flow trend: {cash_trend['direction']}",
    ]
    if missing_fields:
        evidence.append(f"Missing fields: {', '.join(missing_fields[:5])}")
    return _section(
        headline=_earnings_quality_headline(conversion, missing_fields),
        value=conversion,
        trend="Evidence-based",
        explanation="Earnings quality compares profit, revenue consistency, and cash conversion without inferring unavailable details.",
        evidence=evidence,
        confidence=confidence,
        provenance=provenance,
        why_it_matters="Higher-quality earnings are usually easier to understand when profit is supported by cash and consistent operations.",
        eli18="Good earnings quality means the profit number is backed by real cash and a stable business pattern.",
        learn_next=["Earnings Quality", "Cash Conversion", "Financial Ratios"],
    )


def _section(
    *,
    headline: str,
    value: float | None,
    trend: str,
    explanation: str,
    evidence: list[str],
    confidence: str,
    provenance: dict[str, Any],
    why_it_matters: str,
    eli18: str,
    learn_next: list[str],
) -> dict[str, Any]:
    return {
        "headline": headline,
        "value": value,
        "trend": trend,
        "explanation": explanation,
        "evidence": [item for item in evidence if item],
        "confidence": confidence,
        "provenance": {
            "source": provenance["source"],
            "reporting_period": provenance["reporting_period"],
            "verification_status": provenance["verification_status"],
            "last_updated": provenance["last_updated"],
        },
        "why_it_matters": why_it_matters,
        "explain_like_im_18": eli18,
        "learn_next": learn_next,
    }


def _statement_snapshot(statement: Any) -> tuple[tuple[str, Any], ...]:
    fields = (
        "fiscal_year",
        "period",
        "currency",
        "source_name",
        "source_type",
        "source_url",
        "imported_at",
        "verified_at",
        "verification_status",
        "dataset_version",
        "external_key",
        "is_development_data",
        "updated_at",
        "revenue",
        "cost_of_sales",
        "gross_profit",
        "operating_profit",
        "profit_before_tax",
        "net_profit",
        "interest_expense",
        "total_assets",
        "current_assets",
        "inventory",
        "cash_and_equivalents",
        "total_liabilities",
        "current_liabilities",
        "total_debt",
        "total_equity",
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "net_cash_flow",
        "capital_expenditure",
        "free_cash_flow",
    )
    return tuple(sorted((field, _json_value(getattr(statement, field, None))) for field in fields))


def _company_snapshot(company: Any) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted((field, _json_value(getattr(company, field, None))) for field in ("ticker", "name", "sector", "industry")))


def _coverage(incomes: list[dict[str, Any]], balances: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "income_statement_periods": len(incomes),
        "balance_sheet_periods": len(balances),
        "cash_flow_periods": len(cash_flows),
        "complete_latest_period": bool(incomes and balances and cash_flows),
    }


def _available_periods(rows: list[dict[str, Any]]) -> list[str]:
    periods = {
        f"{row.get('fiscal_year')} {row.get('period') or 'annual'}"
        for row in rows
        if row.get("fiscal_year") is not None
    }
    return sorted(periods, reverse=True)


def _missing_fields(income: dict[str, Any], balance: dict[str, Any], cash: dict[str, Any]) -> list[str]:
    required = (
        ("revenue", income),
        ("gross_profit", income),
        ("operating_profit", income),
        ("net_profit", income),
        ("current_assets", balance),
        ("current_liabilities", balance),
        ("total_debt", balance),
        ("total_equity", balance),
        ("operating_cash_flow", cash),
        ("free_cash_flow", cash),
    )
    return [field for field, row in required if row.get(field) is None]


def _evidence(incomes: list[dict[str, Any]], balances: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> dict[str, Any]:
    data_used = []
    if incomes:
        data_used.append(f"{len(incomes)} income statement period(s)")
    if balances:
        data_used.append(f"{len(balances)} balance sheet period(s)")
    if cash_flows:
        data_used.append(f"{len(cash_flows)} cash flow statement period(s)")
    return {"statement_count": len(incomes) + len(balances) + len(cash_flows), "data_used": data_used or ["No structured financial statements available."]}


def _confidence(statement_count: int, missing_count: int, uncertainty: str) -> str:
    if statement_count >= 6 and missing_count <= 1 and uncertainty == "Low":
        return "High"
    if statement_count >= 3 and missing_count <= 4:
        return "Medium"
    return "Low"


def _confidence_reason(confidence: str, statement_count: int, missing_count: int) -> str:
    return f"{confidence} because {statement_count} statement row(s) are available and {missing_count} key field(s) are missing."


def _provenance(rows: list[dict[str, Any]], confidence: str) -> dict[str, Any]:
    source_names = sorted({row.get("source_name") for row in rows if row.get("source_name")})
    verification_statuses = sorted({row.get("verification_status") for row in rows if row.get("verification_status")})
    return {
        "source": ", ".join(source_names) if source_names else "No financial statement source is available.",
        "sources": source_names or ["No financial statement source is available."],
        "reporting_period": ", ".join(_available_periods(rows)) or "Unavailable",
        "verification_status": ", ".join(verification_statuses) if verification_statuses else ("development_preview" if any(row.get("is_development_data") for row in rows) else "unavailable"),
        "last_updated": _latest_updated(rows),
        "development_data": any(row.get("is_development_data") for row in rows),
        "confidence": confidence,
    }


def _latest_updated(rows: list[dict[str, Any]]) -> str | None:
    timestamps = [
        row.get("verified_at") or row.get("imported_at") or row.get("updated_at") or row.get("created_at")
        for row in rows
        if row.get("verified_at") or row.get("imported_at") or row.get("updated_at") or row.get("created_at")
    ]
    if not timestamps:
        return None
    return max(str(timestamp) for timestamp in timestamps)

def _learn_next(missing_fields: list[str]) -> list[str]:
    topics = ["Understanding Cash Flow", "Profit Margins", "Balance Sheets", "Working Capital", "Debt", "Financial Ratios"]
    if missing_fields:
        topics.append("Why Missing Financial Data Matters")
    return topics


def _ratio(ratios: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return next((ratio for ratio in ratios if ratio["name"] == name), {"name": name, "value": None, "interpretation": "Unavailable.", "why_it_matters": "", "educational_explanation": ""})


def _find_trend(trends: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    return next((trend for trend in trends if trend["metric"] == metric), {"metric": metric, "direction": "Insufficient Data", "values": [], "explanation": "No data available.", "why_it_matters": ""})


def _earnings_quality_headline(conversion: float | None, missing_fields: list[str]) -> str:
    if missing_fields:
        return "Earnings quality confidence is limited by missing data."
    if conversion is None:
        return "Cash conversion is unavailable."
    if conversion >= 1:
        return "Cash conversion supports reported profit."
    if conversion > 0:
        return "Cash conversion is positive but below reported profit."
    return "Cash conversion is weak from available data."


def _period_evidence(row: dict[str, Any]) -> str:
    if not row:
        return "No latest statement period is available."
    return f"Latest period: {row.get('fiscal_year')} {row.get('period') or 'annual'}"


def _compact_money(value: float | None) -> str:
    if value is None:
        return "Unavailable"
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    return f"{value:,.0f}"


def _percent(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value * 100:.1f}%"


def _ratio_value(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value:.2f}"


def _subtract(left: Any, right: Any) -> float | None:
    left_number = _number(left)
    right_number = _number(right)
    if left_number is None:
        return None
    return left_number - (right_number or 0)


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (int, float, bool, str)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


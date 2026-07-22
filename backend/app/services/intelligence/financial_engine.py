"""Deterministic Financial Intelligence Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

ENGINE_VERSION = "1"
METHODOLOGY_VERSION = "1"


@dataclass(frozen=True)
class FinancialStatementBundle:
    """Structured financial statement inputs for one company."""

    company: Any
    income_statements: tuple[Any, ...] = ()
    balance_sheets: tuple[Any, ...] = ()
    cash_flow_statements: tuple[Any, ...] = ()


def clear_financial_cache() -> None:
    """Clear process-local financial intelligence cache."""
    _build_financial_intelligence_cached.cache_clear()


def build_financial_intelligence(
    company: Any,
    *,
    income_statements: list[Any] | tuple[Any, ...] | None = None,
    balance_sheets: list[Any] | tuple[Any, ...] | None = None,
    cash_flow_statements: list[Any] | tuple[Any, ...] | None = None,
) -> dict[str, Any]:
    """Build deterministic financial intelligence from structured statements."""
    income_payloads = tuple(_statement_snapshot(statement) for statement in income_statements or [])
    balance_payloads = tuple(_statement_snapshot(statement) for statement in balance_sheets or [])
    cash_payloads = tuple(_statement_snapshot(statement) for statement in cash_flow_statements or [])
    company_payload = _company_snapshot(company)
    return _build_financial_intelligence_cached(company_payload, income_payloads, balance_payloads, cash_payloads)


@lru_cache(maxsize=256)
def _build_financial_intelligence_cached(
    company: tuple[tuple[str, Any], ...],
    income_statements: tuple[tuple[tuple[str, Any], ...], ...],
    balance_sheets: tuple[tuple[tuple[str, Any], ...], ...],
    cash_flow_statements: tuple[tuple[tuple[str, Any], ...], ...],
) -> dict[str, Any]:
    company_data = dict(company)
    incomes = [dict(item) for item in income_statements]
    balances = [dict(item) for item in balance_sheets]
    cash_flows = [dict(item) for item in cash_flow_statements]

    incomes = sorted(incomes, key=lambda row: row.get("fiscal_year") or 0, reverse=True)
    balances = sorted(balances, key=lambda row: row.get("fiscal_year") or 0, reverse=True)
    cash_flows = sorted(cash_flows, key=lambda row: row.get("fiscal_year") or 0, reverse=True)

    latest_income = incomes[0] if incomes else {}
    latest_balance = balances[0] if balances else {}
    latest_cash_flow = cash_flows[0] if cash_flows else {}

    ratios = calculate_ratios(latest_income, latest_balance, latest_cash_flow)
    trends = analyze_trends(incomes, balances, cash_flows)
    health = assess_financial_health(ratios, trends, latest_income, latest_balance, latest_cash_flow)
    available_periods = sorted(
        {
            str(row["fiscal_year"])
            for row in [*incomes, *balances, *cash_flows]
            if row.get("fiscal_year") is not None
        },
        reverse=True,
    )
    missing_data = _missing_data(incomes, balances, cash_flows, latest_income, latest_balance, latest_cash_flow)

    return {
        "ticker": company_data.get("ticker"),
        "company_name": company_data.get("name"),
        "financial_health": health,
        "revenue_analysis": _revenue_analysis(latest_income, trends),
        "profitability_analysis": _profitability_analysis(ratios, trends),
        "liquidity_analysis": _liquidity_analysis(ratios, latest_balance),
        "leverage_analysis": _leverage_analysis(ratios, latest_balance),
        "cash_flow_analysis": _cash_flow_analysis(latest_cash_flow, ratios, trends),
        "growth_characteristics": _growth_characteristics(trends),
        "stability_assessment": _stability_assessment(trends),
        "revenue_quality": _revenue_quality(company_data, latest_income),
        "balance_sheet_intelligence": _balance_sheet_intelligence(latest_balance, ratios),
        "ratios": ratios,
        "trend_analysis": trends,
        "educational_summary": _educational_summary(health),
        "explain_like_im_18": _eli18(health),
        "knowledge_graph": _financial_graph(company_data),
        "transparency": {
            "data_sources": sorted(
                {
                    row.get("source_name")
                    for row in [*incomes, *balances, *cash_flows]
                    if row.get("source_name")
                }
            )
            or ["No financial statement source is available."],
            "available_periods": available_periods,
            "missing_data": missing_data,
            "evidence_used": _evidence_used(incomes, balances, cash_flows),
            "last_updated": _latest_updated([*incomes, *balances, *cash_flows]),
            "development_data": any(row.get("is_development_data") for row in [*incomes, *balances, *cash_flows]),
            "methodology": "Deterministic ratio, trend, and evidence checks from persisted structured financial statement rows.",
            "not_advice": "This is educational financial intelligence, not a buy/sell recommendation or earnings forecast.",
            "engine_version": ENGINE_VERSION,
            "methodology_version": METHODOLOGY_VERSION,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }


def calculate_ratios(
    income: dict[str, Any],
    balance: dict[str, Any],
    cash_flow: dict[str, Any],
) -> list[dict[str, Any]]:
    """Calculate deterministic ratios with beginner-friendly explanations."""
    definitions = [
        ("Profit Margin", _divide(income.get("gross_profit"), income.get("revenue")), "Gross profit compared with revenue.", "Shows how much money remains after direct costs."),
        ("Operating Margin", _divide(income.get("operating_profit"), income.get("revenue")), "Operating profit compared with revenue.", "Shows whether the core business is profitable before financing and tax effects."),
        ("Net Margin", _divide(income.get("net_profit"), income.get("revenue")), "Net profit compared with revenue.", "Shows how much of each dollar of sales becomes profit after expenses."),
        ("Current Ratio", _divide(balance.get("current_assets"), balance.get("current_liabilities")), "Current assets compared with current liabilities.", "Shows whether short-term assets can cover short-term obligations."),
        ("Quick Ratio", _divide(_subtract(balance.get("current_assets"), balance.get("inventory")), balance.get("current_liabilities")), "Liquid current assets compared with current liabilities.", "A stricter liquidity check that excludes inventory."),
        ("Debt-to-Equity", _divide(balance.get("total_debt"), balance.get("total_equity")), "Debt compared with shareholder equity.", "Shows how much borrowing supports the business relative to owner capital."),
        ("Debt Ratio", _divide(balance.get("total_liabilities"), balance.get("total_assets")), "Liabilities compared with total assets.", "Shows how much of the asset base is funded by obligations."),
        ("Return on Equity", _divide(income.get("net_profit"), balance.get("total_equity")), "Net profit compared with equity.", "Shows how efficiently shareholder capital is producing profit."),
        ("Return on Assets", _divide(income.get("net_profit"), balance.get("total_assets")), "Net profit compared with assets.", "Shows how effectively the asset base produces profit."),
        ("Asset Turnover", _divide(income.get("revenue"), balance.get("total_assets")), "Revenue compared with total assets.", "Shows how efficiently assets generate sales."),
        ("Operating Cash Flow Ratio", _divide(cash_flow.get("operating_cash_flow"), balance.get("current_liabilities")), "Operating cash flow compared with current liabilities.", "Shows whether normal operations generate enough cash for short-term obligations."),
        ("Interest Coverage", _divide(income.get("operating_profit"), income.get("interest_expense")), "Operating profit compared with interest expense.", "Shows whether operating profit can comfortably cover financing costs."),
    ]
    return [
        {
            "name": name,
            "value": round(value, 4) if value is not None else None,
            "interpretation": _ratio_interpretation(name, value),
            "why_it_matters": why,
            "educational_explanation": education,
        }
        for name, value, why, education in definitions
    ]


def analyze_trends(
    incomes: list[dict[str, Any]],
    balances: list[dict[str, Any]],
    cash_flows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compare historical financial periods for key metrics."""
    return [
        _trend("Revenue", incomes, "revenue", "Sales tell us whether the business is getting larger or smaller."),
        _trend("Operating Profit", incomes, "operating_profit", "Operating profit shows how the core business is performing."),
        _trend("Net Profit", incomes, "net_profit", "Net profit shows what remains after all major costs."),
        _trend("Operating Cash Flow", cash_flows, "operating_cash_flow", "Cash flow shows whether profits are turning into real cash."),
        _trend("Debt", balances, "total_debt", "Debt trends show whether borrowing is rising or falling."),
        _trend("Assets", balances, "total_assets", "Assets show the scale of resources controlled by the company."),
        _trend("Equity", balances, "total_equity", "Equity shows the shareholder-funded base of the business."),
    ]


def assess_financial_health(
    ratios: list[dict[str, Any]],
    trends: list[dict[str, Any]],
    income: dict[str, Any],
    balance: dict[str, Any],
    cash_flow: dict[str, Any],
) -> dict[str, Any]:
    """Create a deterministic financial health assessment."""
    score = 0
    evidence: list[str] = []
    cautions: list[str] = []

    ratio_map = {ratio["name"]: ratio["value"] for ratio in ratios}
    if ratio_map.get("Net Margin") is not None and ratio_map["Net Margin"] > 0.08:
        score += 2
        evidence.append("Net margin is positive and above a basic healthy threshold.")
    elif ratio_map.get("Net Margin") is not None and ratio_map["Net Margin"] > 0:
        score += 1
        evidence.append("Net margin is positive.")
    else:
        cautions.append("Net margin is missing or weak.")

    if ratio_map.get("Current Ratio") is not None and ratio_map["Current Ratio"] >= 1.2:
        score += 2
        evidence.append("Current ratio suggests short-term obligations may be manageable.")
    elif ratio_map.get("Current Ratio") is not None and ratio_map["Current Ratio"] >= 1:
        score += 1
        evidence.append("Current ratio is near minimum coverage.")
    else:
        cautions.append("Liquidity evidence is limited or weak.")

    if ratio_map.get("Debt-to-Equity") is not None and ratio_map["Debt-to-Equity"] <= 1:
        score += 2
        evidence.append("Debt-to-equity appears manageable from available data.")
    elif ratio_map.get("Debt-to-Equity") is not None and ratio_map["Debt-to-Equity"] <= 2:
        score += 1
        evidence.append("Debt-to-equity is elevated but not extreme.")
    else:
        cautions.append("Debt evidence is missing or elevated.")

    if ratio_map.get("Operating Cash Flow Ratio") is not None and ratio_map["Operating Cash Flow Ratio"] > 0.5:
        score += 2
        evidence.append("Operating cash flow supports short-term obligations.")
    elif ratio_map.get("Operating Cash Flow Ratio") is not None and ratio_map["Operating Cash Flow Ratio"] > 0:
        score += 1
        evidence.append("Operating cash flow is positive.")
    else:
        cautions.append("Operating cash flow evidence is missing or weak.")

    positive_trends = [trend for trend in trends if trend["direction"] == "Increasing"]
    declining_trends = [trend for trend in trends if trend["direction"] == "Declining"]
    if len(positive_trends) >= 3:
        score += 1
        evidence.append("Several tracked metrics are increasing across available periods.")
    if declining_trends:
        cautions.append("Some tracked metrics are declining across available periods.")

    missing = []
    if not income:
        missing.append("income statement")
    if not balance:
        missing.append("balance sheet")
    if not cash_flow:
        missing.append("cash flow statement")

    label = _health_label(score, missing)
    return {
        "label": label,
        "score": score,
        "why": _health_why(label, score, missing),
        "evidence": evidence or ["Financial statement evidence is limited."],
        "cautions": cautions or ["No major deterministic cautions were identified from available fields."],
        "missing_data": missing,
        "uncertainty": "High" if missing else ("Medium" if score < 5 else "Low"),
    }


def _health_label(score: int, missing: list[str]) -> str:
    if missing:
        return "Moderate" if score >= 5 else "Concerning"
    if score >= 9:
        return "Excellent"
    if score >= 7:
        return "Strong"
    if score >= 5:
        return "Healthy"
    if score >= 3:
        return "Moderate"
    if score >= 1:
        return "Weak"
    return "Concerning"


def _health_why(label: str, score: int, missing: list[str]) -> str:
    if missing:
        return f"{label} because only partial financial statement evidence is available."
    return f"{label} based on deterministic liquidity, leverage, profitability, cash flow, and trend checks."


def _ratio_interpretation(name: str, value: float | None) -> str:
    if value is None:
        return "Unavailable because one or more required inputs are missing."
    if name in {"Profit Margin", "Operating Margin", "Net Margin", "Return on Equity", "Return on Assets"}:
        if value > 0.15:
            return "Strong positive profitability signal."
        if value > 0.05:
            return "Positive profitability signal."
        if value > 0:
            return "Thin but positive profitability signal."
        return "Weak profitability signal."
    if name in {"Current Ratio", "Quick Ratio", "Operating Cash Flow Ratio"}:
        if value >= 1.5:
            return "Strong short-term coverage signal."
        if value >= 1:
            return "Adequate short-term coverage signal."
        return "Potential short-term coverage pressure."
    if name in {"Debt-to-Equity", "Debt Ratio"}:
        if value <= 0.5:
            return "Low leverage signal."
        if value <= 1.5:
            return "Manageable leverage signal."
        return "Elevated leverage signal."
    if name == "Interest Coverage":
        if value >= 5:
            return "Strong interest coverage signal."
        if value >= 2:
            return "Adequate interest coverage signal."
        return "Weak interest coverage signal."
    return "Efficiency indicator from available data."


def _trend(label: str, rows: list[dict[str, Any]], field: str, why: str) -> dict[str, Any]:
    ordered = sorted([row for row in rows if row.get(field) is not None], key=lambda row: row.get("fiscal_year") or 0)
    values = [{"period": row.get("fiscal_year"), "value": _number(row.get(field))} for row in ordered]
    if len(values) < 2:
        direction = "Insufficient Data"
        explanation = f"{label} needs at least two periods to identify a trend."
    else:
        first = values[0]["value"]
        last = values[-1]["value"]
        if first is None or last is None:
            direction = "Insufficient Data"
        elif last > first * 1.05:
            direction = "Increasing"
        elif last < first * 0.95:
            direction = "Declining"
        else:
            direction = "Stable"
        explanation = f"{label} appears {direction.lower()} based on the earliest and latest available periods."
    return {"metric": label, "direction": direction, "values": values, "explanation": explanation, "why_it_matters": why}


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
    payload = {}
    for field in fields:
        value = getattr(statement, field, None)
        if hasattr(value, "value"):
            value = value.value
        payload[field] = _json_value(value)
    return tuple(sorted(payload.items()))


def _company_snapshot(company: Any) -> tuple[tuple[str, Any], ...]:
    fields = ("ticker", "name", "sector", "industry", "country", "description")
    return tuple(sorted((field, _json_value(getattr(company, field, None))) for field in fields))


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
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


def _divide(numerator: Any, denominator: Any) -> float | None:
    left = _number(numerator)
    right = _number(denominator)
    if left is None or right in (None, 0):
        return None
    return left / right


def _subtract(left: Any, right: Any) -> float | None:
    left_number = _number(left)
    right_number = _number(right)
    if left_number is None:
        return None
    return left_number - (right_number or 0)


def _revenue_analysis(income: dict[str, Any], trends: list[dict[str, Any]]) -> dict[str, Any]:
    trend = _find_trend(trends, "Revenue")
    return {
        "current_revenue": _number(income.get("revenue")),
        "trend": trend["direction"],
        "explanation": trend["explanation"],
        "why_it_matters": "Revenue shows the scale of customer demand before costs are deducted.",
    }


def _profitability_analysis(ratios: list[dict[str, Any]], trends: list[dict[str, Any]]) -> dict[str, Any]:
    ratio_map = {ratio["name"]: ratio for ratio in ratios}
    return {
        "net_margin": ratio_map["Net Margin"],
        "operating_margin": ratio_map["Operating Margin"],
        "net_profit_trend": _find_trend(trends, "Net Profit"),
        "explanation": "Profitability connects sales to actual earnings after costs.",
    }


def _liquidity_analysis(ratios: list[dict[str, Any]], balance: dict[str, Any]) -> dict[str, Any]:
    ratio_map = {ratio["name"]: ratio for ratio in ratios}
    return {
        "current_ratio": ratio_map["Current Ratio"],
        "quick_ratio": ratio_map["Quick Ratio"],
        "working_capital": _subtract(balance.get("current_assets"), balance.get("current_liabilities")),
        "explanation": "Liquidity shows whether the company can handle near-term obligations.",
    }


def _leverage_analysis(ratios: list[dict[str, Any]], balance: dict[str, Any]) -> dict[str, Any]:
    ratio_map = {ratio["name"]: ratio for ratio in ratios}
    return {
        "debt_to_equity": ratio_map["Debt-to-Equity"],
        "debt_ratio": ratio_map["Debt Ratio"],
        "total_debt": _number(balance.get("total_debt")),
        "explanation": "Leverage shows how much debt is used to fund the business.",
    }


def _cash_flow_analysis(cash_flow: dict[str, Any], ratios: list[dict[str, Any]], trends: list[dict[str, Any]]) -> dict[str, Any]:
    ratio_map = {ratio["name"]: ratio for ratio in ratios}
    return {
        "operating_cash_flow": _number(cash_flow.get("operating_cash_flow")),
        "free_cash_flow": _number(cash_flow.get("free_cash_flow")),
        "operating_cash_flow_ratio": ratio_map["Operating Cash Flow Ratio"],
        "trend": _find_trend(trends, "Operating Cash Flow"),
        "explanation": "Cash flow matters because bills, dividends, and reinvestment are paid with cash, not accounting profit.",
    }


def _growth_characteristics(trends: list[dict[str, Any]]) -> dict[str, Any]:
    revenue = _find_trend(trends, "Revenue")
    profit = _find_trend(trends, "Net Profit")
    return {
        "label": "Growth-Oriented" if revenue["direction"] == "Increasing" and profit["direction"] == "Increasing" else "Mixed or Unproven",
        "revenue_trend": revenue,
        "profit_trend": profit,
        "explanation": "Growth is strongest when revenue and profit improve together.",
    }


def _stability_assessment(trends: list[dict[str, Any]]) -> dict[str, Any]:
    declining = [trend["metric"] for trend in trends if trend["direction"] == "Declining"]
    return {
        "label": "Stable" if not declining else "Mixed",
        "watch_items": declining,
        "explanation": "Stability is higher when key financial lines avoid sharp declines across periods.",
    }


def _revenue_quality(company: dict[str, Any], income: dict[str, Any]) -> dict[str, Any]:
    return {
        "revenue_drivers": [
            f"{company.get('industry') or 'The industry'} demand",
            "Pricing and volume",
            "Distribution reach",
        ],
        "revenue_concentration": "Unavailable from current structured financial statement fields.",
        "recurring_vs_variable": "Unavailable unless future filings identify recurring contract revenue.",
        "business_stability": "Best assessed together with revenue trend, cash flow trend, and industry context.",
        "educational_explanation": "Revenue quality asks whether sales are repeatable, diversified, and backed by real customer demand.",
        "current_revenue": _number(income.get("revenue")),
    }


def _balance_sheet_intelligence(balance: dict[str, Any], ratios: list[dict[str, Any]]) -> dict[str, Any]:
    ratio_map = {ratio["name"]: ratio for ratio in ratios}
    return {
        "assets": _number(balance.get("total_assets")),
        "liabilities": _number(balance.get("total_liabilities")),
        "equity": _number(balance.get("total_equity")),
        "working_capital": _subtract(balance.get("current_assets"), balance.get("current_liabilities")),
        "liquidity": ratio_map["Current Ratio"]["interpretation"],
        "debt": ratio_map["Debt-to-Equity"]["interpretation"],
        "financial_flexibility": "Higher when liquidity is adequate, debt is manageable, and cash generation is positive.",
    }


def _educational_summary(health: dict[str, Any]) -> str:
    return (
        f"Financial health is marked {health['label']} because InvestGuide checks profitability, liquidity, "
        "debt, cash flow, and trends together. A single strong ratio is not enough; the overall pattern matters."
    )


def _eli18(health: dict[str, Any]) -> str:
    return (
        f"Think of the company like a household budget. A {health['label'].lower()} result means the available "
        "numbers suggest how comfortably the business sells, earns profit, handles bills, manages debt, and turns earnings into cash."
    )


def _financial_graph(company: dict[str, Any]) -> dict[str, Any]:
    ticker = company.get("ticker") or "Company"
    nodes = [
        {"id": ticker, "label": company.get("name") or ticker, "type": "Company"},
        {"id": "revenue", "label": "Revenue", "type": "Financial Metric"},
        {"id": "profitability", "label": "Profitability", "type": "Financial Concept"},
        {"id": "cash-flow", "label": "Cash Flow", "type": "Financial Concept"},
        {"id": "financial-health", "label": "Financial Health", "type": "Financial Intelligence"},
        {"id": "dividend-capacity", "label": "Dividend Capacity", "type": "Learning Topic"},
        {"id": "long-term-investing", "label": "Long-Term Investing", "type": "Learning Topic"},
    ]
    edges = [
        {"from": ticker, "to": "revenue", "relationship": "generates"},
        {"from": "revenue", "to": "profitability", "relationship": "supports"},
        {"from": "profitability", "to": "cash-flow", "relationship": "should convert into"},
        {"from": "cash-flow", "to": "financial-health", "relationship": "informs"},
        {"from": "financial-health", "to": "dividend-capacity", "relationship": "helps assess"},
        {"from": "dividend-capacity", "to": "long-term-investing", "relationship": "connects to"},
    ]
    return {"nodes": nodes, "edges": edges}


def _missing_data(incomes: list[dict[str, Any]], balances: list[dict[str, Any]], cash_flows: list[dict[str, Any]], income: dict[str, Any], balance: dict[str, Any], cash_flow: dict[str, Any]) -> list[str]:
    missing = []
    if len(incomes) < 2:
        missing.append("at least two income statement periods for richer trend analysis")
    if len(balances) < 2:
        missing.append("at least two balance sheet periods for richer trend analysis")
    if len(cash_flows) < 2:
        missing.append("at least two cash flow periods for richer trend analysis")
    required = [
        ("revenue", income),
        ("net_profit", income),
        ("current_assets", balance),
        ("current_liabilities", balance),
        ("total_debt", balance),
        ("operating_cash_flow", cash_flow),
    ]
    for field, row in required:
        if row.get(field) is None:
            missing.append(field)
    return missing


def _evidence_used(incomes: list[dict[str, Any]], balances: list[dict[str, Any]], cash_flows: list[dict[str, Any]]) -> list[str]:
    evidence = []
    if incomes:
        evidence.append(f"{len(incomes)} income statement period(s)")
    if balances:
        evidence.append(f"{len(balances)} balance sheet period(s)")
    if cash_flows:
        evidence.append(f"{len(cash_flows)} cash flow statement period(s)")
    return evidence or ["No structured financial statements available."]


def _latest_updated(rows: list[dict[str, Any]]) -> str | None:
    values = [str(row["updated_at"]) for row in rows if row.get("updated_at")]
    return max(values) if values else None


def _find_trend(trends: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    return next((trend for trend in trends if trend["metric"] == metric), {"metric": metric, "direction": "Insufficient Data", "values": [], "explanation": "No data available.", "why_it_matters": ""})


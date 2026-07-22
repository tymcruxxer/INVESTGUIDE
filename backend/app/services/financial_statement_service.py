"""Financial statement data access services."""

from __future__ import annotations

from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.development_data_guard import get_development_data_policy
from app.models.company import Company
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement

StatementT = TypeVar("StatementT", IncomeStatement, BalanceSheet, CashFlowStatement)


def get_company_financial_statements(
    db: Session,
    company: Company,
) -> tuple[list[IncomeStatement], list[BalanceSheet], list[CashFlowStatement]]:
    """Return financial statements with verified-over-development precedence."""
    return (
        _select_financial_rows(db, company, IncomeStatement),
        _select_financial_rows(db, company, BalanceSheet),
        _select_financial_rows(db, company, CashFlowStatement),
    )


def _select_financial_rows(
    db: Session,
    company: Company,
    model: type[StatementT],
) -> list[StatementT]:
    """Return verified rows first, development rows only when explicitly allowed."""
    rows = list(
        db.scalars(
            select(model)
            .where(model.company_id == company.id)
            .order_by(model.fiscal_year.desc())
        ).all()
    )
    verified_rows = [row for row in rows if not row.is_development_data]
    if verified_rows:
        return verified_rows

    policy = get_development_data_policy()
    if policy.permits_fixtures:
        return [row for row in rows if row.is_development_data]
    return []


def get_latest_financial_statements(
    db: Session,
    company: Company,
) -> tuple[IncomeStatement | None, BalanceSheet | None, CashFlowStatement | None]:
    """Return the latest acceptable statement from each statement family."""
    income, balance, cash_flow = get_company_financial_statements(db, company)
    return (
        income[0] if income else None,
        balance[0] if balance else None,
        cash_flow[0] if cash_flow else None,
    )


def get_available_reporting_periods(
    db: Session,
    company: Company,
) -> list[str]:
    """Return reporting periods available across all acceptable statements."""
    income, balance, cash_flow = get_company_financial_statements(db, company)
    periods = {
        f"{row.fiscal_year} {getattr(row.period, 'value', row.period)}"
        for row in [*income, *balance, *cash_flow]
        if row.fiscal_year is not None
    }
    return sorted(periods, reverse=True)


def get_statement_trends(
    db: Session,
    company: Company,
) -> dict[str, list[dict[str, Any]]]:
    """Return lightweight historical rows by statement family for future API consumers."""
    income, balance, cash_flow = get_company_financial_statements(db, company)
    return {
        "income_statements": [serialize_statement(row) for row in income],
        "balance_sheets": [serialize_statement(row) for row in balance],
        "cash_flow_statements": [serialize_statement(row) for row in cash_flow],
    }


def get_missing_financial_fields(
    db: Session,
    company: Company,
) -> list[str]:
    """Return key financial fields that are unavailable from latest acceptable statements."""
    latest_income, latest_balance, latest_cash_flow = get_latest_financial_statements(db, company)
    required: tuple[tuple[str, Any], ...] = (
        ("revenue", latest_income),
        ("gross_profit", latest_income),
        ("operating_profit", latest_income),
        ("net_profit", latest_income),
        ("current_assets", latest_balance),
        ("current_liabilities", latest_balance),
        ("total_debt", latest_balance),
        ("total_equity", latest_balance),
        ("operating_cash_flow", latest_cash_flow),
        ("free_cash_flow", latest_cash_flow),
    )
    missing = []
    for field, row in required:
        if row is None or getattr(row, field, None) is None:
            missing.append(field)
    return missing


def serialize_statement(statement: Any) -> dict[str, Any]:
    """Serialize one statement row with provenance metadata."""
    payload: dict[str, Any] = {}
    for field in (
        "id",
        "company_id",
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
        "created_at",
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
    ):
        value = getattr(statement, field, None)
        if hasattr(value, "value"):
            value = value.value
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        payload[field] = value
    payload["statement_type"] = statement.__class__.__name__
    payload["data_origin"] = "Development Preview" if getattr(statement, "is_development_data", False) else "Persisted Backend"
    return payload

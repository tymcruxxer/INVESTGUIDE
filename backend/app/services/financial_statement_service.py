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

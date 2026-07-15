"""Manual development seed runner for financial statement fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.database.session import SessionLocal
from app.models.company import Company
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement, StatementPeriod

logger = get_logger(__name__)

SOURCE_NAME = "InvestGuide development financial statement fixture data"

FINANCIAL_STATEMENT_FIXTURES: dict[str, dict[int, dict[str, dict[str, float | str | bool | None]]]] = {
    "DLTA": {
        2024: {
            "common": {"currency": "USD", "source_name": SOURCE_NAME, "source_url": None, "is_development_data": True},
            "income": {
                "revenue": 780_000_000,
                "cost_of_sales": 470_000_000,
                "gross_profit": 310_000_000,
                "operating_profit": 145_000_000,
                "profit_before_tax": 130_000_000,
                "net_profit": 92_000_000,
                "interest_expense": 12_000_000,
            },
            "balance": {
                "total_assets": 620_000_000,
                "current_assets": 265_000_000,
                "inventory": 85_000_000,
                "cash_and_equivalents": 58_000_000,
                "total_liabilities": 260_000_000,
                "current_liabilities": 150_000_000,
                "total_debt": 115_000_000,
                "total_equity": 360_000_000,
            },
            "cash_flow": {
                "operating_cash_flow": 118_000_000,
                "investing_cash_flow": -55_000_000,
                "financing_cash_flow": -42_000_000,
                "net_cash_flow": 21_000_000,
                "capital_expenditure": 48_000_000,
                "free_cash_flow": 70_000_000,
            },
        },
        2023: {
            "common": {"currency": "USD", "source_name": SOURCE_NAME, "source_url": None, "is_development_data": True},
            "income": {
                "revenue": 690_000_000,
                "cost_of_sales": 425_000_000,
                "gross_profit": 265_000_000,
                "operating_profit": 118_000_000,
                "profit_before_tax": 104_000_000,
                "net_profit": 76_000_000,
                "interest_expense": 11_000_000,
            },
            "balance": {
                "total_assets": 565_000_000,
                "current_assets": 235_000_000,
                "inventory": 78_000_000,
                "cash_and_equivalents": 44_000_000,
                "total_liabilities": 245_000_000,
                "current_liabilities": 142_000_000,
                "total_debt": 120_000_000,
                "total_equity": 320_000_000,
            },
            "cash_flow": {
                "operating_cash_flow": 95_000_000,
                "investing_cash_flow": -48_000_000,
                "financing_cash_flow": -35_000_000,
                "net_cash_flow": 12_000_000,
                "capital_expenditure": 42_000_000,
                "free_cash_flow": 53_000_000,
            },
        },
    },
    "ECO": {
        2024: {
            "common": {"currency": "USD", "source_name": SOURCE_NAME, "source_url": None, "is_development_data": True},
            "income": {
                "revenue": 540_000_000,
                "cost_of_sales": 285_000_000,
                "gross_profit": 255_000_000,
                "operating_profit": 105_000_000,
                "profit_before_tax": 82_000_000,
                "net_profit": 58_000_000,
                "interest_expense": 20_000_000,
            },
            "balance": {
                "total_assets": 880_000_000,
                "current_assets": 240_000_000,
                "inventory": 28_000_000,
                "cash_and_equivalents": 70_000_000,
                "total_liabilities": 520_000_000,
                "current_liabilities": 210_000_000,
                "total_debt": 280_000_000,
                "total_equity": 360_000_000,
            },
            "cash_flow": {
                "operating_cash_flow": 112_000_000,
                "investing_cash_flow": -92_000_000,
                "financing_cash_flow": -15_000_000,
                "net_cash_flow": 5_000_000,
                "capital_expenditure": 88_000_000,
                "free_cash_flow": 24_000_000,
            },
        }
    },
}


@dataclass(frozen=True)
class FinancialStatementSeedResult:
    """Summary of a financial statement seed execution."""

    inserted: int
    updated: int
    skipped: int
    missing_companies: list[str]


def seed_financial_statements(
    db: Session,
    fixtures: dict[str, dict[int, dict[str, dict[str, Any]]]] = FINANCIAL_STATEMENT_FIXTURES,
) -> FinancialStatementSeedResult:
    """Seed development financial statements without duplicate rows."""
    ensure_development_data_allowed()
    inserted = 0
    updated = 0
    skipped = 0
    missing_companies: list[str] = []

    try:
        for ticker, years in sorted(fixtures.items()):
            company = db.scalar(select(Company).where(func.upper(Company.ticker) == ticker.upper()))
            if company is None:
                missing_companies.append(ticker)
                skipped += 1
                logger.warning("Skipping financial seed; company %s is missing", ticker)
                continue

            for fiscal_year, payload in sorted(years.items()):
                common = dict(payload.get("common", {}))
                common.update({"company_id": company.id, "fiscal_year": fiscal_year, "period": StatementPeriod.ANNUAL})
                for model, key in (
                    (IncomeStatement, "income"),
                    (BalanceSheet, "balance"),
                    (CashFlowStatement, "cash_flow"),
                ):
                    result = _upsert_statement(db, model, common, dict(payload.get(key, {})))
                    inserted += 1 if result == "inserted" else 0
                    updated += 1 if result == "updated" else 0
                    skipped += 1 if result == "skipped" else 0
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Financial statement seed failed; transaction rolled back")
        raise

    logger.info(
        "Financial statement seed completed: %s inserted, %s updated, %s skipped, %s missing companies",
        inserted,
        updated,
        skipped,
        len(missing_companies),
    )
    return FinancialStatementSeedResult(inserted=inserted, updated=updated, skipped=skipped, missing_companies=missing_companies)


def _upsert_statement(
    db: Session,
    model: type[IncomeStatement] | type[BalanceSheet] | type[CashFlowStatement],
    common: dict[str, Any],
    values: dict[str, Any],
) -> str:
    existing = db.scalar(
        select(model).where(
            model.company_id == common["company_id"],
            model.fiscal_year == common["fiscal_year"],
            model.period == common["period"],
        )
    )
    payload = {**common, **values}
    if existing is None:
        db.add(model(**payload))
        return "inserted"

    changed = False
    if not existing.is_development_data:
        return "skipped"
    for field, value in payload.items():
        if getattr(existing, field) != value:
            setattr(existing, field, value)
            changed = True
    return "updated" if changed else "skipped"


def main() -> None:
    """Run financial statement seeding as an explicit manual command."""
    ensure_development_data_allowed()
    logger.info("Starting manual financial statement seed")
    with SessionLocal() as db:
        result = seed_financial_statements(db)
    logger.info(
        "Manual financial statement seed finished: %s inserted, %s updated, %s skipped",
        result.inserted,
        result.updated,
        result.skipped,
    )


if __name__ == "__main__":
    main()



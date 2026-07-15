"""Safe reporting and optional cleanup for development fixture data."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.session import SessionLocal
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.dividend import CorporateAction, Dividend
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement

logger = get_logger(__name__)


@dataclass(frozen=True)
class DevelopmentDataCleanupReport:
    """Dry-run or confirmed cleanup result."""

    dry_run: bool
    company_profiles: int
    income_statements: int
    balance_sheets: int
    cash_flow_statements: int
    dividends: int
    corporate_actions: int
    deleted: bool

    @property
    def total(self) -> int:
        """Return total development records targeted."""
        return (
            self.company_profiles
            + self.income_statements
            + self.balance_sheets
            + self.cash_flow_statements
            + self.dividends
            + self.corporate_actions
        )


def build_development_data_report(db: Session, *, confirm: bool = False) -> DevelopmentDataCleanupReport:
    """Report development records and delete only when explicitly confirmed."""
    profile_count = db.scalar(
        select(func.count()).select_from(CompanyProfile).where(CompanyProfile.research_status == ResearchStatus.DEVELOPMENT)
    ) or 0
    income_count = _count_development_rows(db, IncomeStatement)
    balance_count = _count_development_rows(db, BalanceSheet)
    cash_count = _count_development_rows(db, CashFlowStatement)
    dividend_count = _count_development_rows(db, Dividend)
    corporate_action_count = _count_development_rows(db, CorporateAction)

    if confirm:
        db.execute(delete(IncomeStatement).where(IncomeStatement.is_development_data.is_(True)))
        db.execute(delete(BalanceSheet).where(BalanceSheet.is_development_data.is_(True)))
        db.execute(delete(CashFlowStatement).where(CashFlowStatement.is_development_data.is_(True)))
        db.execute(delete(Dividend).where(Dividend.is_development_data.is_(True)))
        db.execute(delete(CorporateAction).where(CorporateAction.is_development_data.is_(True)))
        db.execute(delete(CompanyProfile).where(CompanyProfile.research_status == ResearchStatus.DEVELOPMENT))
        db.commit()

    return DevelopmentDataCleanupReport(
        dry_run=not confirm,
        company_profiles=profile_count,
        income_statements=income_count,
        balance_sheets=balance_count,
        cash_flow_statements=cash_count,
        dividends=dividend_count,
        corporate_actions=corporate_action_count,
        deleted=confirm,
    )


def _count_development_rows(db: Session, model: type[IncomeStatement] | type[BalanceSheet] | type[CashFlowStatement] | type[Dividend] | type[CorporateAction]) -> int:
    """Count development financial rows for one statement table."""
    return db.scalar(select(func.count()).select_from(model).where(model.is_development_data.is_(True))) or 0


def main() -> None:
    """Run a dry-run report by default; delete only with --confirm."""
    parser = argparse.ArgumentParser(description="Report or remove development fixture data.")
    parser.add_argument("--dry-run", action="store_true", help="Report development records without deleting them.")
    parser.add_argument("--confirm", action="store_true", help="Delete development records after reviewing the dry-run output.")
    args = parser.parse_args()
    if args.dry_run and args.confirm:
        parser.error("Use either --dry-run or --confirm, not both.")

    with SessionLocal() as db:
        report = build_development_data_report(db, confirm=args.confirm)

    mode = "CONFIRMED DELETE" if args.confirm else "DRY RUN"
    logger.info(
        "%s development data cleanup: %s total records, %s company profiles, %s income statements, "
        "%s balance sheets, %s cash flow statements, %s dividends, %s corporate actions",
        mode,
        report.total,
        report.company_profiles,
        report.income_statements,
        report.balance_sheets,
        report.cash_flow_statements,
        report.dividends,
        report.corporate_actions,
    )
    if not args.confirm:
        logger.info("No records deleted. Re-run with --confirm only after backup and review.")


if __name__ == "__main__":
    main()






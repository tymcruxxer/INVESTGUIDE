"""Development data isolation and cleanup tests."""

from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.database.base import Base
from app.database.cleanup_development_data import build_development_data_report
from app.database.development_data_guard import (
    DEVELOPMENT_DATA_DISABLED_MESSAGE,
    ensure_development_data_allowed,
    get_development_data_policy,
)
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement, StatementPeriod
from app.services import financial_statement_service
from app.services.intelligence.financial_engine import build_financial_intelligence


def test_development_environment_permits_fixture_policy() -> None:
    settings = Settings(APP_ENV="development", ALLOW_DEVELOPMENT_DATA=True)
    policy = get_development_data_policy(settings)

    assert policy.permits_fixtures is True


def test_production_environment_blocks_fixture_policy() -> None:
    settings = Settings(APP_ENV="production", ALLOW_DEVELOPMENT_DATA=False)

    with pytest.raises(RuntimeError, match=DEVELOPMENT_DATA_DISABLED_MESSAGE):
        ensure_development_data_allowed(settings)


class FakeScalarResult:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows

    def scalars(self, *_args, **_kwargs):
        return FakeScalarResult(self.rows)


def test_verified_financial_rows_take_precedence_over_development_rows(monkeypatch) -> None:
    verified = SimpleNamespace(fiscal_year=2024, is_development_data=False)
    development = SimpleNamespace(fiscal_year=2023, is_development_data=True)

    monkeypatch.setattr(
        financial_statement_service,
        "get_development_data_policy",
        lambda: SimpleNamespace(permits_fixtures=True),
    )

    rows = financial_statement_service._select_financial_rows(  # noqa: SLF001
        FakeSession([development, verified]),
        SimpleNamespace(id=1),
        IncomeStatement,
    )

    assert rows == [verified]


def test_production_api_service_excludes_development_financial_rows(monkeypatch) -> None:
    development = SimpleNamespace(fiscal_year=2024, is_development_data=True)

    monkeypatch.setattr(
        financial_statement_service,
        "get_development_data_policy",
        lambda: SimpleNamespace(permits_fixtures=False),
    )

    rows = financial_statement_service._select_financial_rows(  # noqa: SLF001
        FakeSession([development]),
        SimpleNamespace(id=1),
        IncomeStatement,
    )

    assert rows == []


def test_empty_financial_dataset_has_transparent_missing_data() -> None:
    payload = build_financial_intelligence(SimpleNamespace(ticker="NONE", name="No Financials Ltd"))

    assert payload["financial_health"]["missing_data"]
    assert payload["transparency"]["evidence_used"] == ["No structured financial statements available."]


def test_partial_financial_dataset_reports_missing_statements() -> None:
    income = SimpleNamespace(
        fiscal_year=2024,
        period="annual",
        currency="USD",
        source_name="Verified Manual Import",
        source_url=None,
        is_development_data=False,
        revenue=100,
        gross_profit=40,
        operating_profit=20,
        net_profit=10,
        interest_expense=2,
        updated_at=None,
    )

    payload = build_financial_intelligence(
        SimpleNamespace(ticker="PART", name="Partial Financials Ltd"),
        income_statements=[income],
    )

    missing = " ".join(payload["transparency"]["missing_data"])
    assert "balance sheet" in missing
    assert "cash flow" in missing
    assert payload["financial_health"]["uncertainty"] == "High"


def test_cleanup_command_defaults_to_dry_run_and_preserves_records() -> None:
    db = _build_sqlite_session()
    db.add(CompanyProfile(company_id=1, research_status=ResearchStatus.DEVELOPMENT, products_services=[]))
    db.add(CompanyProfile(company_id=2, research_status=ResearchStatus.VERIFIED, products_services=[]))
    db.add(IncomeStatement(company_id=1, fiscal_year=2024, period=StatementPeriod.ANNUAL, is_development_data=True))
    db.commit()

    report = build_development_data_report(db)

    assert report.dry_run is True
    assert report.total == 2
    assert db.query(CompanyProfile).count() == 2
    assert db.query(IncomeStatement).count() == 1


def test_cleanup_confirmation_never_targets_verified_records() -> None:
    db = _build_sqlite_session()
    db.add(CompanyProfile(company_id=1, research_status=ResearchStatus.DEVELOPMENT, products_services=[]))
    db.add(CompanyProfile(company_id=2, research_status=ResearchStatus.VERIFIED, products_services=[]))
    db.add(IncomeStatement(company_id=1, fiscal_year=2024, period=StatementPeriod.ANNUAL, is_development_data=True))
    db.add(BalanceSheet(company_id=1, fiscal_year=2024, period=StatementPeriod.ANNUAL, is_development_data=False))
    db.add(CashFlowStatement(company_id=1, fiscal_year=2024, period=StatementPeriod.ANNUAL, is_development_data=True))
    db.commit()

    report = build_development_data_report(db, confirm=True)

    assert report.deleted is True
    assert db.query(CompanyProfile).filter(CompanyProfile.research_status == ResearchStatus.VERIFIED).count() == 1
    assert db.query(CompanyProfile).filter(CompanyProfile.research_status == ResearchStatus.DEVELOPMENT).count() == 0
    assert db.query(BalanceSheet).count() == 1
    assert db.query(IncomeStatement).count() == 0
    assert db.query(CashFlowStatement).count() == 0


def _build_sqlite_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

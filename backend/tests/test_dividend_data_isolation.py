"""Dividend data isolation tests."""

from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.database.base import Base
from app.database.cleanup_development_data import build_development_data_report
from app.database.development_data_guard import DEVELOPMENT_DATA_DISABLED_MESSAGE, ensure_development_data_allowed
from app.models.company import Company
from app.models.dividend import Dividend, DividendType
from app.models.asset import AssetStatus, Currency, Exchange
from app.services import dividend_service


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


def test_verified_dividends_take_precedence_over_development_rows(monkeypatch) -> None:
    verified = SimpleNamespace(fiscal_year=2024, is_development_data=False)
    development = SimpleNamespace(fiscal_year=2023, is_development_data=True)

    monkeypatch.setattr(dividend_service, "get_development_data_policy", lambda: SimpleNamespace(permits_fixtures=True))

    rows = dividend_service.get_company_dividends(FakeSession([development, verified]), SimpleNamespace(id=1))

    assert rows == [verified]


def test_production_excludes_development_dividends(monkeypatch) -> None:
    development = SimpleNamespace(fiscal_year=2024, is_development_data=True)

    monkeypatch.setattr(dividend_service, "get_development_data_policy", lambda: SimpleNamespace(permits_fixtures=False))

    rows = dividend_service.get_company_dividends(FakeSession([development]), SimpleNamespace(id=1))

    assert rows == []


def test_fixture_seeding_is_blocked_in_production() -> None:
    settings = Settings(APP_ENV="production", ALLOW_DEVELOPMENT_DATA=False)

    with pytest.raises(RuntimeError, match=DEVELOPMENT_DATA_DISABLED_MESSAGE):
        ensure_development_data_allowed(settings)


def test_cleanup_reports_dividend_fixtures_and_preserves_verified_rows() -> None:
    db = _build_sqlite_session()
    company = Company(
        name="Delta Corporation Limited",
        legal_name="Delta Corporation Limited",
        ticker="DLTA",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        country="Zimbabwe",
        market="ZSE",
        currency=Currency.USD,
        status=AssetStatus.ACTIVE,
    )
    db.add(company)
    db.flush()
    db.add(
        Dividend(
            company_id=company.id,
            fiscal_year=2024,
            dividend_type=DividendType.FINAL,
            announcement_date=date(2024, 6, 14),
            is_development_data=True,
        )
    )
    db.add(
        Dividend(
            company_id=company.id,
            fiscal_year=2023,
            dividend_type=DividendType.FINAL,
            announcement_date=date(2023, 6, 14),
            is_development_data=False,
        )
    )
    db.commit()

    dry_run = build_development_data_report(db)
    confirmed = build_development_data_report(db, confirm=True)

    assert dry_run.dividends == 1
    assert dry_run.total == 1
    assert confirmed.deleted is True
    assert db.query(Dividend).count() == 1
    assert db.query(Dividend).filter(Dividend.is_development_data.is_(False)).count() == 1


def _build_sqlite_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

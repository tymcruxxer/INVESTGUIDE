"""Company profile seed runner tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.company_profile_seed import COMPANY_PROFILE_FIXTURES
from app.database.seed import seed_development_assets, seed_development_companies
from app.database.seed_assets import SEED_ASSETS
from app.database.seed_company_profiles import seed_company_profiles
from app.models.asset import Asset
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an in-memory database with company-related tables."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_seed_development_companies_creates_companies_from_assets(db_session: Session) -> None:
    """Unified seed workflow can derive issuer records from asset seed data."""
    seed_development_assets(db_session, [SEED_ASSETS[0], SEED_ASSETS[1]])

    result = seed_development_companies(db_session)
    companies = db_session.scalars(select(Company).order_by(Company.ticker)).all()

    assert result.inserted == 2
    assert result.linked_assets == 2
    assert [company.ticker for company in companies] == ["DLTA", "ECO"]
    assert all(asset.company_id is not None for asset in db_session.scalars(select(Asset)).all())


def test_seed_development_companies_is_duplicate_aware(db_session: Session) -> None:
    """Company seed is safe to run repeatedly."""
    seed_development_assets(db_session, [SEED_ASSETS[0]])

    first_result = seed_development_companies(db_session)
    second_result = seed_development_companies(db_session)

    assert first_result.inserted == 1
    assert second_result.inserted == 0
    assert second_result.skipped == 1
    assert db_session.scalar(select(Company).where(Company.ticker == "DLTA")) is not None


def test_seed_company_profiles_inserts_missing_profiles(db_session: Session) -> None:
    """Company profile seed persists fixture-backed profile data."""
    seed_development_assets(db_session, [SEED_ASSETS[0]])
    seed_development_companies(db_session)

    result = seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})
    profile = db_session.scalar(select(CompanyProfile))

    assert result.inserted == 1
    assert result.updated == 0
    assert result.skipped == 0
    assert profile is not None
    assert profile.research_status == ResearchStatus.DEVELOPMENT
    assert profile.source_name == "InvestGuide development fixture data"


def test_seed_company_profiles_skips_duplicates(db_session: Session) -> None:
    """Company profile seed avoids duplicate profile rows."""
    seed_development_assets(db_session, [SEED_ASSETS[0]])
    seed_development_companies(db_session)

    first_result = seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})
    second_result = seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})
    profile_count = len(db_session.scalars(select(CompanyProfile)).all())

    assert first_result.inserted == 1
    assert second_result.inserted == 0
    assert second_result.skipped == 1
    assert profile_count == 1


def test_seed_company_profiles_updates_missing_fields(db_session: Session) -> None:
    """Existing incomplete development profiles are enriched in place."""
    seed_development_assets(db_session, [SEED_ASSETS[0]])
    seed_development_companies(db_session)
    company = db_session.scalar(select(Company).where(Company.ticker == "DLTA"))
    assert company is not None
    db_session.add(CompanyProfile(company_id=company.id, research_status=ResearchStatus.DEVELOPMENT))
    db_session.commit()

    result = seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})
    profile = db_session.scalar(select(CompanyProfile).where(CompanyProfile.company_id == company.id))

    assert result.updated == 1
    assert profile is not None
    assert profile.primary_business == "Consumer beverages and related fast-moving consumer goods"
    assert profile.products_services == ["Beverages", "Consumer goods distribution"]


def test_seed_company_profiles_preserves_verified_fields(db_session: Session) -> None:
    """Verified research fields are not overwritten by development fixture data."""
    seed_development_assets(db_session, [SEED_ASSETS[0]])
    seed_development_companies(db_session)
    company = db_session.scalar(select(Company).where(Company.ticker == "DLTA"))
    assert company is not None
    db_session.add(
        CompanyProfile(
            company_id=company.id,
            business_summary="Verified business summary",
            primary_business="Verified primary business",
            products_services=["Verified service"],
            research_status=ResearchStatus.VERIFIED,
            source_name="Verified source",
        )
    )
    db_session.commit()

    seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})
    profile = db_session.scalar(select(CompanyProfile).where(CompanyProfile.company_id == company.id))

    assert profile is not None
    assert profile.business_summary == "Verified business summary"
    assert profile.primary_business == "Verified primary business"
    assert profile.products_services == ["Verified service"]
    assert profile.research_status == ResearchStatus.VERIFIED
    assert profile.source_name == "Verified source"


def test_seed_company_profiles_reports_missing_companies(db_session: Session) -> None:
    """Profile seed reports fixture tickers whose companies do not exist yet."""
    result = seed_company_profiles(db_session, {"DLTA": COMPANY_PROFILE_FIXTURES["DLTA"]})

    assert result.inserted == 0
    assert result.skipped == 1
    assert result.missing_companies == ["DLTA"]



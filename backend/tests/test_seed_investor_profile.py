"""Development investor profile seed tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.seed import seed_development_investor_profile
from app.database.seed_investor_profile import DEMO_INVESTOR_PROFILE
from app.models.investor_profile import ExperienceLevel, PreferredLanguageLevel, RiskAppetite


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_demo_investor_profile_seed_shape() -> None:
    """Demo profile seed matches the Sprint 019 development profile contract."""
    assert DEMO_INVESTOR_PROFILE["experience_level"] == ExperienceLevel.BEGINNER
    assert DEMO_INVESTOR_PROFILE["risk_appetite"] == RiskAppetite.MODERATE
    assert DEMO_INVESTOR_PROFILE["investment_horizon"] == "long_term"
    assert DEMO_INVESTOR_PROFILE["planned_investment_range"] == "100_to_500_usd"
    assert DEMO_INVESTOR_PROFILE["preferred_asset_types"] == ["zse", "reits"]
    assert DEMO_INVESTOR_PROFILE["investment_goals"] == ["long_term_wealth", "learning"]
    assert DEMO_INVESTOR_PROFILE["preferred_language_level"] == PreferredLanguageLevel.SIMPLE


def test_seed_development_investor_profile_inserts_once(db_session: Session) -> None:
    """Development profile seed inserts once and skips duplicates."""
    first_result = seed_development_investor_profile(db_session)
    second_result = seed_development_investor_profile(db_session)

    assert first_result.inserted == 1
    assert first_result.skipped == 0
    assert first_result.profile_id == 1
    assert second_result.inserted == 0
    assert second_result.skipped == 1
    assert second_result.profile_id == 1

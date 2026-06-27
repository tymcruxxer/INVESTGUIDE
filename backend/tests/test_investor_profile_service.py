"""Investor profile service tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models.investor_profile import ExperienceLevel, RiskAppetite
from app.models.user import User
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileUpdate
from app.services.personalization_service import (
    InvestorProfileConflictError,
    InvestorProfileValidationError,
    create_investor_profile,
    get_investor_profile,
    update_investor_profile,
)


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


def test_get_investor_profile_returns_none_when_missing(db_session: Session) -> None:
    """Missing development profile returns None at the service layer."""
    assert get_investor_profile(db_session) is None


def test_create_investor_profile_applies_defaults(db_session: Session) -> None:
    """Profile creation applies schema defaults and returns a typed read schema."""
    profile = create_investor_profile(db_session, InvestorProfileCreate())

    assert profile.id == 1
    assert profile.experience_level == ExperienceLevel.BEGINNER
    assert profile.risk_appetite == RiskAppetite.MODERATE
    assert profile.preferred_asset_types == []
    assert profile.investment_goals == []


def test_create_investor_profile_validates_supported_asset_types(db_session: Session) -> None:
    """Unsupported asset preferences are rejected by business rules."""
    payload = InvestorProfileCreate(preferred_asset_types=["crypto"])

    with pytest.raises(InvestorProfileValidationError) as exc_info:
        create_investor_profile(db_session, payload)

    assert "preferred_asset_types" in exc_info.value.details


def test_create_investor_profile_validates_supported_horizon(db_session: Session) -> None:
    """Unsupported investment horizons are rejected by business rules."""
    payload = InvestorProfileCreate(investment_horizon="tomorrow")

    with pytest.raises(InvestorProfileValidationError) as exc_info:
        create_investor_profile(db_session, payload)

    assert "investment_horizon" in exc_info.value.details


def test_update_investor_profile_updates_existing_profile(db_session: Session) -> None:
    """Partial updates modify the first development profile when no user is supplied."""
    create_investor_profile(
        db_session,
        InvestorProfileCreate(
            investment_goals=["learning"],
            preferred_asset_types=["zse"],
        ),
    )

    updated = update_investor_profile(
        db_session,
        InvestorProfileUpdate(
            experience_level=ExperienceLevel.INTERMEDIATE,
            investment_goals=["long_term_wealth", "learning"],
        ),
    )

    assert updated is not None
    assert updated.experience_level == ExperienceLevel.INTERMEDIATE
    assert updated.investment_goals == ["long_term_wealth", "learning"]
    assert updated.preferred_asset_types == ["zse"]


def test_update_investor_profile_returns_none_when_missing(db_session: Session) -> None:
    """Updating without an existing profile returns None for route-level 404 handling."""
    assert update_investor_profile(db_session, InvestorProfileUpdate()) is None


def _create_user(db_session: Session, email: str = "user@example.com") -> User:
    """Create a lightweight persisted user for profile ownership tests."""
    user = User(email=email, hashed_password="hashed-password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_investor_profile_attaches_authenticated_user(db_session: Session) -> None:
    """Profiles created with a user are owned by that user."""
    user = _create_user(db_session)

    profile = create_investor_profile(db_session, InvestorProfileCreate(), user)

    assert profile.user_id == user.id
    assert get_investor_profile(db_session, user).id == profile.id


def test_get_investor_profile_filters_by_authenticated_user(db_session: Session) -> None:
    """User-bound lookups do not return another user's profile."""
    first_user = _create_user(db_session, "first@example.com")
    second_user = _create_user(db_session, "second@example.com")
    create_investor_profile(db_session, InvestorProfileCreate(investment_goals=["learning"]), first_user)

    assert get_investor_profile(db_session, second_user) is None


def test_create_investor_profile_rejects_duplicate_for_user(db_session: Session) -> None:
    """Only one investor profile is allowed for each authenticated user."""
    user = _create_user(db_session)
    create_investor_profile(db_session, InvestorProfileCreate(), user)

    with pytest.raises(InvestorProfileConflictError):
        create_investor_profile(db_session, InvestorProfileCreate(), user)


def test_update_investor_profile_updates_user_profile_only(db_session: Session) -> None:
    """Authenticated updates target only the current user's profile."""
    first_user = _create_user(db_session, "first@example.com")
    second_user = _create_user(db_session, "second@example.com")
    create_investor_profile(db_session, InvestorProfileCreate(investment_goals=["learning"]), first_user)
    create_investor_profile(db_session, InvestorProfileCreate(investment_goals=["diversification"]), second_user)

    updated = update_investor_profile(
        db_session,
        InvestorProfileUpdate(investment_goals=["long_term_wealth"]),
        second_user,
    )

    assert updated is not None
    assert updated.user_id == second_user.id
    assert updated.investment_goals == ["long_term_wealth"]
    assert get_investor_profile(db_session, first_user).investment_goals == ["learning"]

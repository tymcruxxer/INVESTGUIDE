"""Investor profile schema tests."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.investor_profile import ExperienceLevel, PreferredLanguageLevel, RiskAppetite
from app.schemas.investor_profile import (
    InvestorProfileCreate,
    InvestorProfileRead,
    InvestorProfileUpdate,
)


def test_investor_profile_create_defaults_to_beginner_friendly_profile() -> None:
    """Create schema defaults support users before detailed onboarding."""
    schema = InvestorProfileCreate()

    assert schema.user_id is None
    assert schema.experience_level == ExperienceLevel.BEGINNER
    assert schema.risk_appetite == RiskAppetite.MODERATE
    assert schema.preferred_language_level == PreferredLanguageLevel.SIMPLE
    assert schema.preferred_asset_types == []
    assert schema.investment_goals == []
    assert schema.education_focus == []


def test_investor_profile_create_normalizes_preference_lists() -> None:
    """Preference fields accept strings/lists and normalize values."""
    schema = InvestorProfileCreate(
        preferred_asset_types=[" ZSE Equities ", "REITs", "zse equities"],
        investment_goals="Passive Income",
        education_focus=["Dividend Yield", " risk "],
    )

    assert schema.preferred_asset_types == ["zse_equities", "reits"]
    assert schema.investment_goals == ["passive_income"]
    assert schema.education_focus == ["dividend_yield", "risk"]


def test_investor_profile_schema_rejects_invalid_experience_level() -> None:
    """Experience level is constrained to supported personalization tiers."""
    with pytest.raises(ValidationError):
        InvestorProfileCreate(experience_level="expert")


def test_investor_profile_update_allows_partial_payloads() -> None:
    """Update schema supports partial profile edits."""
    schema = InvestorProfileUpdate(risk_appetite=RiskAppetite.CONSERVATIVE)

    assert schema.experience_level is None
    assert schema.risk_appetite == RiskAppetite.CONSERVATIVE


def test_investor_profile_read_accepts_persisted_shape() -> None:
    """Read schema validates persisted profile data."""
    now = datetime(2026, 6, 26, tzinfo=UTC)
    schema = InvestorProfileRead(
        id=1,
        user_id=None,
        experience_level=ExperienceLevel.ADVANCED,
        risk_appetite=RiskAppetite.AGGRESSIVE,
        investment_horizon="long_term",
        planned_investment_range="100_to_500",
        preferred_asset_types=["vfex_equities"],
        investment_goals=["wealth_building"],
        preferred_language_level=PreferredLanguageLevel.TECHNICAL,
        education_focus=["valuation"],
        created_at=now,
        updated_at=now,
    )

    assert schema.id == 1
    assert schema.experience_level == ExperienceLevel.ADVANCED
    assert schema.preferred_language_level == PreferredLanguageLevel.TECHNICAL

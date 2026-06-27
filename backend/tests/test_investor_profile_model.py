"""Investor profile model tests."""

from sqlalchemy import JSON

from app.models.investor_profile import (
    ExperienceLevel,
    InvestorProfile,
    PreferredLanguageLevel,
    RiskAppetite,
)


def test_investor_profile_model_has_required_columns() -> None:
    """InvestorProfile contains the personalization foundation fields."""
    columns = InvestorProfile.__table__.columns

    for column_name in (
        "id",
        "user_id",
        "experience_level",
        "risk_appetite",
        "investment_horizon",
        "planned_investment_range",
        "preferred_asset_types",
        "investment_goals",
        "preferred_language_level",
        "education_focus",
        "created_at",
        "updated_at",
    ):
        assert column_name in columns


def test_investor_profile_model_uses_expected_defaults_and_nullable_user_reference() -> None:
    """Profile can exist before auth while keeping beginner-friendly defaults."""
    columns = InvestorProfile.__table__.columns

    assert columns.user_id.nullable is True
    assert columns.experience_level.default.arg == ExperienceLevel.BEGINNER
    assert columns.risk_appetite.default.arg == RiskAppetite.MODERATE
    assert columns.preferred_language_level.default.arg == PreferredLanguageLevel.SIMPLE
    assert isinstance(columns.preferred_asset_types.type, JSON)
    assert isinstance(columns.investment_goals.type, JSON)
    assert isinstance(columns.education_focus.type, JSON)


def test_investor_profile_indexes_support_future_lookup_and_segments() -> None:
    """Profile indexes support future user lookup and personalization segments."""
    index_names = {index.name for index in InvestorProfile.__table__.indexes}

    assert "ix_investor_profiles_user_id" in index_names
    assert "ix_investor_profiles_experience_level" in index_names
    assert "ix_investor_profiles_risk_appetite" in index_names

def test_investor_profile_user_id_has_foreign_key_and_unique_constraint() -> None:
    """InvestorProfile links to users while nullable dev fallback remains possible."""
    user_id = InvestorProfile.__table__.columns.user_id
    unique_constraints = {constraint.name for constraint in InvestorProfile.__table__.constraints}

    assert user_id.foreign_keys
    assert "uq_investor_profiles_user_id" in unique_constraints

"""Personalization service tests."""

from app.models.investor_profile import ExperienceLevel, RiskAppetite
from app.schemas.investor_profile import InvestorProfileCreate
from app.services.personalization_service import (
    default_personalization_settings,
    determine_personalization_settings,
)


def test_default_personalization_is_beginner_friendly() -> None:
    """Missing profile falls back to safe beginner-friendly behavior."""
    settings = default_personalization_settings()

    assert settings.language_complexity == "simple"
    assert settings.metrics_visibility_level == "essential"
    assert settings.education_depth == "guided"
    assert settings.explanation_style == "plain_language_examples"


def test_beginner_conservative_profile_gets_cautious_plain_language() -> None:
    """Beginner conservative users get cautious simple explanations."""
    settings = determine_personalization_settings(
        experience_level=ExperienceLevel.BEGINNER,
        risk_appetite=RiskAppetite.CONSERVATIVE,
    )

    assert settings.language_complexity == "simple"
    assert settings.metrics_visibility_level == "essential"
    assert settings.explanation_style == "cautious_plain_language"


def test_beginner_income_goal_gets_income_basics() -> None:
    """Passive-income goals adapt education depth for beginner users."""
    settings = determine_personalization_settings(
        experience_level=ExperienceLevel.BEGINNER,
        risk_appetite=RiskAppetite.MODERATE,
        investment_goals=["passive_income"],
    )

    assert settings.education_depth == "income_basics"


def test_intermediate_capital_preservation_profile_is_risk_first() -> None:
    """Intermediate conservative profiles emphasize risk-first context."""
    profile = InvestorProfileCreate(
        experience_level=ExperienceLevel.INTERMEDIATE,
        risk_appetite=RiskAppetite.CONSERVATIVE,
        investment_goals=["capital_preservation"],
    )

    settings = determine_personalization_settings(profile)

    assert settings.language_complexity == "balanced"
    assert settings.metrics_visibility_level == "expanded"
    assert settings.explanation_style == "risk_first_context"


def test_advanced_profile_gets_professional_behavior() -> None:
    """Advanced users see full metrics and technical tradeoff explanations."""
    settings = determine_personalization_settings(
        experience_level=ExperienceLevel.ADVANCED,
        risk_appetite=RiskAppetite.AGGRESSIVE,
        investment_goals=["wealth_building"],
        investment_horizon="long_term",
    )

    assert settings.language_complexity == "technical"
    assert settings.metrics_visibility_level == "full"
    assert settings.education_depth == "methodology_notes"
    assert settings.explanation_style == "analytical_tradeoffs"

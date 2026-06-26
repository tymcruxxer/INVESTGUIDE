"""Personalization rules for adaptive investor education and analytics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.models.investor_profile import ExperienceLevel, RiskAppetite
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileRead


@dataclass(frozen=True)
class PersonalizationSettings:
    """Presentation settings derived from an investor profile."""

    language_complexity: str
    metrics_visibility_level: str
    education_depth: str
    explanation_style: str


def _normalize_goals(goals: Iterable[str] | None) -> set[str]:
    """Normalize goal values for rule matching."""
    return {str(goal).strip().lower().replace(" ", "_") for goal in goals or [] if str(goal).strip()}


def default_personalization_settings() -> PersonalizationSettings:
    """Return safe beginner-friendly defaults when no profile exists yet."""
    return PersonalizationSettings(
        language_complexity="simple",
        metrics_visibility_level="essential",
        education_depth="guided",
        explanation_style="plain_language_examples",
    )


def determine_personalization_settings(
    profile: InvestorProfileCreate | InvestorProfileRead | None = None,
    *,
    experience_level: ExperienceLevel | None = None,
    risk_appetite: RiskAppetite | None = None,
    investment_goals: Iterable[str] | None = None,
    investment_horizon: str | None = None,
) -> PersonalizationSettings:
    """Derive adaptive presentation settings from profile dimensions."""
    if profile is not None:
        experience_level = profile.experience_level
        risk_appetite = profile.risk_appetite
        investment_goals = profile.investment_goals
        investment_horizon = profile.investment_horizon

    if experience_level is None:
        return default_personalization_settings()

    risk_appetite = risk_appetite or RiskAppetite.MODERATE
    goals = _normalize_goals(investment_goals)
    horizon = (investment_horizon or "").strip().lower().replace(" ", "_")

    if experience_level == ExperienceLevel.ADVANCED:
        return PersonalizationSettings(
            language_complexity="technical",
            metrics_visibility_level="full",
            education_depth="methodology_notes",
            explanation_style="analytical_tradeoffs",
        )

    if experience_level == ExperienceLevel.INTERMEDIATE:
        explanation_style = "balanced_context"
        education_depth = "contextual"
        metrics_visibility_level = "expanded"
        if risk_appetite == RiskAppetite.CONSERVATIVE or "capital_preservation" in goals:
            explanation_style = "risk_first_context"
        if "passive_income" in goals or "income" in goals:
            education_depth = "income_focused_context"
        return PersonalizationSettings(
            language_complexity="balanced",
            metrics_visibility_level=metrics_visibility_level,
            education_depth=education_depth,
            explanation_style=explanation_style,
        )

    education_depth = "guided"
    explanation_style = "plain_language_examples"
    if risk_appetite == RiskAppetite.CONSERVATIVE:
        explanation_style = "cautious_plain_language"
    if risk_appetite == RiskAppetite.AGGRESSIVE:
        explanation_style = "risk_aware_plain_language"
    if "passive_income" in goals or "reits" in goals:
        education_depth = "income_basics"
    if "long_term" in horizon or "retirement" in horizon:
        education_depth = "compounding_basics"

    return PersonalizationSettings(
        language_complexity="simple",
        metrics_visibility_level="essential",
        education_depth=education_depth,
        explanation_style=explanation_style,
    )
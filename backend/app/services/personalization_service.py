"""Personalization service layer for investor profiles and adaptive presentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investor_profile import ExperienceLevel, InvestorProfile, RiskAppetite
from app.models.user import User
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileRead, InvestorProfileUpdate

SUPPORTED_INVESTMENT_HORIZONS = {
    "short_term",
    "medium_term",
    "long_term",
    "retirement",
    "education_funding",
    "wealth_transfer",
}
SUPPORTED_ASSET_TYPES = {
    "zse",
    "vfex",
    "reits",
    "zse_equities",
    "vfex_equities",
    "bonds",
    "money_market",
    "alternatives",
}
SUPPORTED_INVESTMENT_GOALS = {
    "long_term_wealth",
    "learning",
    "wealth_building",
    "passive_income",
    "capital_preservation",
    "inflation_protection",
    "usd_exposure",
    "education",
    "diversification",
}


@dataclass(frozen=True)
class PersonalizationSettings:
    """Presentation settings derived from an investor profile."""

    language_complexity: str
    metrics_visibility_level: str
    education_depth: str
    explanation_style: str


class InvestorProfileValidationError(ValueError):
    """Raised when profile values fail business-rule validation."""

    def __init__(self, details: dict[str, list[str]]) -> None:
        super().__init__("Investor profile validation failed")
        self.details = details


class InvestorProfileConflictError(ValueError):
    """Raised when a user already owns an investor profile."""


def _normalize_goals(goals: Iterable[str] | None) -> set[str]:
    """Normalize goal values for rule matching."""
    return {str(goal).strip().lower().replace(" ", "_") for goal in goals or [] if str(goal).strip()}


def _serialize_profile(profile: InvestorProfile) -> InvestorProfileRead:
    """Return a typed read schema for an investor profile ORM object."""
    return InvestorProfileRead.model_validate(profile)


def _profile_query(user: User | None = None):
    """Build the current profile lookup query."""
    statement = select(InvestorProfile).order_by(InvestorProfile.id.asc())
    if user is not None:
        statement = statement.where(InvestorProfile.user_id == user.id)
    return statement


def _validate_supported_values(data: InvestorProfileCreate | InvestorProfileUpdate) -> None:
    """Validate profile values that are flexible strings/lists in storage."""
    errors: dict[str, list[str]] = {}

    horizon = data.investment_horizon
    if horizon is not None and horizon not in SUPPORTED_INVESTMENT_HORIZONS:
        errors["investment_horizon"] = [f"Unsupported investment horizon: {horizon}"]

    asset_types = data.preferred_asset_types
    if asset_types is not None:
        unsupported = sorted(set(asset_types) - SUPPORTED_ASSET_TYPES)
        if unsupported:
            errors["preferred_asset_types"] = [
                f"Unsupported preferred asset types: {', '.join(unsupported)}"
            ]

    goals = data.investment_goals
    if goals is not None:
        unsupported = sorted(set(goals) - SUPPORTED_INVESTMENT_GOALS)
        if unsupported:
            errors["investment_goals"] = [f"Unsupported investment goals: {', '.join(unsupported)}"]

    if errors:
        raise InvestorProfileValidationError(errors)


def default_personalization_settings() -> PersonalizationSettings:
    """Return safe beginner-friendly defaults when no profile exists yet."""
    return PersonalizationSettings(
        language_complexity="simple",
        metrics_visibility_level="essential",
        education_depth="guided",
        explanation_style="plain_language_examples",
    )


def get_investor_profile(db: Session, user: User | None = None) -> InvestorProfileRead | None:
    """Return the authenticated user's profile or the development profile fallback."""
    profile = db.scalars(_profile_query(user)).first()
    if profile is None:
        return None
    return _serialize_profile(profile)


def create_investor_profile(
    db: Session,
    payload: InvestorProfileCreate,
    user: User | None = None,
) -> InvestorProfileRead:
    """Create an investor profile with defaults and business-rule validation."""
    _validate_supported_values(payload)
    if user is not None and get_investor_profile(db, user) is not None:
        raise InvestorProfileConflictError("Investor profile already exists for this user")

    data = payload.model_dump()
    if user is not None:
        data["user_id"] = user.id
    profile = InvestorProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _serialize_profile(profile)


def update_investor_profile(
    db: Session,
    payload: InvestorProfileUpdate,
    user: User | None = None,
) -> InvestorProfileRead | None:
    """Update the authenticated user's profile or the development profile fallback."""
    profile = db.scalars(_profile_query(user)).first()
    if profile is None:
        return None

    _validate_supported_values(payload)
    updates = payload.model_dump(exclude_unset=True)
    if user is not None:
        updates.pop("user_id", None)
    for field_name, value in updates.items():
        setattr(profile, field_name, value)
    if user is not None:
        profile.user_id = user.id

    db.commit()
    db.refresh(profile)
    return _serialize_profile(profile)


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

"""Development investor profile seed data."""

from __future__ import annotations

from app.models.investor_profile import ExperienceLevel, PreferredLanguageLevel, RiskAppetite

DEMO_INVESTOR_PROFILE: dict[str, object] = {
    "user_id": None,
    "experience_level": ExperienceLevel.BEGINNER,
    "risk_appetite": RiskAppetite.MODERATE,
    "investment_horizon": "long_term",
    "planned_investment_range": "100_to_500_usd",
    "preferred_asset_types": ["zse", "reits"],
    "investment_goals": ["long_term_wealth", "learning"],
    "preferred_language_level": PreferredLanguageLevel.SIMPLE,
    "education_focus": ["investing_basics", "reits", "risk"],
}

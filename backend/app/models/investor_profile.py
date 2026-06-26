"""Investor profile SQLAlchemy model for personalization foundations."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin


class ExperienceLevel(StrEnum):
    """Supported investor experience levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class RiskAppetite(StrEnum):
    """Supported investor risk appetite levels."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class PreferredLanguageLevel(StrEnum):
    """Supported explanation language levels."""

    SIMPLE = "simple"
    BALANCED = "balanced"
    TECHNICAL = "technical"


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Return enum values for SQLAlchemy check constraints."""
    return [member.value for member in enum_class]


class InvestorProfile(TimestampMixin, Base):
    """Personalization profile for a current or future authenticated user."""

    __tablename__ = "investor_profiles"
    __table_args__ = (
        Index("ix_investor_profiles_user_id", "user_id"),
        Index("ix_investor_profiles_experience_level", "experience_level"),
        Index("ix_investor_profiles_risk_appetite", "risk_appetite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(
            ExperienceLevel,
            name="investor_experience_level",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=ExperienceLevel.BEGINNER,
        server_default=ExperienceLevel.BEGINNER.value,
    )
    risk_appetite: Mapped[RiskAppetite] = mapped_column(
        Enum(
            RiskAppetite,
            name="investor_risk_appetite",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=RiskAppetite.MODERATE,
        server_default=RiskAppetite.MODERATE.value,
    )
    investment_horizon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    planned_investment_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_asset_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    investment_goals: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preferred_language_level: Mapped[PreferredLanguageLevel] = mapped_column(
        Enum(
            PreferredLanguageLevel,
            name="investor_preferred_language_level",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=PreferredLanguageLevel.SIMPLE,
        server_default=PreferredLanguageLevel.SIMPLE.value,
    )
    education_focus: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
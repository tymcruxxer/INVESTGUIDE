"""Pydantic schemas for investor personalization profiles."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.investor_profile import ExperienceLevel, PreferredLanguageLevel, RiskAppetite


class InvestorProfileBase(BaseModel):
    """Shared investor profile fields."""

    user_id: int | None = None
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    risk_appetite: RiskAppetite = RiskAppetite.MODERATE
    investment_horizon: str | None = Field(default=None, max_length=100)
    planned_investment_range: str | None = Field(default=None, max_length=100)
    preferred_asset_types: list[str] = Field(default_factory=list)
    investment_goals: list[str] = Field(default_factory=list)
    preferred_language_level: PreferredLanguageLevel = PreferredLanguageLevel.SIMPLE
    education_focus: list[str] = Field(default_factory=list)

    @field_validator("preferred_asset_types", "investment_goals", "education_focus", mode="before")
    @classmethod
    def normalize_list_values(cls, value: Any) -> list[str]:
        """Accept strings or lists and normalize preference values."""
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            normalized: list[str] = []
            for item in value:
                text = str(item).strip().lower().replace(" ", "_")
                if text and text not in normalized:
                    normalized.append(text)
            return normalized
        return value

    @field_validator("investment_horizon", "planned_investment_range", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str | None:
        """Trim optional text fields and store blanks as null."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class InvestorProfileCreate(InvestorProfileBase):
    """Schema for creating an investor personalization profile."""


class InvestorProfileUpdate(BaseModel):
    """Schema for updating an investor personalization profile."""

    user_id: int | None = None
    experience_level: ExperienceLevel | None = None
    risk_appetite: RiskAppetite | None = None
    investment_horizon: str | None = Field(default=None, max_length=100)
    planned_investment_range: str | None = Field(default=None, max_length=100)
    preferred_asset_types: list[str] | None = None
    investment_goals: list[str] | None = None
    preferred_language_level: PreferredLanguageLevel | None = None
    education_focus: list[str] | None = None

    @field_validator("preferred_asset_types", "investment_goals", "education_focus", mode="before")
    @classmethod
    def normalize_list_values(cls, value: Any) -> list[str] | None:
        """Accept strings or lists and normalize preference values."""
        if value is None:
            return None
        return InvestorProfileBase.normalize_list_values(value)

    @field_validator("investment_horizon", "planned_investment_range", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str | None:
        """Trim optional text fields and store blanks as null."""
        return InvestorProfileBase.normalize_optional_text(value)


class InvestorProfileRead(InvestorProfileBase):
    """Schema returned for persisted investor profiles."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
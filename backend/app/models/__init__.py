"""SQLAlchemy model registry.

Import model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.associations import asset_news
from app.models.investor_profile import (
    ExperienceLevel,
    InvestorProfile,
    PreferredLanguageLevel,
    RiskAppetite,
)
from app.models.mixins import TimestampMixin
from app.models.news import News
from app.models.user import User

__all__ = [
    "Asset",
    "AssetStatus",
    "AssetType",
    "Currency",
    "Exchange",
    "ExperienceLevel",
    "InvestorProfile",
    "PreferredLanguageLevel",
    "RiskAppetite",
    "News",
    "TimestampMixin",
    "User",
    "asset_news",
]

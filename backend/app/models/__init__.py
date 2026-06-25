"""SQLAlchemy model registry.

Import model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.associations import asset_news
from app.models.mixins import TimestampMixin
from app.models.news import News

__all__ = [
    "Asset",
    "AssetStatus",
    "AssetType",
    "Currency",
    "Exchange",
    "News",
    "TimestampMixin",
    "asset_news",
]
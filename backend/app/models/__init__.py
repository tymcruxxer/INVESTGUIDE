"""SQLAlchemy model registry.

Import model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.mixins import TimestampMixin

__all__ = [
    "Asset",
    "AssetStatus",
    "AssetType",
    "Currency",
    "Exchange",
    "TimestampMixin",
]
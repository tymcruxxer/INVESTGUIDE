"""Pydantic schema registry."""

from app.schemas.asset import AssetBase, AssetCreate, AssetRead, AssetUpdate
from app.schemas.news import NewsBase, NewsCreate, NewsRead

__all__ = [
    "AssetBase",
    "AssetCreate",
    "AssetRead",
    "AssetUpdate",
    "NewsBase",
    "NewsCreate",
    "NewsRead",
]
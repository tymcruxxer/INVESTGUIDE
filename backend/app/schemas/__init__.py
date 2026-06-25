"""Pydantic schema registry."""

from app.schemas.asset import AssetBase, AssetCreate, AssetRead, AssetUpdate

__all__ = ["AssetBase", "AssetCreate", "AssetRead", "AssetUpdate"]
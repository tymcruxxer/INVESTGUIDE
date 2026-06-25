"""Shared SQLAlchemy association tables."""

from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint

from app.database.base import Base

asset_news = Table(
    "asset_news",
    Base.metadata,
    Column("asset_id", Integer, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
    Column("news_id", Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("asset_id", "news_id", name="uq_asset_news_asset_id_news_id"),
)
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

company_news = Table(
    "company_news",
    Base.metadata,
    Column("company_id", Integer, ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True),
    Column("news_id", Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("company_id", "news_id", name="uq_company_news_company_id_news_id"),
)
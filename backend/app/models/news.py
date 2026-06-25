"""Investment news SQLAlchemy model and asset-news association."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Numeric, String, Text, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.associations import asset_news
from app.models.mixins import TimestampMixin
from app.utils.hashing import generate_content_hash

if TYPE_CHECKING:
    from app.models.asset import Asset


class News(TimestampMixin, Base):
    """Investment news article tracked by InvestGuide."""

    __tablename__ = "news_articles"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_news_articles_content_hash"),
        Index("ix_news_articles_source", "source"),
        Index("ix_news_articles_published_at", "published_at"),
        Index("ix_news_articles_url", "url"),
        Index("ix_news_articles_content_hash", "content_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(150), nullable=False)
    author: Mapped[str | None] = mapped_column(String(150), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en", server_default="en")
    sentiment: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    relevance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    credibility_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    assets: Mapped[list[Asset]] = relationship(
        "Asset",
        secondary=asset_news,
        back_populates="news_articles",
    )


@event.listens_for(News, "before_insert")
def populate_news_content_hash(_mapper: object, _connection: object, target: News) -> None:
    """Ensure direct News inserts also persist the canonical content hash."""
    if not target.content_hash:
        target.content_hash = generate_content_hash(target.title, target.summary, target.content)
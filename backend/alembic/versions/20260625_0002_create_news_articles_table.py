"""create news articles table

Revision ID: 20260625_0002
Revises: 20260625_0001
Create Date: 2026-06-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260625_0002"
down_revision: str | None = "20260625_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create news articles and the asset-news association table."""
    op.create_table(
        "news_articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=150), nullable=False),
        sa.Column("author", sa.String(length=150), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("sentiment", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("relevance_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("credibility_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_news_articles"),
    )
    op.create_index("ix_news_articles_source", "news_articles", ["source"], unique=False)
    op.create_index("ix_news_articles_published_at", "news_articles", ["published_at"], unique=False)
    op.create_index("ix_news_articles_url", "news_articles", ["url"], unique=False)

    op.create_table(
        "asset_news",
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("news_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name="fk_asset_news_asset_id_assets", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["news_id"], ["news_articles.id"], name="fk_asset_news_news_id_news_articles", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("asset_id", "news_id", name="pk_asset_news"),
        sa.UniqueConstraint("asset_id", "news_id", name="uq_asset_news_asset_id_news_id"),
    )


def downgrade() -> None:
    """Drop news association and article tables."""
    op.drop_table("asset_news")
    op.drop_index("ix_news_articles_url", table_name="news_articles")
    op.drop_index("ix_news_articles_published_at", table_name="news_articles")
    op.drop_index("ix_news_articles_source", table_name="news_articles")
    op.drop_table("news_articles")
"""News model tests."""

from sqlalchemy import UniqueConstraint

from app.models.asset import Asset
from app.models.associations import asset_news
from app.models.news import News


def test_news_model_has_required_columns() -> None:
    """News model contains the foundation fields plus persisted content hash."""
    columns = News.__table__.columns

    for column_name in (
        "id",
        "title",
        "summary",
        "content",
        "content_hash",
        "source",
        "author",
        "published_at",
        "url",
        "image_url",
        "language",
        "sentiment",
        "relevance_score",
        "credibility_score",
        "created_at",
        "updated_at",
    ):
        assert column_name in columns


def test_asset_news_association_table_links_assets_and_news() -> None:
    """The many-to-many junction table is registered in metadata."""
    assert asset_news.name == "asset_news"
    assert "asset_id" in asset_news.columns
    assert "news_id" in asset_news.columns
    assert asset_news.c.asset_id.primary_key is True
    assert asset_news.c.news_id.primary_key is True
    assert Asset.news_articles.property.secondary is asset_news
    assert News.assets.property.secondary is asset_news


def test_news_model_indexes_support_read_filters_and_hash_lookup() -> None:
    """News table has lookup indexes for read filters and duplicate detection."""
    index_names = {index.name for index in News.__table__.indexes}

    assert "ix_news_articles_source" in index_names
    assert "ix_news_articles_published_at" in index_names
    assert "ix_news_articles_url" in index_names
    assert "ix_news_articles_content_hash" in index_names


def test_news_content_hash_is_unique_and_required() -> None:
    """Persisted content hashes are required and unique for scalable duplicate detection."""
    columns = News.__table__.columns
    unique_names = {
        constraint.name
        for constraint in News.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert columns.content_hash.nullable is False
    assert columns.content_hash.type.length == 64
    assert "uq_news_articles_content_hash" in unique_names
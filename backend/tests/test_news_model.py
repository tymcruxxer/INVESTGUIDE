"""News model tests."""

from app.models.asset import Asset
from app.models.news import News
from app.models.associations import asset_news


def test_news_model_has_required_columns() -> None:
    """News model contains the Sprint 008 foundation fields."""
    columns = News.__table__.columns

    for column_name in (
        "id",
        "title",
        "summary",
        "content",
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


def test_news_model_indexes_support_read_filters() -> None:
    """News table has lookup indexes for source, published date, and URL."""
    index_names = {index.name for index in News.__table__.indexes}

    assert "ix_news_articles_source" in index_names
    assert "ix_news_articles_published_at" in index_names
    assert "ix_news_articles_url" in index_names
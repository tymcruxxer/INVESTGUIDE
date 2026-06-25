"""Read-only news service functions."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database.seed_news import SAMPLE_NEWS_ARTICLES
from app.models.asset import Asset
from app.models.news import News


def _normalize_search(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _seed_matches(
    article: dict[str, Any],
    *,
    source: str | None = None,
    asset: str | None = None,
    search: str | None = None,
) -> bool:
    if source and article["source"].lower() != source.strip().lower():
        return False
    if asset and asset.strip().upper() not in article.get("asset_tickers", []):
        return False
    if search:
        query = search.strip().lower()
        haystack = " ".join(
            str(article.get(field) or "")
            for field in ("title", "summary", "content", "source", "author")
        ).lower()
        return query in haystack
    return True


def _list_seed_news(
    *,
    source: str | None = None,
    asset: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
) -> tuple[list[dict[str, Any]], int]:
    filtered = [
        article
        for article in SAMPLE_NEWS_ARTICLES
        if _seed_matches(article, source=source, asset=asset, search=search)
    ]
    reverse = sort != "asc"
    filtered.sort(key=lambda article: article["published_at"], reverse=reverse)
    total = len(filtered)
    offset = (page - 1) * limit
    return filtered[offset : offset + limit], total


def list_news(
    db: Session,
    *,
    source: str | None = None,
    asset: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
) -> tuple[list[News | dict[str, Any]], int]:
    """Return paginated news matching optional filters.

    Falls back to development sample data when the configured database is not
    available, keeping the foundation API usable before local PostgreSQL is set up.
    """
    normalized_search = _normalize_search(search)
    filters = []

    if source:
        filters.append(func.lower(News.source) == source.strip().lower())
    if normalized_search:
        search_pattern = f"%{normalized_search}%"
        filters.append(
            or_(
                News.title.ilike(search_pattern),
                News.summary.ilike(search_pattern),
                News.content.ilike(search_pattern),
                News.source.ilike(search_pattern),
                News.author.ilike(search_pattern),
            )
        )

    query = select(News).options(selectinload(News.assets))
    total_query = select(func.count(func.distinct(News.id))).select_from(News)

    if asset:
        normalized_asset = asset.strip().upper()
        query = query.join(News.assets).where(func.upper(Asset.ticker) == normalized_asset)
        total_query = total_query.join(News.assets).where(func.upper(Asset.ticker) == normalized_asset)

    query = query.where(*filters)
    total_query = total_query.where(*filters)

    order_by = News.published_at.asc() if sort == "asc" else News.published_at.desc()
    query = query.order_by(order_by, News.id.desc()).offset((page - 1) * limit).limit(limit)

    try:
        total = db.scalar(total_query) or 0
        articles = list(db.scalars(query).unique().all())
        return articles, total
    except SQLAlchemyError:
        return _list_seed_news(
            source=source,
            asset=asset,
            search=normalized_search,
            page=page,
            limit=limit,
            sort=sort,
        )


def get_news(db: Session, news_id: int) -> News | dict[str, Any] | None:
    """Return one news article by id, falling back to sample data if needed."""
    query = select(News).options(selectinload(News.assets)).where(News.id == news_id)
    try:
        return db.scalar(query)
    except SQLAlchemyError:
        return next((article for article in SAMPLE_NEWS_ARTICLES if article["id"] == news_id), None)
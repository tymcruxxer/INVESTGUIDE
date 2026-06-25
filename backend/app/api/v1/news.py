"""Read-only news endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.schemas.news import NewsRead
from app.services import news_service

router = APIRouter(prefix="/news", tags=["news"])


def _serialize_news(article: Any) -> dict[str, Any]:
    """Serialize ORM or development seed news objects into API-safe dictionaries."""
    if isinstance(article, dict):
        payload = dict(article)
        now = datetime.now(UTC)
        payload.setdefault("created_at", now)
        payload.setdefault("updated_at", now)
        return NewsRead.model_validate(payload).model_dump(mode="json")

    payload = {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "source": article.source,
        "author": article.author,
        "published_at": article.published_at,
        "url": article.url,
        "image_url": article.image_url,
        "language": article.language,
        "sentiment": article.sentiment,
        "relevance_score": article.relevance_score,
        "credibility_score": article.credibility_score,
        "asset_tickers": [asset.ticker for asset in article.assets],
        "created_at": article.created_at,
        "updated_at": article.updated_at,
    }
    return NewsRead.model_validate(payload).model_dump(mode="json")


@router.get("")
async def list_news(
    source: str | None = Query(default=None, min_length=1, max_length=150),
    asset: str | None = Query(default=None, min_length=1, max_length=20),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List investment news with optional filtering and pagination."""
    articles, total = news_service.list_news(
        db,
        source=source,
        asset=asset,
        search=search,
        sort=sort,
        page=page,
        limit=limit,
    )

    return success_response(
        message="News retrieved successfully",
        data=[_serialize_news(article) for article in articles],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": page * limit < total,
            "source": source,
            "asset": asset.strip().upper() if asset else None,
            "sort": sort,
        },
    )


@router.get("/{news_id}", response_model=None)
async def get_news(
    news_id: int,
    db: Session = Depends(get_db),
):
    """Return a news article by id."""
    article = news_service.get_news(db, news_id)
    if article is None:
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"News article '{news_id}' was not found",
                error_code="NEWS_NOT_FOUND",
            ),
        )

    return success_response(
        message="News article retrieved successfully",
        data=_serialize_news(article),
    )
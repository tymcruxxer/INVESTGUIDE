"""Duplicate detection helpers for news ingestion."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.news import News
from app.schemas.ingestion_report import DuplicateStatus, IngestionArticlePayload
from app.utils.hashing import generate_content_hash, normalize_title


def _same_published_at(left: datetime | None, right: datetime | None) -> bool:
    if left is None or right is None:
        return False
    return left == right


def incoming_content_hash(payload: IngestionArticlePayload) -> str:
    """Generate the canonical content hash for an incoming ingestion payload."""
    return generate_content_hash(payload.title, payload.summary, payload.content)


def check_news_duplicate(db: Session, payload: IngestionArticlePayload) -> DuplicateStatus:
    """Classify whether an incoming article already exists."""
    if payload.url:
        existing_by_url = db.scalar(select(News).where(News.url == payload.url))
        if existing_by_url is not None:
            return "DUPLICATE"

    content_hash = incoming_content_hash(payload)
    existing_by_hash = db.scalar(select(News).where(News.content_hash == content_hash))
    if existing_by_hash is not None:
        return "DUPLICATE"

    normalized_title = normalize_title(payload.title)
    title_candidates = db.scalars(select(News).where(News.title.ilike(payload.title))).all()
    possible_duplicate = False

    for article in title_candidates:
        if normalize_title(article.title) != normalized_title:
            continue
        if _same_published_at(article.published_at, payload.published_at):
            return "DUPLICATE"
        possible_duplicate = True

    if possible_duplicate:
        return "POSSIBLE_DUPLICATE"

    return "NEW"
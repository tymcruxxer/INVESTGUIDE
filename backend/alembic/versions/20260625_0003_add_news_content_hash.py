"""add news content hash

Revision ID: 20260625_0003
Revises: 20260625_0002
Create Date: 2026-06-25
"""

from __future__ import annotations

from collections.abc import Sequence
import hashlib
import re

from alembic import op
import sqlalchemy as sa


revision: str = "20260625_0003"
down_revision: str | None = "20260625_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TITLE_PATTERN = re.compile(r"[^a-z0-9]+")


def _normalize_title(title: str) -> str:
    return _TITLE_PATTERN.sub(" ", title.lower()).strip()


def _generate_content_hash(title: str, summary: str | None, content: str | None) -> str:
    parts = [_normalize_title(title), (summary or "").strip().lower(), (content or "").strip().lower()]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def upgrade() -> None:
    """Persist deterministic content hashes for scalable duplicate detection."""
    op.add_column("news_articles", sa.Column("content_hash", sa.String(length=64), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, title, summary, content FROM news_articles")).mappings()
    for row in rows:
        content_hash = _generate_content_hash(row["title"], row["summary"], row["content"])
        connection.execute(
            sa.text("UPDATE news_articles SET content_hash = :content_hash WHERE id = :id"),
            {"content_hash": content_hash, "id": row["id"]},
        )

    op.alter_column("news_articles", "content_hash", existing_type=sa.String(length=64), nullable=False)
    op.create_index("ix_news_articles_content_hash", "news_articles", ["content_hash"], unique=False)
    op.create_unique_constraint("uq_news_articles_content_hash", "news_articles", ["content_hash"])


def downgrade() -> None:
    """Remove persisted content hashes from news articles."""
    op.drop_constraint("uq_news_articles_content_hash", "news_articles", type_="unique")
    op.drop_index("ix_news_articles_content_hash", table_name="news_articles")
    op.drop_column("news_articles", "content_hash")
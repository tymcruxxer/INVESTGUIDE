"""News schema tests."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.news import NewsCreate, NewsRead


def test_news_create_normalizes_asset_tickers() -> None:
    """News schemas normalize related tickers for future linking."""
    schema = NewsCreate(
        title="Sample: Delta market note",
        summary="Development placeholder.",
        content=None,
        source="InvestGuide Sample Data",
        author=None,
        published_at=datetime(2026, 6, 25, tzinfo=UTC),
        asset_tickers=[" dlta ", "eco"],
    )

    assert schema.asset_tickers == ["DLTA", "ECO"]
    assert schema.language == "en"


def test_news_schema_rejects_invalid_scores() -> None:
    """Scores are constrained for later analytics and sentiment usage."""
    with pytest.raises(ValidationError):
        NewsCreate(
            title="Invalid score",
            source="InvestGuide Sample Data",
            published_at=datetime(2026, 6, 25, tzinfo=UTC),
            sentiment=Decimal("1.50"),
        )


def test_news_read_accepts_persisted_shape() -> None:
    """NewsRead validates persisted article data."""
    now = datetime(2026, 6, 25, tzinfo=UTC)
    schema = NewsRead(
        id=1,
        title="Sample: RBZ policy context",
        summary=None,
        content=None,
        source="InvestGuide Sample Data",
        author="InvestGuide Development",
        published_at=now,
        url=None,
        image_url=None,
        language="en",
        sentiment=None,
        relevance_score=Decimal("0.50"),
        credibility_score=Decimal("0.40"),
        asset_tickers=[],
        created_at=now,
        updated_at=now,
    )

    assert schema.id == 1
    assert schema.source == "InvestGuide Sample Data"
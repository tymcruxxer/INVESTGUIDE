"""News service tests."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.news import News
from app.services.news_service import get_news, list_news


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an in-memory database session for service tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    delta = Asset(
        ticker="DLTA",
        company_name="Delta Corporation Limited",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        status=AssetStatus.ACTIVE,
    )
    econet = Asset(
        ticker="ECO",
        company_name="Econet Wireless Zimbabwe Limited",
        exchange=Exchange.ZSE,
        sector="Telecommunications",
        industry="Mobile Telecommunications",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        status=AssetStatus.ACTIVE,
    )
    session.add_all([delta, econet])
    session.flush()

    session.add_all(
        [
            News(
                title="Sample: Delta market note",
                summary="Delta development placeholder.",
                content="Sample article for testing.",
                source="InvestGuide Sample Data",
                author="InvestGuide Development",
                published_at=datetime(2026, 6, 25, 8, 0, tzinfo=UTC),
                assets=[delta],
            ),
            News(
                title="Sample: Econet telecom note",
                summary="Econet development placeholder.",
                content="Telecommunications sample article.",
                source="InvestGuide Sample Data",
                author="InvestGuide Development",
                published_at=datetime(2026, 6, 24, 8, 0, tzinfo=UTC),
                assets=[econet],
            ),
            News(
                title="Sample: RBZ policy context",
                summary="Macro development placeholder.",
                content="Central bank policy sample article.",
                source="Macro Sample",
                author="InvestGuide Development",
                published_at=datetime(2026, 6, 23, 8, 0, tzinfo=UTC),
            ),
        ]
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_list_news_filters_by_asset_and_search(db_session: Session) -> None:
    """Service supports asset filtering and search."""
    articles, total = list_news(db_session, asset="dlta", search="Delta", page=1, limit=20)

    assert total == 1
    assert articles[0].title == "Sample: Delta market note"
    assert articles[0].assets[0].ticker == "DLTA"


def test_list_news_filters_by_source_and_sorts_ascending(db_session: Session) -> None:
    """Service supports source filtering and date sorting."""
    articles, total = list_news(db_session, source="InvestGuide Sample Data", sort="asc", page=1, limit=20)

    assert total == 2
    assert [article.title for article in articles] == [
        "Sample: Econet telecom note",
        "Sample: Delta market note",
    ]


def test_get_news_returns_article_by_id(db_session: Session) -> None:
    """Service returns a single article by id."""
    article = get_news(db_session, 1)

    assert article is not None
    assert article.title == "Sample: Delta market note"


def test_list_news_falls_back_to_seed_data_when_database_unavailable(monkeypatch, db_session: Session) -> None:
    """Service returns development seed data if DB access fails."""

    def raise_operational_error(*args, **kwargs):
        raise OperationalError("select", {}, Exception("database unavailable"))

    monkeypatch.setattr(db_session, "scalar", raise_operational_error)

    articles, total = list_news(db_session, asset="ECO", page=1, limit=10)

    assert total >= 1
    assert articles[0]["source"] == "InvestGuide Sample Data"
    assert "ECO" in articles[0]["asset_tickers"]
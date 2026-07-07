"""Company service tests."""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.company import Company
from app.models.news import News
from app.services.company_service import get_company_by_ticker, get_company_news, list_companies


def make_session() -> Session:
    """Create an isolated in-memory database session for service tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_list_companies_filters_by_search() -> None:
    """Company list supports text search across issuer fields."""
    session = make_session()
    session.add_all(
        [
            Company(name="Delta Corporation Limited", ticker="DLTA", exchange=Exchange.ZSE, sector="Consumer Staples"),
            Company(name="Econet Wireless Zimbabwe", ticker="ECO", exchange=Exchange.ZSE, sector="Telecommunications"),
        ]
    )
    session.commit()

    companies, total = list_companies(session, search="delta")

    assert total == 1
    assert companies[0].ticker == "DLTA"


def test_get_company_by_ticker_loads_related_assets() -> None:
    """Ticker lookup returns company intelligence with related assets loaded."""
    session = make_session()
    company = Company(name="Delta Corporation Limited", ticker="DLTA", exchange=Exchange.ZSE, sector="Consumer Staples")
    asset = Asset(
        ticker="DLTA",
        company_name="Delta Corporation Limited",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        description="Beverages company.",
        status=AssetStatus.ACTIVE,
        company=company,
    )
    session.add(asset)
    session.commit()

    found = get_company_by_ticker(session, "dlta")

    assert found is not None
    assert found.ticker == "DLTA"
    assert found.assets[0].ticker == "DLTA"


def test_get_company_news_falls_back_to_asset_news() -> None:
    """Company news can be derived from news attached to related assets."""
    session = make_session()
    company = Company(name="Delta Corporation Limited", ticker="DLTA", exchange=Exchange.ZSE)
    asset = Asset(
        ticker="DLTA",
        company_name="Delta Corporation Limited",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        description="Beverages company.",
        status=AssetStatus.ACTIVE,
        company=company,
    )
    article = News(
        title="Delta sample update",
        source="InvestGuide Sample",
        published_at=datetime(2026, 7, 3, tzinfo=UTC),
        content_hash="a" * 64,
        assets=[asset],
    )
    session.add(article)
    session.commit()

    news = get_company_news(session, company)

    assert [article.title for article in news] == ["Delta sample update"]
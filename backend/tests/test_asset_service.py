"""Asset service tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.services.asset_service import get_asset_by_ticker, list_assets


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an in-memory database session for service tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Asset.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    session.add_all(
        [
            Asset(
                ticker="DLTA",
                company_name="Delta Corporation Limited",
                exchange=Exchange.ZSE,
                sector="Consumer Staples",
                industry="Beverages",
                asset_type=AssetType.EQUITY,
                currency=Currency.ZWG,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                ticker="ECO",
                company_name="Econet Wireless Zimbabwe Limited",
                exchange=Exchange.ZSE,
                sector="Telecommunications",
                industry="Mobile Telecommunications",
                asset_type=AssetType.EQUITY,
                currency=Currency.ZWG,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                ticker="CMCL",
                company_name="Caledonia Mining Corporation Plc",
                exchange=Exchange.VFEX,
                sector="Basic Materials",
                industry="Gold Mining",
                asset_type=AssetType.EQUITY,
                currency=Currency.USD,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                ticker="TIGZ",
                company_name="Tigere Real Estate Investment Trust",
                exchange=Exchange.ZSE,
                sector="Real Estate",
                industry="REIT",
                asset_type=AssetType.REIT,
                currency=Currency.ZWG,
                status=AssetStatus.SUSPENDED,
            ),
        ]
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_list_assets_filters_by_exchange_and_status(db_session: Session) -> None:
    """Service applies enum filters and returns total count."""
    assets, total = list_assets(
        db_session,
        exchange=Exchange.ZSE,
        status=AssetStatus.ACTIVE,
        page=1,
        limit=20,
    )

    assert total == 2
    assert [asset.ticker for asset in assets] == ["DLTA", "ECO"]


def test_list_assets_filters_by_asset_type_and_sector(db_session: Session) -> None:
    """Service supports asset type and case-insensitive sector filtering."""
    assets, total = list_assets(
        db_session,
        asset_type=AssetType.REIT,
        sector="real estate",
        page=1,
        limit=20,
    )

    assert total == 1
    assert assets[0].ticker == "TIGZ"


def test_list_assets_filters_by_search_and_paginates(db_session: Session) -> None:
    """Service supports search query and pagination."""
    assets, total = list_assets(
        db_session,
        search="limited",
        page=1,
        limit=1,
    )

    assert total == 2
    assert len(assets) == 1
    assert assets[0].ticker == "DLTA"


def test_get_asset_by_ticker_is_case_insensitive(db_session: Session) -> None:
    """Ticker lookup normalizes user input."""
    asset = get_asset_by_ticker(db_session, " cmcl ")

    assert asset is not None
    assert asset.company_name == "Caledonia Mining Corporation Plc"
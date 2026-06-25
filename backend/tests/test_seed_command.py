"""Manual seed command tests."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.seed import normalize_seed_asset, seed_development_assets
from app.database.seed_assets import SEED_ASSETS
from app.models.asset import Asset


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an in-memory database session for seed tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Asset.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_seed_asset_shape_contains_required_model_fields() -> None:
    """Seed assets contain the fields needed by the Asset model."""
    required_fields = {
        "ticker",
        "company_name",
        "exchange",
        "sector",
        "industry",
        "asset_type",
        "currency",
        "description",
        "logo_url",
        "official_website",
        "market_cap",
        "listing_date",
        "status",
    }

    for seed_asset in SEED_ASSETS:
        assert required_fields.issubset(seed_asset.keys())
        assert seed_asset["ticker"]
        assert seed_asset["company_name"]


def test_normalize_seed_asset_uppercases_ticker() -> None:
    """Seed normalization produces consistent ticker keys."""
    normalized = normalize_seed_asset({"ticker": " dlta "})

    assert normalized["ticker"] == "DLTA"


def test_seed_development_assets_inserts_assets(db_session: Session) -> None:
    """Seed command inserts missing assets and reports them."""
    seed_assets = [SEED_ASSETS[0], SEED_ASSETS[1]]

    result = seed_development_assets(db_session, seed_assets)
    tickers = set(db_session.scalars(select(Asset.ticker)).all())

    assert result.inserted == 2
    assert result.skipped == 0
    assert result.inserted_tickers == ["DLTA", "ECO"]
    assert result.skipped_tickers == []
    assert tickers == {"DLTA", "ECO"}


def test_seed_development_assets_skips_duplicate_tickers(db_session: Session) -> None:
    """Seed command is duplicate-aware and safe to run repeatedly."""
    seed_assets = [SEED_ASSETS[0], SEED_ASSETS[1]]

    first_result = seed_development_assets(db_session, seed_assets)
    second_result = seed_development_assets(db_session, seed_assets)
    asset_count = len(db_session.scalars(select(Asset)).all())

    assert first_result.inserted == 2
    assert second_result.inserted == 0
    assert second_result.skipped == 2
    assert second_result.skipped_tickers == ["DLTA", "ECO"]
    assert asset_count == 2
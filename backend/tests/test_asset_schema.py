"""Asset schema validation tests."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.asset import AssetStatus, AssetType, Currency, Exchange
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate


def test_asset_create_validates_and_normalizes_ticker() -> None:
    """Asset creation schema validates enums and normalizes ticker symbols."""
    asset = AssetCreate(
        ticker=" dlta ",
        company_name="Delta Corporation Limited",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        market_cap=Decimal("0"),
    )

    assert asset.ticker == "DLTA"
    assert asset.status == AssetStatus.ACTIVE


def test_asset_create_rejects_invalid_enum_value() -> None:
    """Unsupported exchanges are rejected before persistence."""
    with pytest.raises(ValidationError):
        AssetCreate(
            ticker="BAD",
            company_name="Unsupported Exchange Asset",
            exchange="JSE",
            asset_type=AssetType.EQUITY,
            currency=Currency.USD,
        )


def test_asset_update_allows_partial_updates() -> None:
    """Update schema supports PATCH-style partial data."""
    update = AssetUpdate(ticker=" eco ", status=AssetStatus.SUSPENDED)

    assert update.ticker == "ECO"
    assert update.status == AssetStatus.SUSPENDED


def test_asset_read_supports_from_attributes_shape() -> None:
    """Read schema carries persisted fields and timestamps."""
    now = datetime.now(UTC)
    asset = AssetRead(
        id=1,
        ticker="CBZ",
        company_name="CBZ Holdings Limited",
        exchange=Exchange.ZSE,
        sector="Financial Services",
        industry="Banking",
        asset_type=AssetType.EQUITY,
        currency=Currency.ZWG,
        status=AssetStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    assert asset.id == 1
    assert asset.ticker == "CBZ"
    assert asset.created_at == now
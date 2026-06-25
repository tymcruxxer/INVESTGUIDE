"""Development asset seed data tests."""

from app.database.seed_assets import SEED_ASSETS
from app.models.asset import AssetStatus, AssetType, Currency, Exchange


def test_seed_assets_include_initial_development_universe() -> None:
    """Seed data contains the requested Zimbabwean asset examples."""
    tickers = {asset["ticker"] for asset in SEED_ASSETS}

    assert tickers == {
        "DLTA",
        "ECO",
        "CBZ",
        "INN",
        "TIGZ",
        "FMCREIT",
        "SCIL",
        "CMCL",
        "PHL",
    }


def test_seed_assets_use_allowed_domain_values() -> None:
    """Seed data stays aligned with model enum value sets."""
    exchanges = {item.value for item in Exchange}
    asset_types = {item.value for item in AssetType}
    currencies = {item.value for item in Currency}
    statuses = {item.value for item in AssetStatus}

    for asset in SEED_ASSETS:
        assert asset["exchange"] in exchanges
        assert asset["asset_type"] in asset_types
        assert asset["currency"] in currencies
        assert asset["status"] in statuses
        assert asset["market_cap"] is None
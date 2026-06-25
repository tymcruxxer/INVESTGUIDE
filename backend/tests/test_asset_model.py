"""Asset model metadata tests."""

from sqlalchemy import CheckConstraint, Index, UniqueConstraint, inspect

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange


def test_asset_model_columns_match_domain_contract() -> None:
    """Asset model exposes the fields required for the data foundation."""
    columns = inspect(Asset).columns

    expected_columns = {
        "id",
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
        "created_at",
        "updated_at",
    }

    assert set(columns.keys()) == expected_columns
    assert columns.ticker.nullable is False
    assert columns.company_name.nullable is False
    assert columns.status.default is not None
    assert columns.status.server_default is not None


def test_asset_model_constraints_and_indexes_are_registered() -> None:
    """Asset metadata is ready for deterministic Alembic migrations."""
    table = Asset.__table__
    unique_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    check_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    index_names = {index.name for index in table.indexes if isinstance(index, Index)}

    assert "uq_assets_ticker" in unique_names
    assert {"ck_assets_asset_exchange", "ck_assets_asset_type", "ck_assets_asset_currency", "ck_assets_asset_status"}.issubset(
        check_names
    )
    assert {
        "ix_assets_ticker",
        "ix_assets_exchange",
        "ix_assets_sector",
        "ix_assets_asset_type",
    }.issubset(index_names)


def test_asset_allowed_values_are_explicit() -> None:
    """Domain value sets are explicit for future validation and APIs."""
    assert {item.value for item in Exchange} == {"ZSE", "VFEX"}
    assert {item.value for item in AssetType} == {
        "equity",
        "REIT",
        "bond",
        "money_market",
        "alternative",
    }
    assert {item.value for item in Currency} == {"ZWG", "USD"}
    assert {item.value for item in AssetStatus} == {"active", "suspended", "delisted"}
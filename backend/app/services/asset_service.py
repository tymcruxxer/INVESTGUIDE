"""Read-only asset service functions."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus, AssetType, Exchange


def list_assets(
    db: Session,
    *,
    exchange: Exchange | None = None,
    sector: str | None = None,
    asset_type: AssetType | None = None,
    status: AssetStatus | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Asset], int]:
    """Return paginated assets matching optional filters."""
    filters = []

    if exchange is not None:
        filters.append(Asset.exchange == exchange)
    if sector:
        filters.append(func.lower(Asset.sector) == sector.strip().lower())
    if asset_type is not None:
        filters.append(Asset.asset_type == asset_type)
    if status is not None:
        filters.append(Asset.status == status)
    if search:
        normalized_search = f"%{search.strip()}%"
        filters.append(
            or_(
                Asset.ticker.ilike(normalized_search),
                Asset.company_name.ilike(normalized_search),
                Asset.sector.ilike(normalized_search),
                Asset.industry.ilike(normalized_search),
            )
        )

    offset = (page - 1) * limit
    total_query = select(func.count()).select_from(Asset).where(*filters)
    assets_query = (
        select(Asset)
        .where(*filters)
        .order_by(Asset.ticker.asc())
        .offset(offset)
        .limit(limit)
    )

    total = db.scalar(total_query) or 0
    assets = list(db.scalars(assets_query).all())

    return assets, total


def get_asset_by_ticker(db: Session, ticker: str) -> Asset | None:
    """Return one asset by ticker, case-insensitively."""
    normalized_ticker = ticker.strip().upper()
    query = select(Asset).where(func.upper(Asset.ticker) == normalized_ticker)
    return db.scalar(query)
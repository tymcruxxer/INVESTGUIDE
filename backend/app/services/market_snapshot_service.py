"""Market snapshot retrieval helpers with fixture isolation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.development_data_guard import get_development_data_policy
from app.models.asset import Asset
from app.models.market_snapshot import MarketSnapshot


def get_latest_asset_snapshot(db: Session, asset: Asset) -> MarketSnapshot | None:
    """Return the latest acceptable market snapshot for one asset."""
    try:
        rows = list(
            db.scalars(
                select(MarketSnapshot)
                .where(MarketSnapshot.asset_id == asset.id)
                .order_by(MarketSnapshot.snapshot_date.desc(), MarketSnapshot.id.desc())
            ).all()
        )
    except SQLAlchemyError:
        db.rollback()
        return None
    if not rows:
        return None

    verified_rows = [row for row in rows if not row.is_development_data]
    if verified_rows:
        return verified_rows[0]

    if get_development_data_policy().permits_fixtures:
        return rows[0]
    return None


def get_latest_company_reference_snapshot(db: Session, company_id: int) -> MarketSnapshot | None:
    """Return the latest acceptable snapshot across a company's listed assets."""
    assets = list(db.scalars(select(Asset).where(Asset.company_id == company_id)).all())
    snapshots = [snapshot for asset in assets if (snapshot := get_latest_asset_snapshot(db, asset)) is not None]
    return max(snapshots, key=lambda row: (row.snapshot_date, row.id)) if snapshots else None

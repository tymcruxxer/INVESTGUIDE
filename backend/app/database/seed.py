"""Manual development database seed command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.seed_assets import SEED_ASSETS
from app.database.session import SessionLocal
from app.models.asset import Asset

logger = get_logger(__name__)


@dataclass(frozen=True)
class SeedResult:
    """Summary of a seed execution."""

    inserted: int
    skipped: int
    inserted_tickers: list[str]
    skipped_tickers: list[str]


def normalize_seed_asset(seed_asset: dict[str, object]) -> dict[str, object]:
    """Normalize one seed asset before persistence."""
    normalized = dict(seed_asset)
    normalized["ticker"] = str(normalized["ticker"]).strip().upper()
    return normalized


def seed_development_assets(
    db: Session,
    seed_assets: Iterable[dict[str, object]] = SEED_ASSETS,
) -> SeedResult:
    """Insert development assets while skipping existing tickers."""
    normalized_assets = [normalize_seed_asset(asset) for asset in seed_assets]
    tickers = [str(asset["ticker"]) for asset in normalized_assets]

    existing_tickers = set(
        db.scalars(select(Asset.ticker).where(Asset.ticker.in_(tickers))).all()
    )

    inserted_tickers: list[str] = []
    skipped_tickers: list[str] = []

    for asset_data in normalized_assets:
        ticker = str(asset_data["ticker"])
        if ticker in existing_tickers:
            skipped_tickers.append(ticker)
            logger.info("Skipping existing asset seed: %s", ticker)
            continue

        db.add(Asset(**asset_data))
        inserted_tickers.append(ticker)
        logger.info("Queued asset seed insert: %s", ticker)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Asset seed failed; transaction rolled back")
        raise

    logger.info(
        "Asset seed completed: %s inserted, %s skipped",
        len(inserted_tickers),
        len(skipped_tickers),
    )
    return SeedResult(
        inserted=len(inserted_tickers),
        skipped=len(skipped_tickers),
        inserted_tickers=inserted_tickers,
        skipped_tickers=skipped_tickers,
    )


def main() -> None:
    """Run the manual development seed command."""
    logger.info("Starting manual development asset seed")
    with SessionLocal() as db:
        result = seed_development_assets(db)
    logger.info(
        "Manual development asset seed finished: %s inserted, %s skipped",
        result.inserted,
        result.skipped,
    )


if __name__ == "__main__":
    main()
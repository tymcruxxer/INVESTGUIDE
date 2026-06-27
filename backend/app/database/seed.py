"""Manual development database seed command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.seed_assets import SEED_ASSETS
from app.database.seed_investor_profile import DEMO_INVESTOR_PROFILE
from app.database.session import SessionLocal
from app.models.asset import Asset
from app.models.investor_profile import InvestorProfile

logger = get_logger(__name__)


@dataclass(frozen=True)
class SeedResult:
    """Summary of an asset seed execution."""

    inserted: int
    skipped: int
    inserted_tickers: list[str]
    skipped_tickers: list[str]


@dataclass(frozen=True)
class InvestorProfileSeedResult:
    """Summary of a development investor profile seed execution."""

    inserted: int
    skipped: int
    profile_id: int | None


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


def seed_development_investor_profile(
    db: Session,
    profile_data: dict[str, object] = DEMO_INVESTOR_PROFILE,
) -> InvestorProfileSeedResult:
    """Insert one demo investor profile if no profile exists yet."""
    existing_count = db.scalar(select(func.count()).select_from(InvestorProfile)) or 0
    if existing_count > 0:
        existing_profile = db.scalars(select(InvestorProfile).order_by(InvestorProfile.id.asc())).first()
        logger.info("Skipping investor profile seed; profile already exists")
        return InvestorProfileSeedResult(
            inserted=0,
            skipped=1,
            profile_id=existing_profile.id if existing_profile else None,
        )

    profile = InvestorProfile(**dict(profile_data))
    db.add(profile)

    try:
        db.commit()
        db.refresh(profile)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Investor profile seed failed; transaction rolled back")
        raise

    logger.info("Investor profile seed completed: profile %s inserted", profile.id)
    return InvestorProfileSeedResult(inserted=1, skipped=0, profile_id=profile.id)


def main() -> None:
    """Run the manual development seed command."""
    logger.info("Starting manual development seed")
    with SessionLocal() as db:
        asset_result = seed_development_assets(db)
        profile_result = seed_development_investor_profile(db)
    logger.info(
        "Manual development seed finished: %s assets inserted, %s assets skipped, "
        "%s profiles inserted, %s profiles skipped",
        asset_result.inserted,
        asset_result.skipped,
        profile_result.inserted,
        profile_result.skipped,
    )


if __name__ == "__main__":
    main()

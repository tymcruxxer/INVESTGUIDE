"""Manual development database seed command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.database.seed_assets import SEED_ASSETS
from app.database.seed_investor_profile import DEMO_INVESTOR_PROFILE
from app.database.session import SessionLocal
from app.models.asset import Asset
from app.models.company import Company
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


@dataclass(frozen=True)
class CompanySeedResult:
    """Summary of a development company seed execution."""

    inserted: int
    updated: int
    skipped: int
    linked_assets: int


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
    ensure_development_data_allowed()
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


def _company_data_from_asset(asset: Asset) -> dict[str, object]:
    """Build issuer-level company seed data from a listed asset."""
    return {
        "name": asset.company_name,
        "legal_name": asset.company_name,
        "ticker": asset.ticker.strip().upper(),
        "exchange": asset.exchange,
        "sector": asset.sector,
        "industry": asset.industry,
        "country": "Zimbabwe",
        "website": asset.official_website,
        "description": asset.description,
        "market": asset.exchange,
        "currency": asset.currency,
        "status": asset.status,
        "logo_url": asset.logo_url,
    }


def seed_development_companies(db: Session) -> CompanySeedResult:
    """Create or update issuer records from seeded assets and link assets to them."""
    ensure_development_data_allowed()
    assets = list(db.scalars(select(Asset).order_by(Asset.ticker.asc())).all())
    inserted = 0
    updated = 0
    skipped = 0
    linked_assets = 0

    for asset in assets:
        seed_data = _company_data_from_asset(asset)
        ticker = str(seed_data["ticker"])
        company = db.scalar(select(Company).where(func.upper(Company.ticker) == ticker))

        if company is None:
            company = Company(**seed_data)
            db.add(company)
            db.flush()
            inserted += 1
            logger.info("Queued company seed insert: %s", ticker)
        else:
            changed = False
            for field, value in seed_data.items():
                current_value = getattr(company, field)
                if current_value in (None, "", []) and value not in (None, "", []):
                    setattr(company, field, value)
                    changed = True
            if changed:
                updated += 1
                logger.info("Queued company seed update: %s", ticker)
            else:
                skipped += 1
                logger.info("Skipping existing company seed: %s", ticker)

        if asset.company_id != company.id:
            asset.company_id = company.id
            linked_assets += 1
            logger.info("Linked asset %s to company %s", asset.ticker, ticker)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Company seed failed; transaction rolled back")
        raise

    logger.info(
        "Company seed completed: %s inserted, %s updated, %s skipped, %s assets linked",
        inserted,
        updated,
        skipped,
        linked_assets,
    )
    return CompanySeedResult(
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        linked_assets=linked_assets,
    )


def seed_development_investor_profile(
    db: Session,
    profile_data: dict[str, object] = DEMO_INVESTOR_PROFILE,
) -> InvestorProfileSeedResult:
    """Insert one demo investor profile if no profile exists yet."""
    ensure_development_data_allowed()
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
    ensure_development_data_allowed()
    logger.info("Starting manual development seed")
    with SessionLocal() as db:
        asset_result = seed_development_assets(db)
        company_result = seed_development_companies(db)
        from app.database.seed_company_profiles import seed_company_profiles
        from app.database.seed_financial_statements import seed_financial_statements
        from app.database.seed_dividends import seed_dividends

        company_profile_result = seed_company_profiles(db)
        financial_result = seed_financial_statements(db)
        dividend_result = seed_dividends(db)
        profile_result = seed_development_investor_profile(db)
    logger.info(
        "Manual development seed finished: %s assets inserted, %s assets skipped, "
        "%s companies inserted, %s companies updated, %s companies skipped, "
        "%s company profiles inserted, %s company profiles updated, %s company profiles skipped, "
        "%s financial statement rows inserted, %s financial statement rows updated, %s financial statement rows skipped, "
        "%s dividend rows inserted, %s dividend rows updated, %s dividend rows skipped, "
        "%s investor profiles inserted, %s investor profiles skipped",
        asset_result.inserted,
        asset_result.skipped,
        company_result.inserted,
        company_result.updated,
        company_result.skipped,
        company_profile_result.inserted,
        company_profile_result.updated,
        company_profile_result.skipped,
        financial_result.inserted,
        financial_result.updated,
        financial_result.skipped,
        dividend_result.inserted,
        dividend_result.updated,
        dividend_result.skipped,
        profile_result.inserted,
        profile_result.skipped,
    )


if __name__ == "__main__":
    main()





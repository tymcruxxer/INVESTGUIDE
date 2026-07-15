"""Manual development seed runner for dividend fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.database.session import SessionLocal
from app.models.asset import Asset
from app.models.company import Company
from app.models.dividend import Dividend, DividendType

logger = get_logger(__name__)

SOURCE_NAME = "InvestGuide development dividend fixture data"

DIVIDEND_FIXTURES: dict[str, list[dict[str, Any]]] = {
    "DLTA": [
        {
            "announcement_date": date(2024, 6, 14),
            "record_date": date(2024, 7, 5),
            "ex_dividend_date": date(2024, 7, 3),
            "payment_date": date(2024, 7, 26),
            "fiscal_year": 2024,
            "dividend_type": DividendType.FINAL,
            "dividend_per_share": 0.021,
            "currency": "USD",
            "shares_outstanding": None,
            "total_dividend_amount": 27_000_000,
        },
        {
            "announcement_date": date(2023, 11, 17),
            "record_date": date(2023, 12, 8),
            "ex_dividend_date": date(2023, 12, 6),
            "payment_date": date(2023, 12, 29),
            "fiscal_year": 2023,
            "dividend_type": DividendType.INTERIM,
            "dividend_per_share": 0.014,
            "currency": "USD",
            "shares_outstanding": None,
            "total_dividend_amount": 18_000_000,
        },
    ]
}


@dataclass(frozen=True)
class DividendSeedResult:
    """Summary of a dividend seed execution."""

    inserted: int
    updated: int
    skipped: int
    missing_companies: list[str]


def seed_dividends(db: Session, fixtures: dict[str, list[dict[str, Any]]] = DIVIDEND_FIXTURES) -> DividendSeedResult:
    """Seed clearly marked development dividends without duplicate rows."""
    ensure_development_data_allowed()
    inserted = 0
    updated = 0
    skipped = 0
    missing_companies: list[str] = []

    try:
        for ticker, records in sorted(fixtures.items()):
            company = db.scalar(select(Company).where(func.upper(Company.ticker) == ticker.upper()))
            if company is None:
                missing_companies.append(ticker)
                skipped += len(records)
                logger.warning("Skipping dividend seed; company %s is missing", ticker)
                continue

            asset = db.scalar(select(Asset).where(func.upper(Asset.ticker) == ticker.upper()))
            for record in records:
                payload = {
                    **record,
                    "company_id": company.id,
                    "asset_id": asset.id if asset else None,
                    "source_name": SOURCE_NAME,
                    "source_type": "development_fixture",
                    "source_url": None,
                    "imported_at": datetime.now(UTC),
                    "verified_at": None,
                    "is_development_data": True,
                }
                result = _upsert_dividend(db, payload)
                inserted += 1 if result == "inserted" else 0
                updated += 1 if result == "updated" else 0
                skipped += 1 if result == "skipped" else 0
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Dividend seed failed; transaction rolled back")
        raise

    logger.info(
        "Dividend seed completed: %s inserted, %s updated, %s skipped, %s missing companies",
        inserted,
        updated,
        skipped,
        len(missing_companies),
    )
    return DividendSeedResult(inserted=inserted, updated=updated, skipped=skipped, missing_companies=missing_companies)


def _upsert_dividend(db: Session, payload: dict[str, Any]) -> str:
    existing = db.scalar(
        select(Dividend).where(
            Dividend.company_id == payload["company_id"],
            Dividend.asset_id == payload["asset_id"],
            Dividend.fiscal_year == payload["fiscal_year"],
            Dividend.dividend_type == payload["dividend_type"],
            Dividend.announcement_date == payload["announcement_date"],
        )
    )
    if existing is None:
        db.add(Dividend(**payload))
        return "inserted"

    if not existing.is_development_data:
        return "skipped"

    changed = False
    for field, value in payload.items():
        if getattr(existing, field) != value:
            setattr(existing, field, value)
            changed = True
    return "updated" if changed else "skipped"


def main() -> None:
    """Run dividend seeding as an explicit manual command."""
    ensure_development_data_allowed()
    logger.info("Starting manual dividend seed")
    with SessionLocal() as db:
        result = seed_dividends(db)
    logger.info(
        "Manual dividend seed finished: %s inserted, %s updated, %s skipped",
        result.inserted,
        result.updated,
        result.skipped,
    )


if __name__ == "__main__":
    main()

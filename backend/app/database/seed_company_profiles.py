"""Manual development seed runner for persisted company profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.company_profile_seed import COMPANY_PROFILE_FIXTURES
from app.database.session import SessionLocal
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.services.company_enrichment import apply_enrichment, build_company_profile_from_fixture
from app.services.company_profile_service import get_company_profile

logger = get_logger(__name__)

PROFILE_FIELDS = (
    "business_summary",
    "primary_business",
    "products_services",
    "industry",
    "sub_industry",
    "headquarters",
    "founded_year",
    "website",
    "email",
    "phone",
    "country",
    "exchange",
    "currency",
    "employees",
    "status",
    "research_status",
    "last_verified",
    "source_name",
    "source_url",
)


@dataclass(frozen=True)
class CompanyProfileSeedResult:
    """Summary of a company profile seed execution."""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    missing_companies: list[str] = field(default_factory=list)


def _snapshot_value(value: Any) -> Any:
    """Normalize values that can round-trip differently by database dialect."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None).isoformat(timespec="seconds")
    return value


def _profile_snapshot(profile: CompanyProfile) -> dict[str, Any]:
    """Return comparable profile field values before/after enrichment."""
    return {field_name: _snapshot_value(getattr(profile, field_name)) for field_name in PROFILE_FIELDS}


def _find_company_by_ticker(db: Session, ticker: str) -> Company | None:
    """Return a company by ticker using the canonical uppercase key."""
    normalized_ticker = ticker.strip().upper()
    return db.scalar(select(Company).where(func.upper(Company.ticker) == normalized_ticker))


def seed_company_profiles(
    db: Session,
    fixtures: dict[str, dict[str, Any]] = COMPANY_PROFILE_FIXTURES,
) -> CompanyProfileSeedResult:
    """Seed development company profiles without overwriting verified research."""
    inserted = 0
    updated = 0
    skipped = 0
    missing_companies: list[str] = []

    try:
        for ticker in sorted(fixtures):
            company = _find_company_by_ticker(db, ticker)
            if company is None:
                missing_companies.append(ticker)
                skipped += 1
                logger.warning("Skipping company profile seed; company %s is missing", ticker)
                continue

            incoming = build_company_profile_from_fixture(company)
            existing = get_company_profile(db, company)
            if existing is None:
                db.add(incoming)
                inserted += 1
                logger.info("Queued company profile seed insert: %s", ticker)
                continue

            before = _profile_snapshot(existing)
            apply_enrichment(existing, incoming)
            after = _profile_snapshot(existing)
            if after != before:
                updated += 1
                logger.info("Queued company profile seed update: %s", ticker)
            else:
                skipped += 1
                logger.info("Skipping unchanged company profile seed: %s", ticker)

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Company profile seed failed; transaction rolled back")
        raise

    logger.info(
        "Company profile seed completed: %s inserted, %s updated, %s skipped, %s missing companies",
        inserted,
        updated,
        skipped,
        len(missing_companies),
    )
    return CompanyProfileSeedResult(
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        missing_companies=missing_companies,
    )


def main() -> None:
    """Run company profile seeding as an explicit manual command."""
    logger.info("Starting manual company profile seed")
    with SessionLocal() as db:
        result = seed_company_profiles(db)
    logger.info(
        "Manual company profile seed finished: %s inserted, %s updated, %s skipped",
        result.inserted,
        result.updated,
        result.skipped,
    )


if __name__ == "__main__":
    main()

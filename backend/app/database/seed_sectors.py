"""Manual development seed data for sectors and industries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.sector import Industry, Sector
from app.services.sector_service import slugify

logger = get_logger(__name__)


@dataclass(frozen=True)
class SectorSeedResult:
    """Summary for sector and industry seed execution."""

    inserted: int
    updated: int
    skipped: int
    industries_inserted: int
    industries_updated: int
    industries_skipped: int


SEED_SECTORS: list[dict[str, Any]] = [
    {
        "name": "Consumer Staples",
        "description": "Companies that provide everyday goods such as food, beverages, agriculture inputs, and household essentials.",
        "overview": "Consumer Staples sectors are studied because demand can be more resilient than discretionary categories, but margins still depend on inflation, input costs, and consumer purchasing power.",
        "industries": [
            {"name": "Beverages", "description": "Companies that produce, distribute, or sell drinks through retail and hospitality channels."},
            {"name": "Food Production and Distribution", "description": "Companies that manufacture or distribute food and fast-moving consumer goods."},
            {"name": "Agriculture and Seed Production", "description": "Businesses connected to seed, agriculture production, and crop cycles."},
            {"name": "Agriculture and Export Operations", "description": "Agriculture businesses with export or foreign-currency operating exposure."},
        ],
    },
    {
        "name": "Financial Services",
        "description": "Banks and finance businesses that handle deposits, lending, transactions, insurance, or capital-market services.",
        "overview": "Financial Services are studied because interest rates, credit quality, regulation, and economic activity can strongly affect earnings and risk.",
        "industries": [{"name": "Banking", "description": "Banks earn from lending, transaction services, deposits, and financial products."}],
    },
    {
        "name": "Telecommunications",
        "description": "Connectivity and digital service businesses that operate networks, mobile services, and related platforms.",
        "overview": "Telecommunications sectors are studied because they combine recurring usage, infrastructure investment, regulation, and digital-service growth.",
        "industries": [{"name": "Mobile Telecommunications", "description": "Mobile network operators and businesses providing connectivity services."}],
    },
    {
        "name": "Real Estate",
        "description": "Property-owning or property-income businesses, including listed real estate investment trusts.",
        "overview": "Real Estate is studied because property income, tenant quality, interest rates, and occupancy shape long-term income resilience.",
        "industries": [{"name": "REIT", "description": "Real Estate Investment Trusts own income-producing property and may distribute rental income."}],
    },
    {
        "name": "Basic Materials",
        "description": "Companies exposed to commodities, mining, raw materials, and production inputs.",
        "overview": "Basic Materials sectors are studied because commodity prices, costs, production reliability, and foreign-currency earnings can materially affect results.",
        "industries": [{"name": "Gold Mining", "description": "Mining companies whose revenue and costs are connected to gold production and commodity prices."}],
    },
]


def seed_sectors(db: Session, sectors: list[dict[str, Any]] = SEED_SECTORS) -> SectorSeedResult:
    """Seed development sector and industry reference data without duplicates."""
    ensure_development_data_allowed()
    now = datetime.now(UTC)
    inserted = updated = skipped = 0
    industries_inserted = industries_updated = industries_skipped = 0

    try:
        for sector_data in sectors:
            sector_slug = slugify(sector_data["name"])
            sector = db.scalar(select(Sector).where(Sector.slug == sector_slug))
            values = {
                "name": sector_data["name"],
                "slug": sector_slug,
                "description": sector_data.get("description"),
                "exchange_coverage": "ZSE, VFEX",
                "country": "Zimbabwe",
                "overview": sector_data.get("overview"),
                "source_name": "InvestGuide Development Sector Fixture",
                "source_type": "DEVELOPMENT_FIXTURE",
                "source_url": None,
                "imported_at": now,
                "verification_status": "Development",
                "dataset_version": "sector-fixtures-v1",
                "external_key": f"development-sector-{sector_slug}",
                "is_development_data": True,
            }
            if sector is None:
                sector = Sector(**values)
                db.add(sector)
                db.flush()
                inserted += 1
            elif not sector.is_development_data:
                skipped += 1
            else:
                changed = _update_if_changed(sector, values)
                updated += 1 if changed else 0
                skipped += 0 if changed else 1

            for industry_data in sector_data.get("industries", []):
                industry_slug = slugify(industry_data["name"])
                industry = db.scalar(select(Industry).where(Industry.slug == industry_slug))
                industry_values = {
                    "sector_id": sector.id,
                    "name": industry_data["name"],
                    "slug": industry_slug,
                    "description": industry_data.get("description"),
                    "overview": industry_data.get("description"),
                    "source_name": "InvestGuide Development Industry Fixture",
                    "source_type": "DEVELOPMENT_FIXTURE",
                    "source_url": None,
                    "imported_at": now,
                    "verification_status": "Development",
                    "dataset_version": "sector-fixtures-v1",
                    "external_key": f"development-industry-{industry_slug}",
                    "is_development_data": True,
                }
                if industry is None:
                    db.add(Industry(**industry_values))
                    industries_inserted += 1
                elif not industry.is_development_data:
                    industries_skipped += 1
                else:
                    changed = _update_if_changed(industry, industry_values)
                    industries_updated += 1 if changed else 0
                    industries_skipped += 0 if changed else 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Sector seed failed; transaction rolled back")
        raise

    logger.info(
        "Sector seed completed: %s sectors inserted, %s updated, %s skipped; %s industries inserted, %s updated, %s skipped",
        inserted,
        updated,
        skipped,
        industries_inserted,
        industries_updated,
        industries_skipped,
    )
    return SectorSeedResult(inserted, updated, skipped, industries_inserted, industries_updated, industries_skipped)


def _update_if_changed(row: Any, values: dict[str, Any]) -> bool:
    changed = False
    for field, value in values.items():
        if value not in (None, "", []) and getattr(row, field) != value:
            setattr(row, field, value)
            changed = True
    return changed

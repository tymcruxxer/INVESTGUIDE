"""Read-only sector and industry service functions."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database.development_data_guard import get_development_data_policy
from app.models.company import Company
from app.models.sector import Industry, Sector


def slugify(value: str | None) -> str:
    """Return a stable URL slug for sector and industry names."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower())
    return cleaned.strip("-") or "unknown"


def list_sectors(db: Session) -> list[Sector]:
    """Return acceptable sectors with verified/non-development rows first."""
    rows = list(
        db.scalars(
            select(Sector)
            .options(selectinload(Sector.industries))
            .order_by(Sector.name.asc(), Sector.id.desc())
        ).all()
    )
    return _select_acceptable_by_slug(rows)


def get_sector_by_slug(db: Session, slug: str) -> Sector | None:
    """Return one acceptable sector by slug."""
    normalized_slug = slugify(slug)
    rows = list(
        db.scalars(
            select(Sector)
            .options(selectinload(Sector.industries))
            .where(Sector.slug == normalized_slug)
            .order_by(Sector.is_development_data.asc(), Sector.id.desc())
        ).all()
    )
    selected = _select_acceptable_by_slug(rows)
    return selected[0] if selected else None


def list_industries(db: Session) -> list[Industry]:
    """Return acceptable industries with parent sectors eager loaded."""
    rows = list(
        db.scalars(
            select(Industry)
            .options(selectinload(Industry.sector))
            .order_by(Industry.name.asc(), Industry.id.desc())
        ).all()
    )
    return _select_acceptable_by_slug(rows)


def get_industry_by_slug(db: Session, slug: str) -> Industry | None:
    """Return one acceptable industry by slug."""
    normalized_slug = slugify(slug)
    rows = list(
        db.scalars(
            select(Industry)
            .options(selectinload(Industry.sector))
            .where(Industry.slug == normalized_slug)
            .order_by(Industry.is_development_data.asc(), Industry.id.desc())
        ).all()
    )
    selected = _select_acceptable_by_slug(rows)
    return selected[0] if selected else None


def companies_for_sector(db: Session, sector: Sector, limit: int = 50) -> list[Company]:
    """Return companies whose current metadata maps to this sector."""
    return list(
        db.scalars(
            select(Company)
            .where(func.lower(Company.sector) == sector.name.lower())
            .order_by(Company.name.asc())
            .limit(limit)
        ).all()
    )


def companies_for_industry(db: Session, industry: Industry, limit: int = 50) -> list[Company]:
    """Return companies whose current metadata maps to this industry."""
    normalized = industry.name.lower()
    return list(
        db.scalars(
            select(Company)
            .where(func.lower(Company.industry).contains(normalized))
            .order_by(Company.name.asc())
            .limit(limit)
        ).all()
    )


def serialize_sector(sector: Sector) -> dict[str, Any]:
    """Serialize a sector with provenance and industry summaries."""
    return {
        "id": sector.id,
        "name": sector.name,
        "slug": sector.slug,
        "description": sector.description,
        "exchange_coverage": sector.exchange_coverage,
        "country": sector.country,
        "overview": sector.overview,
        "source_name": sector.source_name,
        "source_type": sector.source_type,
        "source_url": sector.source_url,
        "imported_at": sector.imported_at.isoformat() if sector.imported_at else None,
        "verified_at": sector.verified_at.isoformat() if sector.verified_at else None,
        "verification_status": sector.verification_status,
        "dataset_version": sector.dataset_version,
        "is_development_data": sector.is_development_data,
        "data_origin": "Development Preview" if sector.is_development_data else "Persisted Backend",
        "created_at": sector.created_at.isoformat() if sector.created_at else None,
        "updated_at": sector.updated_at.isoformat() if sector.updated_at else None,
        "industries": [serialize_industry_summary(industry) for industry in sorted(sector.industries, key=lambda item: item.name)],
    }


def serialize_industry(industry: Industry) -> dict[str, Any]:
    """Serialize an industry with parent sector and provenance."""
    payload = serialize_industry_summary(industry)
    payload.update(
        {
            "id": industry.id,
            "sector": serialize_sector_summary(industry.sector),
            "description": industry.description,
            "overview": industry.overview,
            "source_name": industry.source_name,
            "source_type": industry.source_type,
            "source_url": industry.source_url,
            "imported_at": industry.imported_at.isoformat() if industry.imported_at else None,
            "verified_at": industry.verified_at.isoformat() if industry.verified_at else None,
            "verification_status": industry.verification_status,
            "dataset_version": industry.dataset_version,
            "is_development_data": industry.is_development_data,
            "data_origin": "Development Preview" if industry.is_development_data else "Persisted Backend",
            "created_at": industry.created_at.isoformat() if industry.created_at else None,
            "updated_at": industry.updated_at.isoformat() if industry.updated_at else None,
        }
    )
    return payload


def serialize_sector_summary(sector: Sector) -> dict[str, Any]:
    return {
        "id": sector.id,
        "name": sector.name,
        "slug": sector.slug,
        "description": sector.description,
        "country": sector.country,
        "data_origin": "Development Preview" if sector.is_development_data else "Persisted Backend",
    }


def serialize_industry_summary(industry: Industry) -> dict[str, Any]:
    return {
        "id": industry.id,
        "name": industry.name,
        "slug": industry.slug,
        "description": industry.description,
        "sector_id": industry.sector_id,
        "data_origin": "Development Preview" if industry.is_development_data else "Persisted Backend",
    }


def _select_acceptable_by_slug[T: Any](rows: Iterable[T]) -> list[T]:
    policy = get_development_data_policy()
    grouped: dict[str, list[T]] = defaultdict(list)
    for row in rows:
        grouped[getattr(row, "slug")].append(row)

    selected: list[T] = []
    for group_rows in grouped.values():
        verified = [row for row in group_rows if not getattr(row, "is_development_data")]
        if verified:
            selected.append(max(verified, key=lambda item: getattr(item, "id") or 0))
        elif policy.permits_fixtures:
            selected.append(max(group_rows, key=lambda item: getattr(item, "id") or 0))
    return sorted(selected, key=lambda item: getattr(item, "name"))

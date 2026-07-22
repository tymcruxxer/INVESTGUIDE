"""Read-only Sector Intelligence endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.services import sector_service
from app.services.intelligence.sector_engine import build_sector_research

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("", response_model=None)
async def list_sectors(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return persisted sectors with provenance metadata."""
    sectors = sector_service.list_sectors(db)
    return success_response(
        message="Sectors retrieved successfully",
        data=[sector_service.serialize_sector(sector) for sector in sectors],
        meta={"total": len(sectors)},
    )


@router.get("/{slug}", response_model=None)
async def get_sector(slug: str, db: Session = Depends(get_db)):
    """Return one sector, its industries, and related companies."""
    sector = sector_service.get_sector_by_slug(db, slug)
    if sector is None:
        return JSONResponse(
            status_code=404,
            content=error_response(message=f"Sector '{slug}' was not found", error_code="SECTOR_NOT_FOUND"),
        )
    companies = sector_service.companies_for_sector(db, sector)
    return success_response(
        message="Sector retrieved successfully",
        data={
            "sector": sector_service.serialize_sector(sector),
            "companies": [
                {
                    "ticker": company.ticker,
                    "name": company.name,
                    "sector": company.sector,
                    "industry": company.industry,
                    "exchange": company.exchange.value if hasattr(company.exchange, "value") else company.exchange,
                    "href": f"/company/{company.ticker.lower()}",
                    "reason": f"Listed because its sector is recorded as {company.sector}.",
                }
                for company in companies
            ],
            "industry_count": len(sector.industries),
            "company_count": len(companies),
        },
    )


@router.get("/{slug}/research", response_model=None)
async def get_sector_research(slug: str, db: Session = Depends(get_db)):
    """Return deterministic research for one sector."""
    sector = sector_service.get_sector_by_slug(db, slug)
    if sector is None:
        return JSONResponse(
            status_code=404,
            content=error_response(message=f"Sector '{slug}' was not found", error_code="SECTOR_NOT_FOUND"),
        )
    companies = sector_service.companies_for_sector(db, sector)
    return success_response(
        message="Sector research retrieved successfully",
        data=build_sector_research(sector, companies),
    )

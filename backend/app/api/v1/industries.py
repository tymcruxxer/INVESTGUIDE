"""Read-only Industry Intelligence endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.services import sector_service
from app.services.intelligence.sector_engine import build_industry_research

router = APIRouter(prefix="/industries", tags=["industries"])


@router.get("", response_model=None)
async def list_industries(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return persisted industries with parent sector metadata."""
    industries = sector_service.list_industries(db)
    return success_response(
        message="Industries retrieved successfully",
        data=[sector_service.serialize_industry(industry) for industry in industries],
        meta={"total": len(industries)},
    )


@router.get("/{slug}", response_model=None)
async def get_industry(slug: str, db: Session = Depends(get_db)):
    """Return one persisted industry with parent sector metadata."""
    industry = sector_service.get_industry_by_slug(db, slug)
    if industry is None:
        return JSONResponse(
            status_code=404,
            content=error_response(message=f"Industry '{slug}' was not found", error_code="INDUSTRY_NOT_FOUND"),
        )
    companies = sector_service.companies_for_industry(db, industry)
    payload = sector_service.serialize_industry(industry)
    payload["companies"] = [
        {
            "ticker": company.ticker,
            "name": company.name,
            "sector": company.sector,
            "industry": company.industry,
            "exchange": company.exchange.value if hasattr(company.exchange, "value") else company.exchange,
            "href": f"/company/{company.ticker.lower()}",
            "reason": f"Listed because its industry is recorded as {company.industry}.",
        }
        for company in companies
    ]
    return success_response(message="Industry retrieved successfully", data=payload)


@router.get("/{slug}/research", response_model=None)
async def get_industry_research(slug: str, db: Session = Depends(get_db)):
    """Return deterministic research for one industry."""
    industry = sector_service.get_industry_by_slug(db, slug)
    if industry is None:
        return JSONResponse(
            status_code=404,
            content=error_response(message=f"Industry '{slug}' was not found", error_code="INDUSTRY_NOT_FOUND"),
        )
    companies = sector_service.companies_for_industry(db, industry)
    return success_response(
        message="Industry research retrieved successfully",
        data=build_industry_research(industry, companies),
    )

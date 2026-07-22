"""Read-only Macro Intelligence endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.macro import MacroIndicatorType
from app.services import company_service, macro_service
from app.services.intelligence.macro_engine import (
    build_company_macro_impact,
    build_macro_overview,
    build_macro_research,
)

router = APIRouter(prefix="/macro", tags=["macro"])


def _not_found(slug: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=error_response(
            message=f"Macro indicator '{slug}' was not found",
            error_code="MACRO_INDICATOR_NOT_FOUND",
        ),
    )


def _companies(db: Session) -> list[Any]:
    companies, _total = company_service.list_companies(db, limit=200)
    return companies


@router.get("", response_model=None)
async def list_macro(db: Session = Depends(get_db)):
    """Return latest acceptable macro indicators and overview research."""
    indicators = macro_service.list_macro_indicators(db)
    return success_response(
        message="Macro indicators retrieved successfully",
        data=build_macro_overview(indicators, _companies(db)),
    )


@router.get("/company/{ticker}", response_model=None)
async def get_company_macro_impact(ticker: str, db: Session = Depends(get_db)):
    """Return deterministic macro factor explanations for one company."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(message=f"Company '{normalized}' was not found", error_code="COMPANY_NOT_FOUND"),
        )
    indicators = macro_service.list_macro_indicators(db)
    return success_response(
        message="Company macro impact retrieved successfully",
        data=build_company_macro_impact(company, indicators),
    )


@router.get("/{indicator_slug}/research", response_model=None)
async def get_macro_research(indicator_slug: str, db: Session = Depends(get_db)):
    """Return deterministic research for one macro indicator family."""
    indicator_type = macro_service.resolve_indicator_type(indicator_slug)
    if indicator_type is None:
        return _not_found(indicator_slug)
    indicators = macro_service.get_indicators_by_type(db, indicator_type)
    return success_response(
        message="Macro research retrieved successfully",
        data=build_macro_research(indicator_type, indicators, _companies(db)),
    )


@router.get("/{indicator_slug}", response_model=None)
async def get_macro_indicator(indicator_slug: str, db: Session = Depends(get_db)):
    """Return latest acceptable rows for one macro indicator family."""
    indicator_type = macro_service.resolve_indicator_type(indicator_slug)
    if indicator_type is None:
        return _not_found(indicator_slug)
    indicators = macro_service.get_indicators_by_type(db, indicator_type)
    return success_response(
        message="Macro indicator retrieved successfully",
        data={
            "indicator_type": indicator_type.value,
            "records": [macro_service.serialize_indicator(row) for row in indicators],
            "latest": macro_service.serialize_indicator(indicators[0]) if indicators else None,
            "data_origin": "Development Preview"
            if indicators and all(row.is_development_data for row in indicators)
            else ("Persisted Backend" if indicators else "Unavailable"),
        },
    )

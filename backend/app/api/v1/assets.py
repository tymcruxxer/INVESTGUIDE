"""Read-only asset endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.asset import AssetStatus, AssetType, Exchange
from app.schemas.asset import AssetRead
from app.services import asset_service
from app.services.intelligence.assessment_service import build_asset_assessment
from app.services.intelligence.research_service import build_asset_research

router = APIRouter(prefix="/assets", tags=["assets"])


def _serialize_asset(asset: Any) -> dict[str, Any]:
    """Serialize ORM-compatible asset objects into API-safe dictionaries."""
    return AssetRead.model_validate(asset).model_dump(mode="json")


@router.get("")
async def list_assets(
    exchange: Exchange | None = Query(default=None),
    sector: str | None = Query(default=None, min_length=1, max_length=100),
    asset_type: AssetType | None = Query(default=None),
    status: AssetStatus | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List assets with optional filtering and pagination."""
    assets, total = asset_service.list_assets(
        db,
        exchange=exchange,
        sector=sector,
        asset_type=asset_type,
        status=status,
        search=search,
        page=page,
        limit=limit,
    )

    return success_response(
        message="Assets retrieved successfully",
        data=[_serialize_asset(asset) for asset in assets],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": page * limit < total,
        },
    )


@router.get("/{ticker}", response_model=None)
async def get_asset(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return asset details for a ticker symbol."""
    asset = asset_service.get_asset_by_ticker(db, ticker)
    if asset is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Asset '{normalized_ticker}' was not found",
                error_code="ASSET_NOT_FOUND",
            ),
        )

    return success_response(
        message="Asset retrieved successfully",
        data=_serialize_asset(asset),
    )


@router.get("/{ticker}/research", response_model=None)
async def get_asset_research(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic AI Research for a ticker symbol."""
    asset = asset_service.get_asset_by_ticker(db, ticker)
    if asset is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Asset '{normalized_ticker}' was not found",
                error_code="ASSET_NOT_FOUND",
            ),
        )

    research_payload = build_asset_research(asset)
    return success_response(
        message="Asset research retrieved successfully",
        data=research_payload,
    )


@router.get("/{ticker}/assessment", response_model=None)
async def get_asset_assessment(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic assessment details for a ticker symbol."""
    asset = asset_service.get_asset_by_ticker(db, ticker)
    if asset is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Asset '{normalized_ticker}' was not found",
                error_code="ASSET_NOT_FOUND",
            ),
        )

    assessment_payload = build_asset_assessment(asset)
    return success_response(
        message="Asset assessment retrieved successfully",
        data=assessment_payload,
    )
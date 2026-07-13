"""Deterministic comparison endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.services import asset_service, company_service
from app.services.intelligence.comparison_engine import build_comparison

router = APIRouter(prefix="/compare", tags=["compare"])


@router.get("", response_model=None)
async def compare_subjects(
    company_a: str | None = Query(default=None, min_length=1, max_length=20),
    company_b: str | None = Query(default=None, min_length=1, max_length=20),
    asset_a: str | None = Query(default=None, min_length=1, max_length=20),
    asset_b: str | None = Query(default=None, min_length=1, max_length=20),
    db: Session = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    """Compare two companies or two assets using deterministic intelligence."""
    if company_a and company_b:
        left = company_service.get_company_by_ticker(db, company_a)
        right = company_service.get_company_by_ticker(db, company_b)
        subject_type = "company"
    elif asset_a and asset_b:
        left = asset_service.get_asset_by_ticker(db, asset_a)
        right = asset_service.get_asset_by_ticker(db, asset_b)
        subject_type = "asset"
    else:
        return JSONResponse(
            status_code=400,
            content=error_response(
                message="Provide either company_a and company_b, or asset_a and asset_b.",
                error_code="INVALID_COMPARE_REQUEST",
            ),
        )

    if left is None or right is None:
        missing = []
        if left is None:
            missing.append(company_a or asset_a or "left")
        if right is None:
            missing.append(company_b or asset_b or "right")
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Could not find comparison subject(s): {', '.join(str(item).upper() for item in missing)}",
                error_code="COMPARE_SUBJECT_NOT_FOUND",
            ),
        )

    return success_response(
        message="Comparison retrieved successfully",
        data=build_comparison(left, right, subject_type=subject_type),
    )

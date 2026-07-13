"""Read-only industry intelligence endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.database.session import get_db
from app.services import company_service
from app.services.intelligence.industry_engine import build_industry_intelligence

router = APIRouter(prefix="/industries", tags=["industries"])


@router.get("/{industry}", response_model=None)
async def get_industry(
    industry: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return deterministic industry overview and related companies."""
    companies, _total = company_service.list_companies(db, limit=100)
    return success_response(
        message="Industry intelligence retrieved successfully",
        data=build_industry_intelligence(industry, companies),
    )

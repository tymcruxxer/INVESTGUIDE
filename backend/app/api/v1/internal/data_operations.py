"""Internal ingestion operations and data-quality endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.responses import success_response
from app.database.session import get_db
from app.services.data_quality import (
    company_quality_report,
    data_quality_summary,
    get_run_detail,
    list_issues,
    list_runs,
    score_entity,
    source_health,
)

router = APIRouter(prefix="/internal", tags=["internal-data-operations"])


def require_internal_access() -> None:
    """Development-only guard until admin roles exist."""
    settings = get_settings()
    if settings.environment != "development" and not settings.debug:
        raise HTTPException(status_code=403, detail="Internal operations endpoints are available only in development until admin roles exist.")


DbSession = Annotated[Session, Depends(get_db)]
InternalAccess = Annotated[None, Depends(require_internal_access)]


@router.get("/ingestion/runs")
def get_ingestion_runs(_: InternalAccess, db: DbSession, page: int = Query(1, ge=1), limit: int = Query(25, ge=1, le=100)) -> dict[str, object]:
    """List ingestion runs for operators."""
    result = list_runs(db, page=page, limit=limit)
    return success_response("Ingestion runs retrieved successfully", result.items, {"total": result.total, "page": result.page, "limit": result.limit})


@router.get("/ingestion/runs/{run_id}")
def get_ingestion_run(run_id: int, _: InternalAccess, db: DbSession) -> dict[str, object]:
    """Return run details and retry guidance."""
    result = get_run_detail(db, run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found.")
    return success_response("Ingestion run retrieved successfully", result)


@router.get("/ingestion/runs/{run_id}/issues")
def get_ingestion_run_issues(
    run_id: int,
    _: InternalAccess,
    db: DbSession,
    severity: str | None = None,
    issue_code: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
) -> dict[str, object]:
    """Return record-level issues for a run."""
    result = list_issues(db, run_id=run_id, severity=severity, issue_code=issue_code, page=page, limit=limit)
    return success_response("Ingestion issues retrieved successfully", result.items, {"total": result.total, "page": result.page, "limit": result.limit})


@router.get("/ingestion/sources")
def get_ingestion_sources(_: InternalAccess, db: DbSession) -> dict[str, object]:
    """Return source health summaries."""
    return success_response("Source health retrieved successfully", source_health(db))


@router.get("/data-quality/summary")
def get_data_quality_summary(_: InternalAccess, db: DbSession) -> dict[str, object]:
    """Return entity quality overview."""
    return success_response("Data quality summary retrieved successfully", data_quality_summary(db))


@router.get("/data-quality/entities/{entity_type}")
def get_entity_quality(entity_type: str, _: InternalAccess, db: DbSession) -> dict[str, object]:
    """Return one entity-quality summary."""
    try:
        result = score_entity(db, entity_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return success_response("Entity data quality retrieved successfully", result)


@router.get("/data-quality/companies/{ticker}")
def get_company_data_quality(ticker: str, _: InternalAccess, db: DbSession) -> dict[str, object]:
    """Return internal company data-quality report."""
    result = company_quality_report(db, ticker)
    if result is None:
        raise HTTPException(status_code=404, detail="Company not found.")
    return success_response("Company data quality retrieved successfully", result)


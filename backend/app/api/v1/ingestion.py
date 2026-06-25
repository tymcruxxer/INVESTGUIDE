"""Internal news ingestion endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.database.session import get_db
from app.schemas.ingestion_report import NewsIngestionRequest
from app.services.ingestion_service import ingest_news_payloads

router = APIRouter(prefix="/ingestion", tags=["internal-ingestion"])


@router.post("/news")
async def ingest_news(
    request: NewsIngestionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Run the internal news ingestion adapter for normalized article payloads."""
    report = ingest_news_payloads(db, request.articles, mode=request.mode)
    return success_response(
        message="News ingestion completed",
        data=report.model_dump(mode="json"),
    )
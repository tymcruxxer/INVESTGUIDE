"""Health check endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import success_response
from app.database.diagnostics import run_database_diagnostics

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return backend health status."""
    settings = get_settings()
    diagnostics = run_database_diagnostics()
    return success_response(
        message="Backend is healthy",
        data={
            "status": "ok",
            "database": diagnostics.database,
            "migrations": diagnostics.migrations,
            "environment": settings.environment,
            "version": settings.app_version,
        },
    )

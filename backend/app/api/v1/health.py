"""Health check endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import success_response

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return backend health status."""
    settings = get_settings()
    return success_response(
        message="Backend is healthy",
        data={
            "status": "ok",
            "version": settings.app_version,
        },
    )

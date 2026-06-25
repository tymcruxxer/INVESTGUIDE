"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.assets import router as assets_router
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.news import router as news_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(assets_router)
api_router.include_router(news_router)
api_router.include_router(ingestion_router)
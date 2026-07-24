"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.admin_ingestion import router as admin_ingestion_router
from app.api.v1.admin_connectors import router as admin_connectors_router`r`nfrom app.api.v1.admin_runtime import router as admin_runtime_router
from app.api.v1.auth import router as auth_router
from app.api.v1.assets import router as assets_router
from app.api.v1.companies import router as companies_router
from app.api.v1.compare import router as compare_router
from app.api.v1.health import router as health_router
from app.api.v1.internal.data_operations import router as data_operations_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.industries import router as industries_router
from app.api.v1.investor_profile import router as investor_profile_router
from app.api.v1.macro import router as macro_router
from app.api.v1.news import router as news_router
from app.api.v1.sectors import router as sectors_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(admin_ingestion_router)
api_router.include_router(admin_connectors_router)`r`napi_router.include_router(admin_runtime_router)
api_router.include_router(assets_router)
api_router.include_router(companies_router)
api_router.include_router(compare_router)
api_router.include_router(news_router)
api_router.include_router(sectors_router)
api_router.include_router(industries_router)
api_router.include_router(ingestion_router)
api_router.include_router(data_operations_router)
api_router.include_router(investor_profile_router)
api_router.include_router(macro_router)










"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_masked_database_url, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware



def log_startup_diagnostics(app: FastAPI) -> None:
    """Log local runtime diagnostics needed for CORS/auth connectivity."""
    settings = get_settings()
    logger = get_logger(__name__)
    cors_installed = any(middleware.cls is CORSMiddleware for middleware in app.user_middleware)
    middleware_order = [middleware.cls.__name__ for middleware in app.user_middleware]
    logger.info("InvestGuide startup APP_ENV=%s", settings.environment)
    logger.info("InvestGuide startup DATABASE_URL=%s", get_masked_database_url(settings.database_url))
    logger.info("InvestGuide startup CORS_ORIGINS=%s", settings.cors_origins)
    logger.info("InvestGuide startup CORSMiddleware installed=%s", cors_installed)
    logger.info("InvestGuide startup middleware order=%s", middleware_order)
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    log_startup_diagnostics(app)

    return app


app = create_app()

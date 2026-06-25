"""Global exception handlers."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.core.responses import error_response

logger = get_logger(__name__)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions with the response envelope."""
    logger.warning(
        "HTTP exception on %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            error_code="HTTP_ERROR",
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors with the response envelope."""
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=error_response(
            message="Request validation failed",
            error_code="VALIDATION_ERROR",
            details=exc.errors(),
        ),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected errors with the response envelope."""
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal server error",
            error_code="INTERNAL_SERVER_ERROR",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

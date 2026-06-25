"""Application middleware."""

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)

RequestHandler = Callable[[Request], Awaitable[Response]]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log requests and attach processing time metadata."""

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        logger.info(
            "%s %s completed with %s in %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )
        return response

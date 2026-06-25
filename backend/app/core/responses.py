"""Reusable API response envelope helpers."""

from typing import Any


def success_response(
    message: str,
    data: Any | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standard success response envelope."""
    response: dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        response["meta"] = meta
    return response


def error_response(
    message: str,
    error_code: str,
    details: Any | None = None,
) -> dict[str, Any]:
    """Build a standard error response envelope."""
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details or {},
    }

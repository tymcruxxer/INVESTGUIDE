"""Secure admin APIs for the Execution Runtime Registry."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.user import User
from app.schemas.runtime_registry import RUNTIME_METADATA, RuntimeCreate, RuntimeUpdate, RuntimeValidationRequest
from app.services import runtime_registry_service
from app.services.rbac_service import require_permission
from app.services.runtime_registry_service import RuntimeRegistryError

router = APIRouter(prefix="/admin/runtime", tags=["admin-runtime"])


def _request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _runtime_error(exc: RuntimeRegistryError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_response(message=exc.message, error_code=exc.error_code))


@router.get("/capabilities", response_model=None)
async def admin_runtime_capabilities(current_user: User = Depends(require_permission("runtime.read"))) -> dict[str, Any]:
    """Return enum metadata for runtime management UI."""
    return success_response(message="Runtime metadata retrieved successfully", data=RUNTIME_METADATA.model_dump(mode="json"))


@router.post("/validate", response_model=None)
async def admin_runtime_validate(payload: RuntimeValidationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("runtime.update"))) -> dict[str, Any] | JSONResponse:
    """Validate runtime/source/connector readiness without executing connector work."""
    try:
        validation = runtime_registry_service.validate_runtime(db, actor=current_user, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except RuntimeRegistryError as exc:
        return _runtime_error(exc)
    return success_response(message="Runtime validation completed", data=runtime_registry_service.validation_to_read(validation).model_dump(mode="json"))


@router.get("", response_model=None)
async def admin_runtimes(
    search: str | None = None,
    status: str | None = None,
    connector_type: str | None = None,
    capability: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("runtime.read")),
) -> dict[str, Any]:
    """Return the runtime registry list."""
    result = runtime_registry_service.list_runtimes(
        db,
        search=search,
        status=status,
        connector_type=connector_type,
        capability=capability,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(message="Runtime registry retrieved successfully", data=runtime_registry_service.runtime_list_payload(result).model_dump(mode="json"))


@router.post("", response_model=None)
async def admin_runtime_create(payload: RuntimeCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("runtime.update"))) -> dict[str, Any] | JSONResponse:
    """Create a reusable runtime definition."""
    try:
        runtime = runtime_registry_service.create_runtime(db, actor=current_user, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except RuntimeRegistryError as exc:
        return _runtime_error(exc)
    return success_response(message="Runtime created successfully", data=runtime_registry_service.runtime_to_read(db, runtime).model_dump(mode="json"))


@router.get("/{runtime_id}", response_model=None)
async def admin_runtime_detail(runtime_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("runtime.read"))) -> dict[str, Any] | JSONResponse:
    """Return one runtime with capabilities, compatibility, validation, and audit history."""
    try:
        runtime = runtime_registry_service.get_runtime_or_raise(db, runtime_id)
    except RuntimeRegistryError as exc:
        return _runtime_error(exc)
    return success_response(message="Runtime retrieved successfully", data=runtime_registry_service.runtime_to_read(db, runtime).model_dump(mode="json"))


@router.patch("/{runtime_id}", response_model=None)
async def admin_runtime_update(runtime_id: int, payload: RuntimeUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("runtime.update"))) -> dict[str, Any] | JSONResponse:
    """Update runtime metadata without executing connector work."""
    try:
        runtime = runtime_registry_service.get_runtime_or_raise(db, runtime_id, include_archived=True)
        updated = runtime_registry_service.update_runtime(db, actor=current_user, runtime=runtime, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except RuntimeRegistryError as exc:
        return _runtime_error(exc)
    return success_response(message="Runtime updated successfully", data=runtime_registry_service.runtime_to_read(db, updated).model_dump(mode="json"))

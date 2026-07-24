"""Secure admin APIs for the Connector Registry."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.user import User
from app.schemas.connector_registry import CONNECTOR_METADATA, ConnectorCreate, ConnectorStatusUpdate, ConnectorUpdate, ConnectorValidationRequest
from app.services import connector_registry_service
from app.services.connector_registry_service import ConnectorRegistryError
from app.services.rbac_service import require_permission

router = APIRouter(prefix="/admin/connectors", tags=["admin-connectors"])


def _request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _connector_error(exc: ConnectorRegistryError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_response(message=exc.message, error_code=exc.error_code))


@router.get("/capabilities", response_model=None)
async def admin_connector_capabilities(current_user: User = Depends(require_permission("connectors.read"))) -> dict[str, Any]:
    """Return enum metadata for connector management UI."""
    return success_response(message="Connector metadata retrieved successfully", data=CONNECTOR_METADATA.model_dump(mode="json"))


@router.get("", response_model=None)
async def admin_connectors(
    search: str | None = None,
    connector_type: str | None = None,
    lifecycle: str | None = None,
    capability: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("connectors.read")),
) -> dict[str, Any]:
    """Return the connector registry list."""
    result = connector_registry_service.list_connectors(
        db,
        search=search,
        connector_type=connector_type,
        lifecycle=lifecycle,
        capability=capability,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(message="Connector registry retrieved successfully", data=connector_registry_service.connector_list_payload(result).model_dump(mode="json"))


@router.post("", response_model=None)
async def admin_connector_create(payload: ConnectorCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("connectors.update"))) -> dict[str, Any] | JSONResponse:
    """Create a reusable connector definition."""
    try:
        connector = connector_registry_service.create_connector(db, actor=current_user, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except ConnectorRegistryError as exc:
        return _connector_error(exc)
    return success_response(message="Connector created successfully", data=connector_registry_service.connector_to_read(db, connector).model_dump(mode="json"))


@router.get("/{connector_id}", response_model=None)
async def admin_connector_detail(connector_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("connectors.read"))) -> dict[str, Any] | JSONResponse:
    """Return one connector with capabilities, schema, validation, and source bindings."""
    try:
        connector = connector_registry_service.get_connector_or_raise(db, connector_id)
    except ConnectorRegistryError as exc:
        return _connector_error(exc)
    return success_response(message="Connector retrieved successfully", data=connector_registry_service.connector_to_read(db, connector).model_dump(mode="json"))


@router.patch("/{connector_id}", response_model=None)
async def admin_connector_update(connector_id: int, payload: ConnectorUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("connectors.update"))) -> dict[str, Any] | JSONResponse:
    """Update connector metadata without executing connector work."""
    try:
        connector = connector_registry_service.get_connector_or_raise(db, connector_id)
        updated = connector_registry_service.update_connector(db, actor=current_user, connector=connector, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except ConnectorRegistryError as exc:
        return _connector_error(exc)
    return success_response(message="Connector updated successfully", data=connector_registry_service.connector_to_read(db, updated).model_dump(mode="json"))


@router.post("/{connector_id}/validate", response_model=None)
async def admin_connector_validate(connector_id: int, payload: ConnectorValidationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("connectors.update"))) -> dict[str, Any] | JSONResponse:
    """Validate connector metadata and config contracts without outbound network calls."""
    try:
        connector = connector_registry_service.get_connector_or_raise(db, connector_id)
        validation = connector_registry_service.validate_connector(db, actor=current_user, connector=connector, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except ConnectorRegistryError as exc:
        return _connector_error(exc)
    return success_response(message="Connector validation completed", data=connector_registry_service.validation_to_read(validation).model_dump(mode="json"))


@router.patch("/{connector_id}/status", response_model=None)
async def admin_connector_status(connector_id: int, payload: ConnectorStatusUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("connectors.update"))) -> dict[str, Any] | JSONResponse:
    """Update connector lifecycle state, including soft archive."""
    try:
        connector = connector_registry_service.get_connector_or_raise(db, connector_id, include_archived=True)
        updated = connector_registry_service.update_connector_status(db, actor=current_user, connector=connector, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except ConnectorRegistryError as exc:
        return _connector_error(exc)
    return success_response(message="Connector lifecycle updated successfully", data=connector_registry_service.connector_to_read(db, updated).model_dump(mode="json"))

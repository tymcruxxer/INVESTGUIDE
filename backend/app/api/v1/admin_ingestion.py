"""Secure admin APIs for the Ingestion Operations Centre."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.user import User
from app.schemas.ingestion_operations import IngestionJobCreate, IngestionJobUpdate, IngestionOperationRequest, INGESTION_OPERATION_METADATA
from app.services import ingestion_operations_service
from app.services.ingestion_operations_service import IngestionOperationsError
from app.services.rbac_service import require_permission

router = APIRouter(prefix="/admin/ingestion", tags=["admin-ingestion"])


def _request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _operations_error(exc: IngestionOperationsError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_response(message=exc.message, error_code=exc.error_code))


@router.get("/metadata", response_model=None)
async def admin_ingestion_metadata(current_user: User = Depends(require_permission("ingestion.read"))) -> dict[str, Any]:
    """Return enum metadata for the operations UI."""
    return success_response(message="Ingestion operations metadata retrieved successfully", data=INGESTION_OPERATION_METADATA.model_dump(mode="json"))


@router.get("/jobs", response_model=None)
async def admin_ingestion_jobs(
    search: str | None = None,
    source_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    job_type: str | None = None,
    freshness_status: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ingestion.read")),
) -> dict[str, Any]:
    """Return the ingestion job registry."""
    result = ingestion_operations_service.list_jobs(db, search=search, source_id=source_id, status=status, priority=priority, job_type=job_type, freshness_status=freshness_status, page=page, limit=limit, sort_by=sort_by, sort_order=sort_order)
    return success_response(message="Ingestion jobs retrieved successfully", data=ingestion_operations_service.job_list_payload(db, result).model_dump(mode="json"))


@router.post("/jobs", response_model=None)
async def admin_ingestion_job_create(payload: IngestionJobCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    """Create an ingestion job definition without executing it."""
    try:
        job = ingestion_operations_service.create_job(db, actor=current_user, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except IngestionOperationsError as exc:
        return _operations_error(exc)
    return success_response(message="Ingestion job created successfully", data=ingestion_operations_service.job_to_read(db, job).model_dump(mode="json"))


@router.get("/jobs/{job_id}", response_model=None)
async def admin_ingestion_job_detail(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.read"))) -> dict[str, Any] | JSONResponse:
    """Return one ingestion job with execution history."""
    try:
        job = ingestion_operations_service.get_job_or_raise(db, job_id)
    except IngestionOperationsError as exc:
        return _operations_error(exc)
    return success_response(message="Ingestion job retrieved successfully", data=ingestion_operations_service.job_to_read(db, job).model_dump(mode="json"))


@router.patch("/jobs/{job_id}", response_model=None)
async def admin_ingestion_job_update(job_id: int, payload: IngestionJobUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    """Update an ingestion job definition without executing it."""
    try:
        job = ingestion_operations_service.get_job_or_raise(db, job_id)
        updated = ingestion_operations_service.update_job(db, actor=current_user, job=job, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except IngestionOperationsError as exc:
        return _operations_error(exc)
    return success_response(message="Ingestion job updated successfully", data=ingestion_operations_service.job_to_read(db, updated).model_dump(mode="json"))


async def _operation(job_id: int, operation: str, payload: IngestionOperationRequest, request: Request, db: Session, current_user: User) -> dict[str, Any] | JSONResponse:
    try:
        job = ingestion_operations_service.get_job_or_raise(db, job_id)
        updated = ingestion_operations_service.request_operation(db, actor=current_user, job=job, operation=operation, payload=payload, request_id=_request_id(request), ip_address=_request_ip(request))
    except IngestionOperationsError as exc:
        return _operations_error(exc)
    return success_response(message=f"Ingestion job {operation} request recorded successfully", data=ingestion_operations_service.job_to_read(db, updated).model_dump(mode="json"))


@router.post("/jobs/{job_id}/run", response_model=None)
async def admin_ingestion_job_run(job_id: int, payload: IngestionOperationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    return await _operation(job_id, "run", payload, request, db, current_user)


@router.post("/jobs/{job_id}/retry", response_model=None)
async def admin_ingestion_job_retry(job_id: int, payload: IngestionOperationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    return await _operation(job_id, "retry", payload, request, db, current_user)


@router.post("/jobs/{job_id}/pause", response_model=None)
async def admin_ingestion_job_pause(job_id: int, payload: IngestionOperationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    return await _operation(job_id, "pause", payload, request, db, current_user)


@router.post("/jobs/{job_id}/resume", response_model=None)
async def admin_ingestion_job_resume(job_id: int, payload: IngestionOperationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    return await _operation(job_id, "resume", payload, request, db, current_user)


@router.post("/jobs/{job_id}/cancel", response_model=None)
async def admin_ingestion_job_cancel(job_id: int, payload: IngestionOperationRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.manage"))) -> dict[str, Any] | JSONResponse:
    return await _operation(job_id, "cancel", payload, request, db, current_user)


@router.get("/executions", response_model=None)
async def admin_ingestion_executions(
    job_id: int | None = None,
    status: str | None = None,
    trigger_type: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ingestion.read")),
) -> dict[str, Any]:
    """Return ingestion execution history."""
    result = ingestion_operations_service.list_executions(db, job_id=job_id, status=status, trigger_type=trigger_type, page=page, limit=limit)
    return success_response(message="Ingestion executions retrieved successfully", data=ingestion_operations_service.execution_list_payload(result).model_dump(mode="json"))


@router.get("/executions/{execution_id}", response_model=None)
async def admin_ingestion_execution_detail(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("ingestion.read"))) -> dict[str, Any] | JSONResponse:
    """Return one ingestion execution detail."""
    try:
        execution = ingestion_operations_service.get_execution_or_raise(db, execution_id)
    except IngestionOperationsError as exc:
        return _operations_error(exc)
    return success_response(message="Ingestion execution retrieved successfully", data=ingestion_operations_service.execution_to_read(execution).model_dump(mode="json"))

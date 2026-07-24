"""Service layer for the Execution Runtime Registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.connector_registry import Connector, ConnectorLifecycle
from app.models.ingestion_operations import IngestionJob
from app.models.runtime_registry import (
    RuntimeCapability,
    RuntimeCompatibility,
    RuntimeCompatibilityStatus,
    RuntimeDefinition,
    RuntimeStatus,
    RuntimeValidation,
    RuntimeValidationStatus,
    RuntimeVersion,
)
from app.models.source_registry import Source, SourceStatus
from app.models.user import User
from app.schemas.runtime_registry import (
    ExecutionResultContract,
    RuntimeCreate,
    RuntimeListPayload,
    RuntimeRead,
    RuntimeSummary,
    RuntimeUpdate,
    RuntimeValidationRead,
    RuntimeValidationRequest,
)
from app.services.audit_service import record_audit_event


class RuntimeRegistryError(ValueError):
    """Raised when runtime registry operations fail validation."""

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


@dataclass(frozen=True)
class RuntimeListResult:
    runtimes: list[RuntimeDefinition]
    total: int
    page: int
    limit: int


def list_runtimes(
    db: Session,
    *,
    search: str | None = None,
    status: str | None = None,
    connector_type: str | None = None,
    capability: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
) -> RuntimeListResult:
    """List non-archived runtime definitions with filters."""
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(RuntimeDefinition).where(RuntimeDefinition.status != RuntimeStatus.ARCHIVED.value).options(selectinload(RuntimeDefinition.capabilities), selectinload(RuntimeDefinition.compatibilities))

    if search:
        needle = f"%{search.strip().lower()}%"
        query = query.where(or_(func.lower(RuntimeDefinition.name).like(needle), func.lower(RuntimeDefinition.display_name).like(needle), func.lower(RuntimeDefinition.runtime_class).like(needle)))
    if status:
        query = query.where(RuntimeDefinition.status == status)
    if connector_type:
        query = query.where(RuntimeDefinition.supported_connector_types.contains([connector_type]))
    if capability:
        query = query.join(RuntimeCapability).where(RuntimeCapability.capability == capability)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = {
        "name": RuntimeDefinition.display_name,
        "status": RuntimeDefinition.status,
        "version": RuntimeDefinition.version,
        "runtime_class": RuntimeDefinition.runtime_class,
        "updated_at": RuntimeDefinition.updated_at,
        "created_at": RuntimeDefinition.created_at,
    }.get(sort_by, RuntimeDefinition.updated_at)
    order = asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)
    runtimes = list(db.scalars(query.order_by(order).offset((page - 1) * limit).limit(limit)).unique().all())
    return RuntimeListResult(runtimes=runtimes, total=total, page=page, limit=limit)


def get_runtime_or_raise(db: Session, runtime_id: int, *, include_archived: bool = False) -> RuntimeDefinition:
    """Return a runtime with relationships or raise a registry error."""
    runtime = db.scalar(
        select(RuntimeDefinition)
        .where(RuntimeDefinition.id == runtime_id)
        .options(
            selectinload(RuntimeDefinition.capabilities),
            selectinload(RuntimeDefinition.compatibilities),
            selectinload(RuntimeDefinition.versions),
            selectinload(RuntimeDefinition.validations),
        )
    )
    if runtime is None or (runtime.status == RuntimeStatus.ARCHIVED.value and not include_archived):
        raise RuntimeRegistryError("Runtime was not found", "RUNTIME_NOT_FOUND", 404)
    return runtime


def create_runtime(db: Session, *, actor: User, payload: RuntimeCreate, request_id: str | None = None, ip_address: str | None = None) -> RuntimeDefinition:
    """Create a runtime definition with capability metadata."""
    existing = db.scalar(select(RuntimeDefinition).where(RuntimeDefinition.name == payload.name))
    if existing is not None and existing.status != RuntimeStatus.ARCHIVED.value:
        raise RuntimeRegistryError("A runtime with this name already exists", "RUNTIME_ALREADY_EXISTS", 409)

    runtime = RuntimeDefinition(
        name=payload.name,
        display_name=payload.display_name,
        description=payload.description,
        version=payload.version,
        runtime_class=payload.runtime_class,
        status=payload.status,
        supported_connector_types=payload.supported_connector_types,
        runtime_metadata=payload.runtime_metadata,
        vendor=payload.vendor,
        author=payload.author,
        classification=payload.classification,
        change_summary=payload.change_summary,
        is_active=payload.status == RuntimeStatus.ACTIVE.value,
    )
    db.add(runtime)
    db.flush()
    _replace_capabilities(db, runtime, payload.capabilities)
    db.flush()
    _record_version(db, runtime, actor, "create", None, _runtime_snapshot(runtime), payload.reason, request_id)
    _audit(db, actor, "admin.runtime.create", runtime, payload.reason, request_id, ip_address, previous=None, new=_runtime_snapshot(runtime))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise RuntimeRegistryError("A runtime with this name already exists", "RUNTIME_ALREADY_EXISTS", 409) from exc
    return get_runtime_or_raise(db, runtime.id)


def update_runtime(db: Session, *, actor: User, runtime: RuntimeDefinition, payload: RuntimeUpdate, request_id: str | None = None, ip_address: str | None = None) -> RuntimeDefinition:
    """Update a runtime definition and preserve an immutable version snapshot."""
    previous = _runtime_snapshot(runtime)
    for field in (
        "display_name",
        "description",
        "version",
        "runtime_class",
        "status",
        "supported_connector_types",
        "runtime_metadata",
        "vendor",
        "author",
        "classification",
        "change_summary",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(runtime, field, value)
    runtime.is_active = runtime.status == RuntimeStatus.ACTIVE.value
    if runtime.status == RuntimeStatus.ARCHIVED.value and runtime.archived_at is None:
        runtime.archived_at = datetime.now(UTC)
        runtime.archived_by_user_id = actor.id
    if payload.capabilities is not None:
        _replace_capabilities(db, runtime, payload.capabilities)
    db.flush()
    new = _runtime_snapshot(runtime)
    _record_version(db, runtime, actor, "update", previous, new, payload.reason, request_id)
    _audit(db, actor, "admin.runtime.update", runtime, payload.reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    return get_runtime_or_raise(db, runtime.id, include_archived=True)


def validate_runtime(db: Session, *, actor: User, payload: RuntimeValidationRequest, request_id: str | None = None, ip_address: str | None = None) -> RuntimeValidation:
    """Validate runtime/source/connector/job readiness without execution."""
    errors: list[str] = []
    warnings: list[str] = []
    checked_fields = [
        "runtime_exists",
        "runtime_active",
        "source_exists",
        "source_active",
        "connector_exists",
        "connector_active",
        "connector_runtime_compatibility",
        "source_connector_binding",
        "job_active",
        "result_contract",
    ]
    runtime = db.get(RuntimeDefinition, payload.runtime_id) if payload.runtime_id is not None else None
    connector = db.get(Connector, payload.connector_id) if payload.connector_id is not None else None
    source = db.get(Source, payload.source_id) if payload.source_id is not None else None
    job = db.get(IngestionJob, payload.job_id) if payload.job_id is not None else None

    if payload.runtime_id is not None and runtime is None:
        errors.append("Runtime was not found.")
    if runtime is not None:
        if runtime.status in {RuntimeStatus.DISABLED.value, RuntimeStatus.ARCHIVED.value}:
            errors.append(f"Runtime status '{runtime.status}' is not executable.")
        if runtime.status == RuntimeStatus.DEPRECATED.value:
            warnings.append("Runtime is deprecated and should only be used for legacy connectors.")
    if payload.connector_id is not None and connector is None:
        errors.append("Connector was not found.")
    if connector is not None and connector.lifecycle in {ConnectorLifecycle.DISABLED.value, ConnectorLifecycle.ARCHIVED.value}:
        errors.append(f"Connector lifecycle '{connector.lifecycle}' is not executable.")
    if payload.source_id is not None and source is None:
        errors.append("Source was not found.")
    if source is not None and (source.status != SourceStatus.ENABLED.value or not source.is_active):
        errors.append("Source is not enabled for runtime validation.")
    if job is not None and not job.is_enabled:
        errors.append("Ingestion job is not enabled.")
    if payload.job_id is not None and job is None:
        errors.append("Ingestion job was not found.")

    if source is not None and connector is not None:
        if source.connector_id is not None and source.connector_id != connector.id:
            errors.append("Source is bound to a different connector.")
        if source.connector_type not in _compatible_source_connector_types(connector.connector_type):
            warnings.append(f"Source connector type '{source.connector_type}' may need connector '{connector.connector_type}'.")
    if runtime is not None and connector is not None and connector.connector_type not in set(runtime.supported_connector_types or []):
        errors.append(f"Runtime does not support connector type '{connector.connector_type}'.")

    result_contract = ExecutionResultContract(
        status="validation_failed" if errors else "success",
        duration_ms=0,
        warnings=warnings,
        errors=errors,
        metrics={"network_requests": 0, "database_writes": 0},
        output_metadata={"payload_data_included": False, "contract_only": True},
        provenance_reference=f"runtime-validation:{request_id or payload.context.request_id or 'local'}",
    )
    if errors:
        status = RuntimeValidationStatus.FAILED.value
        summary = "Runtime readiness validation failed. No connector execution was performed."
    elif warnings:
        status = RuntimeValidationStatus.WARNING.value
        summary = "Runtime readiness validation passed with warnings. No connector execution was performed."
    else:
        status = RuntimeValidationStatus.PASSED.value
        summary = "Runtime readiness validation passed. No connector execution was performed."

    validation = RuntimeValidation(
        runtime_id=runtime.id if runtime is not None else None,
        source_id=source.id if source is not None else payload.source_id,
        connector_id=connector.id if connector is not None else payload.connector_id,
        actor_user_id=actor.id,
        status=status,
        summary=summary,
        errors=errors,
        warnings=warnings,
        checked_fields=checked_fields,
        execution_context=payload.context.model_dump(mode="json"),
        result_contract=result_contract.model_dump(mode="json"),
        request_id=request_id or payload.context.request_id,
    )
    db.add(validation)
    db.flush()
    if runtime is not None and connector is not None:
        _upsert_compatibility(db, runtime, connector, RuntimeCompatibilityStatus.COMPATIBLE.value if not errors else RuntimeCompatibilityStatus.INCOMPATIBLE.value, "; ".join(errors or warnings) or "Validated metadata-only compatibility.")
    target = runtime or RuntimeDefinition(name="unresolved", display_name="Unresolved runtime", runtime_class="unresolved")
    _audit(
        db,
        actor,
        "admin.runtime.validate",
        target,
        payload.reason,
        request_id,
        ip_address,
        previous=None,
        new={"validation_status": status, "errors": errors, "warnings": warnings},
    )
    db.commit()
    db.refresh(validation)
    return validation


def runtime_to_summary(runtime: RuntimeDefinition) -> RuntimeSummary:
    return RuntimeSummary(
        id=runtime.id,
        name=runtime.name,
        display_name=runtime.display_name,
        version=runtime.version,
        runtime_class=runtime.runtime_class,
        status=runtime.status,
        supported_connector_types=runtime.supported_connector_types or [],
        capabilities=sorted(capability.capability for capability in runtime.capabilities),
        compatible_connector_count=len(runtime.compatibilities or []),
        last_updated_at=runtime.updated_at,
    )


def runtime_list_payload(result: RuntimeListResult) -> RuntimeListPayload:
    return RuntimeListPayload(
        runtimes=[runtime_to_summary(runtime) for runtime in result.runtimes],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
    )


def runtime_to_read(db: Session, runtime: RuntimeDefinition) -> RuntimeRead:
    audits = [
        {
            "id": event.id,
            "action": event.action,
            "result": event.result,
            "reason": event.reason,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        for event in db.scalars(select(AuditLog).where(AuditLog.target_type == "runtime", AuditLog.target_id == str(runtime.id)).order_by(AuditLog.created_at.desc()).limit(10)).all()
    ]
    summary = runtime_to_summary(runtime).model_dump()
    return RuntimeRead(
        **summary,
        description=runtime.description,
        runtime_metadata=runtime.runtime_metadata or {},
        vendor=runtime.vendor,
        author=runtime.author,
        classification=runtime.classification,
        lifecycle_states=runtime.lifecycle_states or [],
        result_statuses=runtime.result_statuses or [],
        change_summary=runtime.change_summary,
        is_active=runtime.is_active,
        capability_details=runtime.capabilities,
        compatibility_details=runtime.compatibilities,
        version_history=runtime.versions[:10],
        validation_history=runtime.validations[:10],
        recent_activity=audits,
        created_at=runtime.created_at,
        updated_at=runtime.updated_at,
    )


def validation_to_read(validation: RuntimeValidation) -> RuntimeValidationRead:
    return RuntimeValidationRead.model_validate(validation)


def _replace_capabilities(db: Session, runtime: RuntimeDefinition, capabilities: list[Any]) -> None:
    existing_by_capability = {item.capability: item for item in runtime.capabilities}
    incoming = {item.capability: item for item in capabilities}
    for capability, model in list(existing_by_capability.items()):
        if capability not in incoming:
            db.delete(model)
    for capability, item in incoming.items():
        model = existing_by_capability.get(capability)
        if model is None:
            db.add(RuntimeCapability(runtime_id=runtime.id, capability=capability, description=item.description))
        else:
            model.description = item.description


def _upsert_compatibility(db: Session, runtime: RuntimeDefinition, connector: Connector, status: str, notes: str) -> None:
    compatibility = db.scalar(select(RuntimeCompatibility).where(RuntimeCompatibility.runtime_id == runtime.id, RuntimeCompatibility.connector_id == connector.id))
    if compatibility is None:
        db.add(RuntimeCompatibility(runtime_id=runtime.id, connector_id=connector.id, connector_type=connector.connector_type, compatibility_status=status, notes=notes))
    else:
        compatibility.connector_type = connector.connector_type
        compatibility.compatibility_status = status
        compatibility.notes = notes


def _runtime_snapshot(runtime: RuntimeDefinition) -> dict[str, Any]:
    return {
        "id": runtime.id,
        "name": runtime.name,
        "display_name": runtime.display_name,
        "version": runtime.version,
        "runtime_class": runtime.runtime_class,
        "status": runtime.status,
        "supported_connector_types": runtime.supported_connector_types or [],
        "capabilities": sorted(item.capability for item in runtime.capabilities),
        "is_active": runtime.is_active,
    }


def _record_version(db: Session, runtime: RuntimeDefinition, actor: User, change_type: str, previous: dict[str, Any] | None, new: dict[str, Any] | None, reason: str | None, request_id: str | None) -> None:
    db.add(RuntimeVersion(runtime_id=runtime.id, version=runtime.version, actor_user_id=actor.id, change_type=change_type, change_summary=reason, previous_values=previous, new_values=new, request_id=request_id))


def _audit(db: Session, actor: User, action: str, runtime: RuntimeDefinition, reason: str | None, request_id: str | None, ip_address: str | None, previous: dict[str, Any] | None, new: dict[str, Any] | None) -> None:
    record_audit_event(
        db,
        actor=actor,
        action=action,
        target_type="runtime",
        target_id=str(runtime.id or "unresolved"),
        result="success",
        reason=reason,
        request_id=request_id,
        ip_address=ip_address,
        metadata={"previous": previous, "new": new},
        commit=False,
    )


def _compatible_source_connector_types(source_connector_type: str) -> set[str]:
    mapping = {
        "rest_api": {"rest_api", "graphql", "json_feed"},
        "rss": {"rss", "xml_feed"},
        "website": {"html_scraper", "rest_api"},
        "html_scraper": {"html_scraper"},
        "pdf": {"pdf_extractor"},
        "csv": {"csv_importer"},
        "json": {"json_feed", "rest_api"},
        "xml": {"xml_feed", "rss"},
        "manual_upload": {"file_upload", "manual"},
        "database": {"database"},
        "future_connector": {"future_custom_connector", "rest_api"},
    }
    return mapping.get(source_connector_type, {source_connector_type})

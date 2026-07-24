"""Service layer for the Connector Registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.connector_registry import (
    Connector,
    ConnectorCapability,
    ConnectorConfigurationSchema,
    ConnectorLifecycle,
    ConnectorValidation,
    ConnectorValidationStatus,
    ConnectorVersion,
)
from app.models.source_registry import Source
from app.models.user import User
from app.schemas.connector_registry import (
    ConnectorConfigurationSchemaInput,
    ConnectorCreate,
    ConnectorListPayload,
    ConnectorRead,
    ConnectorStatusUpdate,
    ConnectorSummary,
    ConnectorUpdate,
    ConnectorValidationRead,
    ConnectorValidationRequest,
    SECRET_FIELD_HINTS,
)
from app.services.audit_service import record_audit_event


class ConnectorRegistryError(ValueError):
    """Raised when connector registry operations fail validation."""

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


@dataclass(frozen=True)
class ConnectorListResult:
    """Paginated connector result."""

    connectors: list[Connector]
    total: int
    page: int
    limit: int


def list_connectors(
    db: Session,
    *,
    search: str | None = None,
    connector_type: str | None = None,
    lifecycle: str | None = None,
    capability: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
) -> ConnectorListResult:
    """List non-archived connectors with filters."""
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(Connector).where(Connector.lifecycle != ConnectorLifecycle.ARCHIVED.value).options(selectinload(Connector.capabilities), selectinload(Connector.sources))

    if search:
        needle = f"%{search.strip().lower()}%"
        query = query.where(or_(func.lower(Connector.name).like(needle), func.lower(Connector.display_name).like(needle), func.lower(Connector.vendor).like(needle)))
    if connector_type:
        query = query.where(Connector.connector_type == connector_type)
    if lifecycle:
        query = query.where(Connector.lifecycle == lifecycle)
    if capability:
        query = query.join(ConnectorCapability).where(ConnectorCapability.capability == capability)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = {
        "name": Connector.display_name,
        "type": Connector.connector_type,
        "lifecycle": Connector.lifecycle,
        "version": Connector.version,
        "updated_at": Connector.updated_at,
        "created_at": Connector.created_at,
    }.get(sort_by, Connector.updated_at)
    order = asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)
    connectors = list(db.scalars(query.order_by(order).offset((page - 1) * limit).limit(limit)).unique().all())
    return ConnectorListResult(connectors=connectors, total=total, page=page, limit=limit)


def get_connector_or_raise(db: Session, connector_id: int, *, include_archived: bool = False) -> Connector:
    """Return a connector with relationships or raise a registry error."""
    connector = db.scalar(
        select(Connector)
        .where(Connector.id == connector_id)
        .options(
            selectinload(Connector.capabilities),
            selectinload(Connector.configuration_contract),
            selectinload(Connector.versions),
            selectinload(Connector.validations),
            selectinload(Connector.sources),
        )
    )
    if connector is None or (connector.lifecycle == ConnectorLifecycle.ARCHIVED.value and not include_archived):
        raise ConnectorRegistryError("Connector was not found", "CONNECTOR_NOT_FOUND", 404)
    return connector


def create_connector(db: Session, *, actor: User, payload: ConnectorCreate, request_id: str | None = None, ip_address: str | None = None) -> Connector:
    """Create a connector with capability and configuration metadata."""
    _assert_schema_is_safe(payload.configuration_schema)
    _assert_schema_is_safe(payload.configuration_contract.schema)
    existing = db.scalar(select(Connector).where(Connector.name == payload.name))
    if existing is not None and existing.lifecycle != ConnectorLifecycle.ARCHIVED.value:
        raise ConnectorRegistryError("A connector with this name already exists", "CONNECTOR_ALREADY_EXISTS", 409)

    connector = Connector(
        name=payload.name,
        display_name=payload.display_name,
        description=payload.description,
        version=payload.version,
        vendor=payload.vendor,
        author=payload.author,
        classification=payload.classification,
        connector_type=payload.connector_type,
        lifecycle=payload.lifecycle,
        authentication_strategy=payload.authentication_strategy,
        configuration_schema=payload.configuration_schema,
        required_fields=payload.required_fields,
        supported_source_categories=payload.supported_source_categories,
        compatibility_notes=payload.compatibility_notes,
        deprecation_status=payload.deprecation_status,
        change_summary=payload.change_summary,
        is_active=payload.lifecycle == ConnectorLifecycle.ACTIVE.value,
    )
    db.add(connector)
    db.flush()
    _replace_capabilities(db, connector, payload.capabilities)
    connector.configuration_contract = _configuration_contract_from_payload(payload.configuration_contract, connector.id)
    db.flush()
    _record_version(db, connector, actor, "create", None, _connector_snapshot(connector), payload.reason, request_id)
    _audit(db, actor, "admin.connector.create", connector, payload.reason, request_id, ip_address, previous=None, new=_connector_snapshot(connector))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConnectorRegistryError("A connector with this name already exists", "CONNECTOR_ALREADY_EXISTS", 409) from exc
    db.refresh(connector)
    return get_connector_or_raise(db, connector.id)


def update_connector(db: Session, *, actor: User, connector: Connector, payload: ConnectorUpdate, request_id: str | None = None, ip_address: str | None = None) -> Connector:
    """Update a connector definition and preserve an immutable version snapshot."""
    previous = _connector_snapshot(connector)
    if payload.configuration_schema is not None:
        _assert_schema_is_safe(payload.configuration_schema)
    if payload.configuration_contract is not None:
        _assert_schema_is_safe(payload.configuration_contract.schema)
    for field in (
        "display_name",
        "description",
        "version",
        "vendor",
        "author",
        "classification",
        "connector_type",
        "lifecycle",
        "authentication_strategy",
        "configuration_schema",
        "required_fields",
        "supported_source_categories",
        "compatibility_notes",
        "deprecation_status",
        "change_summary",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(connector, field, value)
    connector.is_active = connector.lifecycle == ConnectorLifecycle.ACTIVE.value
    if connector.lifecycle == ConnectorLifecycle.ARCHIVED.value and connector.archived_at is None:
        connector.archived_at = datetime.now(UTC)
        connector.archived_by_user_id = actor.id
    if payload.capabilities is not None:
        _replace_capabilities(db, connector, payload.capabilities)
    if payload.configuration_contract is not None:
        _apply_configuration_contract(connector.configuration_contract, payload.configuration_contract)
    db.flush()
    new = _connector_snapshot(connector)
    _record_version(db, connector, actor, "update", previous, new, payload.reason, request_id)
    _audit(db, actor, "admin.connector.update", connector, payload.reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    db.refresh(connector)
    return get_connector_or_raise(db, connector.id, include_archived=True)


def update_connector_status(db: Session, *, actor: User, connector: Connector, payload: ConnectorStatusUpdate, request_id: str | None = None, ip_address: str | None = None) -> Connector:
    """Update connector lifecycle without deleting historical metadata."""
    previous = _connector_snapshot(connector)
    connector.lifecycle = payload.lifecycle
    connector.is_active = payload.lifecycle == ConnectorLifecycle.ACTIVE.value
    if payload.lifecycle == ConnectorLifecycle.DEPRECATED.value:
        connector.deprecation_status = True
    if payload.lifecycle == ConnectorLifecycle.ARCHIVED.value:
        connector.archived_at = datetime.now(UTC)
        connector.archived_by_user_id = actor.id
    db.flush()
    new = _connector_snapshot(connector)
    _record_version(db, connector, actor, "status", previous, new, payload.reason, request_id)
    _audit(db, actor, "admin.connector.status", connector, payload.reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    db.refresh(connector)
    return get_connector_or_raise(db, connector.id, include_archived=True)


def validate_connector(db: Session, *, actor: User, connector: Connector, payload: ConnectorValidationRequest, request_id: str | None = None, ip_address: str | None = None) -> ConnectorValidation:
    """Validate connector metadata and requested configuration without outbound network calls."""
    requested = dict(payload.configuration)
    errors: list[str] = []
    warnings: list[str] = []
    checked_fields = ["lifecycle", "authentication_strategy", "configuration_schema", "required_fields", "source_category", "secrets_boundary"]

    if connector.lifecycle in {ConnectorLifecycle.DISABLED.value, ConnectorLifecycle.ARCHIVED.value}:
        errors.append(f"Connector lifecycle '{connector.lifecycle}' is not executable.")
    if connector.lifecycle == ConnectorLifecycle.DEPRECATED.value:
        warnings.append("Connector is deprecated and should only be used for legacy sources.")

    contract = connector.configuration_contract
    required_fields = list(contract.required_fields if contract else connector.required_fields or [])
    for field in required_fields:
        if field not in requested and field not in (connector.configuration_schema or {}):
            errors.append(f"Required configuration field '{field}' is missing.")

    schema = contract.schema if contract else connector.configuration_schema
    secret_fields = _find_secret_field_names(schema)
    if secret_fields:
        errors.append(f"Configuration schema contains secret-bearing fields: {', '.join(secret_fields)}.")

    if connector.authentication_strategy != "none" and connector.authentication_strategy not in _auth_supported_by_type(connector.connector_type):
        errors.append(f"Authentication strategy '{connector.authentication_strategy}' is not compatible with connector type '{connector.connector_type}'.")

    source = db.get(Source, payload.source_id) if payload.source_id is not None else None
    if payload.source_id is not None and source is None:
        errors.append("Requested source was not found.")
    if source is not None and connector.supported_source_categories and source.category not in connector.supported_source_categories:
        errors.append(f"Source category '{source.category}' is not supported by this connector.")
    if source is not None and connector.connector_type not in _compatible_source_connector_types(source.connector_type):
        warnings.append(f"Source connector type '{source.connector_type}' may need migration to '{connector.connector_type}'.")

    if not errors and warnings:
        status = ConnectorValidationStatus.WARNING.value
        summary = "Connector metadata is usable with warnings. No live network validation was performed."
    elif errors:
        status = ConnectorValidationStatus.FAILED.value
        summary = "Connector metadata failed validation. No live network validation was performed."
    else:
        status = ConnectorValidationStatus.PASSED.value
        summary = "Connector metadata passed validation. No live network validation was performed."

    validation = ConnectorValidation(
        connector_id=connector.id,
        actor_user_id=actor.id,
        status=status,
        summary=summary,
        errors=errors,
        warnings=warnings,
        checked_fields=checked_fields,
        requested_config=_redact_config(requested),
        request_id=request_id,
    )
    db.add(validation)
    db.flush()
    _audit(
        db,
        actor,
        "admin.connector.validate",
        connector,
        payload.reason,
        request_id,
        ip_address,
        previous=None,
        new={"validation_status": status, "errors": errors, "warnings": warnings},
    )
    db.commit()
    db.refresh(validation)
    return validation


def connector_to_summary(connector: Connector) -> ConnectorSummary:
    """Serialize a connector list row."""
    return ConnectorSummary(
        id=connector.id,
        name=connector.name,
        display_name=connector.display_name,
        version=connector.version,
        connector_type=connector.connector_type,
        lifecycle=connector.lifecycle,
        authentication_strategy=connector.authentication_strategy,
        classification=connector.classification,
        capabilities=sorted(capability.capability for capability in connector.capabilities),
        compatible_source_count=len(connector.sources or []),
        last_updated_at=connector.updated_at,
    )


def connector_list_payload(result: ConnectorListResult) -> ConnectorListPayload:
    """Serialize paginated connector list payload."""
    return ConnectorListPayload(
        connectors=[connector_to_summary(connector) for connector in result.connectors],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
    )


def connector_to_read(db: Session, connector: Connector) -> ConnectorRead:
    """Serialize connector detail with validation, source bindings, and audit history."""
    recent_activity = [
        {
            "id": event.id,
            "action": event.action,
            "result": event.result,
            "reason": event.reason,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        for event in db.scalars(
            select(AuditLog)
            .where(AuditLog.target_type == "connector", AuditLog.target_id == str(connector.id))
            .order_by(AuditLog.created_at.desc())
            .limit(10)
        ).all()
    ]
    summary = connector_to_summary(connector).model_dump()
    return ConnectorRead(
        **summary,
        description=connector.description,
        vendor=connector.vendor,
        author=connector.author,
        configuration_schema=connector.configuration_schema or {},
        required_fields=connector.required_fields or [],
        supported_source_categories=connector.supported_source_categories or [],
        compatibility_notes=connector.compatibility_notes,
        deprecation_status=connector.deprecation_status,
        change_summary=connector.change_summary,
        is_active=connector.is_active,
        configuration_contract=connector.configuration_contract,
        capability_details=connector.capabilities,
        version_history=connector.versions[:10],
        validation_history=connector.validations[:10],
        compatible_sources=[
            {
                "id": source.id,
                "name": source.name,
                "display_name": source.display_name,
                "category": source.category,
                "status": source.status,
                "connector_type": source.connector_type,
            }
            for source in connector.sources
        ],
        recent_activity=recent_activity,
        created_at=connector.created_at,
        updated_at=connector.updated_at,
    )


def validation_to_read(validation: ConnectorValidation) -> ConnectorValidationRead:
    """Serialize a validation result."""
    return ConnectorValidationRead.model_validate(validation)


def _configuration_contract_from_payload(payload: ConnectorConfigurationSchemaInput, connector_id: int) -> ConnectorConfigurationSchema:
    return ConnectorConfigurationSchema(connector_id=connector_id, **payload.model_dump())


def _apply_configuration_contract(contract: ConnectorConfigurationSchema, payload: ConnectorConfigurationSchemaInput) -> None:
    for field, value in payload.model_dump().items():
        setattr(contract, field, value)


def _replace_capabilities(db: Session, connector: Connector, capabilities: list[Any]) -> None:
    existing_by_capability = {item.capability: item for item in connector.capabilities}
    incoming = {item.capability: item for item in capabilities}
    for capability, model in list(existing_by_capability.items()):
        if capability not in incoming:
            db.delete(model)
    for capability, item in incoming.items():
        model = existing_by_capability.get(capability)
        if model is None:
            db.add(ConnectorCapability(connector_id=connector.id, capability=capability, description=item.description))
        else:
            model.description = item.description


def _connector_snapshot(connector: Connector) -> dict[str, Any]:
    contract = connector.configuration_contract
    return {
        "id": connector.id,
        "name": connector.name,
        "display_name": connector.display_name,
        "version": connector.version,
        "vendor": connector.vendor,
        "author": connector.author,
        "classification": connector.classification,
        "connector_type": connector.connector_type,
        "lifecycle": connector.lifecycle,
        "authentication_strategy": connector.authentication_strategy,
        "capabilities": sorted(item.capability for item in connector.capabilities),
        "required_fields": connector.required_fields or [],
        "supported_source_categories": connector.supported_source_categories or [],
        "configuration_contract": {
            "required_fields": contract.required_fields,
            "parser_identifier": contract.parser_identifier,
            "request_method": contract.request_method,
            "default_timeout_seconds": contract.default_timeout_seconds,
            "default_retry_count": contract.default_retry_count,
        }
        if contract
        else None,
        "deprecation_status": connector.deprecation_status,
        "is_active": connector.is_active,
    }


def _record_version(db: Session, connector: Connector, actor: User, change_type: str, previous: dict[str, Any] | None, new: dict[str, Any] | None, reason: str | None, request_id: str | None) -> None:
    db.add(
        ConnectorVersion(
            connector_id=connector.id,
            version=connector.version,
            actor_user_id=actor.id,
            change_type=change_type,
            change_summary=reason,
            compatibility_notes=connector.compatibility_notes,
            previous_values=previous,
            new_values=new,
            request_id=request_id,
        )
    )


def _audit(db: Session, actor: User, action: str, connector: Connector, reason: str | None, request_id: str | None, ip_address: str | None, previous: dict[str, Any] | None, new: dict[str, Any] | None) -> None:
    record_audit_event(
        db,
        actor=actor,
        action=action,
        target_type="connector",
        target_id=str(connector.id),
        result="success",
        reason=reason,
        request_id=request_id,
        ip_address=ip_address,
        metadata={"previous": previous, "new": new},
        commit=False,
    )


def _find_secret_field_names(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key).lower()
            path = f"{prefix}.{key}" if prefix else str(key)
            if any(hint in key_text for hint in SECRET_FIELD_HINTS):
                found.append(path)
            found.extend(_find_secret_field_names(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(_find_secret_field_names(nested, f"{prefix}[{index}]"))
    return sorted(set(found))


def _assert_schema_is_safe(schema: dict[str, Any]) -> None:
    secret_fields = _find_secret_field_names(schema)
    if secret_fields:
        raise ConnectorRegistryError("Configuration schema must describe secret references, not secret-bearing fields", "CONNECTOR_SCHEMA_CONTAINS_SECRETS")


def _redact_config(config: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in config.items():
        if any(hint in key.lower() for hint in SECRET_FIELD_HINTS):
            redacted[key] = "********"
        elif isinstance(value, dict):
            redacted[key] = _redact_config(value)
        else:
            redacted[key] = value
    return redacted


def _auth_supported_by_type(connector_type: str) -> set[str]:
    if connector_type in {"manual", "file_upload", "csv_importer"}:
        return {"none", "custom"}
    if connector_type == "database":
        return {"none", "username_password", "custom"}
    return {"none", "api_key", "bearer_token", "oauth2", "username_password", "cookie", "custom"}


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

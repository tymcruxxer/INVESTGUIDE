"""Service layer for the Data Source Registry."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.source_registry import Source, SourceConfiguration, SourceCredential, SourceStatus, SourceTier, SourceVersion
from app.models.user import User
from app.schemas.source_registry import (
    SourceConfigurationInput,
    SourceCreate,
    SourceCredentialInput,
    SourceListPayload,
    SourceRead,
    SourceStatusUpdate,
    SourceSummary,
    SourceUpdate,
    default_confidence_for_tier,
)
from app.services.audit_service import record_audit_event


class SourceRegistryError(ValueError):
    """Raised when source registry operations fail validation."""

    def __init__(self, message: str, error_code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


@dataclass(frozen=True)
class SourceListResult:
    """Paginated source result."""

    sources: list[Source]
    total: int
    page: int
    limit: int


def list_sources(
    db: Session,
    *,
    search: str | None = None,
    category: str | None = None,
    tier: str | None = None,
    status: str | None = None,
    connector_type: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
) -> SourceListResult:
    """List active registry sources with filters."""
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = select(Source).where(Source.status != SourceStatus.DELETED.value).options(selectinload(Source.configuration))

    if search:
        needle = f"%{search.strip().lower()}%"
        query = query.where(or_(func.lower(Source.name).like(needle), func.lower(Source.display_name).like(needle), func.lower(Source.organization).like(needle)))
    if category:
        query = query.where(Source.category == category)
    if tier:
        query = query.where(Source.tier == tier)
    if status:
        query = query.where(Source.status == status)
    if connector_type:
        query = query.where(Source.connector_type == connector_type)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = {
        "name": Source.display_name,
        "category": Source.category,
        "tier": Source.tier,
        "status": Source.status,
        "updated_at": Source.updated_at,
        "created_at": Source.created_at,
    }.get(sort_by, Source.updated_at)
    order = asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)
    sources = list(db.scalars(query.order_by(order).offset((page - 1) * limit).limit(limit)).unique().all())
    return SourceListResult(sources=sources, total=total, page=page, limit=limit)


def get_source_or_raise(db: Session, source_id: int, *, include_deleted: bool = False) -> Source:
    """Return a source with relationships or raise a registry error."""
    source = db.scalar(
        select(Source)
        .where(Source.id == source_id)
        .options(selectinload(Source.configuration), selectinload(Source.credentials), selectinload(Source.versions))
    )
    if source is None or (source.status == SourceStatus.DELETED.value and not include_deleted):
        raise SourceRegistryError("Source was not found", "SOURCE_NOT_FOUND", 404)
    return source


def create_source(db: Session, *, actor: User, payload: SourceCreate, request_id: str | None = None, ip_address: str | None = None) -> Source:
    """Create a source and initial configuration/version."""
    existing = db.scalar(select(Source).where(Source.name == payload.name))
    if existing is not None and existing.status != SourceStatus.DELETED.value:
        raise SourceRegistryError("A source with this name already exists", "SOURCE_ALREADY_EXISTS", 409)

    source = Source(
        name=payload.name,
        display_name=payload.display_name,
        description=payload.description,
        category=payload.category,
        tier=payload.tier,
        organization=payload.organization,
        classification=payload.classification,
        supported_capabilities=payload.supported_capabilities,
        connector_type=payload.connector_type,
        connector_id=payload.connector_id,
        authentication_type=payload.authentication_type,
        status=payload.status,
        is_active=payload.status != SourceStatus.DISABLED.value,
    )
    db.add(source)
    db.flush()
    source.configuration = _configuration_from_payload(payload.configuration, source.id, actor.id, payload.tier)
    _replace_credentials(db, source, payload.credentials)
    _record_version(db, source, actor, "create", None, _source_snapshot(source), payload.reason, request_id)
    _audit(db, actor, "admin.source.create", source, payload.reason, request_id, ip_address, previous=None, new=_source_snapshot(source))

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise SourceRegistryError("A source with this name already exists", "SOURCE_ALREADY_EXISTS", 409) from exc
    db.refresh(source)
    return get_source_or_raise(db, source.id)


def update_source(db: Session, *, actor: User, source: Source, payload: SourceUpdate, request_id: str | None = None, ip_address: str | None = None) -> Source:
    """Update source identity/configuration and write a version record."""
    previous = _source_snapshot(source)
    for field in ("display_name", "description", "category", "tier", "organization", "classification", "supported_capabilities", "connector_type", "connector_id", "authentication_type"):
        value = getattr(payload, field)
        if value is not None:
            setattr(source, field, value)

    if payload.configuration is not None:
        _apply_configuration(source.configuration, payload.configuration, actor.id, source.tier)
    elif source.configuration and payload.tier is not None and source.configuration.confidence_weight == previous.get("configuration", {}).get("confidence_weight"):
        source.configuration.confidence_weight = default_confidence_for_tier(source.tier)
        source.configuration.last_modified_by_user_id = actor.id

    if payload.credentials is not None:
        _replace_credentials(db, source, payload.credentials)

    db.flush()
    new = _source_snapshot(source)
    _record_version(db, source, actor, "update", previous, new, payload.reason, request_id)
    _audit(db, actor, "admin.source.update", source, payload.reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    db.refresh(source)
    return get_source_or_raise(db, source.id)


def update_source_status(db: Session, *, actor: User, source: Source, payload: SourceStatusUpdate, request_id: str | None = None, ip_address: str | None = None) -> Source:
    """Update operational status without changing connector details."""
    previous = _source_snapshot(source)
    source.status = payload.status
    source.is_active = payload.status == SourceStatus.ENABLED.value
    db.flush()
    new = _source_snapshot(source)
    _record_version(db, source, actor, "status", previous, new, payload.reason, request_id)
    _audit(db, actor, "admin.source.status", source, payload.reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    db.refresh(source)
    return get_source_or_raise(db, source.id)


def soft_delete_source(db: Session, *, actor: User, source: Source, reason: str, request_id: str | None = None, ip_address: str | None = None) -> Source:
    """Soft-delete a source so historical provenance remains intact."""
    reason = reason.strip()
    if not reason:
        raise SourceRegistryError("A reason is required", "REASON_REQUIRED")
    previous = _source_snapshot(source)
    source.status = SourceStatus.DELETED.value
    source.is_active = False
    source.deleted_at = datetime.now(UTC)
    source.deleted_by_user_id = actor.id
    db.flush()
    new = _source_snapshot(source)
    _record_version(db, source, actor, "delete", previous, new, reason, request_id)
    _audit(db, actor, "admin.source.delete", source, reason, request_id, ip_address, previous=previous, new=new)
    db.commit()
    db.refresh(source)
    return source


def source_to_summary(source: Source) -> SourceSummary:
    """Serialize a source list row."""
    configuration = source.configuration
    return SourceSummary(
        id=source.id,
        name=source.name,
        display_name=source.display_name,
        category=source.category,
        tier=source.tier,
        status=source.status,
        connector_type=source.connector_type,
        connector_id=source.connector_id,
        authentication_type=source.authentication_type,
        supported_capabilities=source.supported_capabilities or [],
        refresh_policy=configuration.refresh_policy if configuration else "manual",
        confidence_weight=configuration.confidence_weight if configuration else default_confidence_for_tier(source.tier),
        last_updated_at=source.updated_at,
    )


def source_list_payload(result: SourceListResult) -> SourceListPayload:
    """Serialize paginated source list payload."""
    return SourceListPayload(
        sources=[source_to_summary(source) for source in result.sources],
        total=result.total,
        page=result.page,
        limit=result.limit,
        has_next=result.page * result.limit < result.total,
        has_prev=result.page > 1,
    )


def source_to_read(db: Session, source: Source) -> SourceRead:
    """Serialize source detail with masked credentials and recent audit."""
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
            .where(AuditLog.target_type == "source", AuditLog.target_id == str(source.id))
            .order_by(AuditLog.created_at.desc())
            .limit(10)
        ).all()
    ]
    summary = source_to_summary(source).model_dump()
    return SourceRead(
        **summary,
        description=source.description,
        organization=source.organization,
        classification=source.classification,
        is_active=source.is_active,
        configuration=source.configuration,
        credentials=[_credential_read(credential) for credential in source.credentials],
        version_history=source.versions[:10],
        recent_activity=recent_activity,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


def _configuration_from_payload(payload: SourceConfigurationInput, source_id: int, actor_id: int, tier: str) -> SourceConfiguration:
    confidence_weight = payload.confidence_weight if payload.confidence_weight is not None else default_confidence_for_tier(tier)
    return SourceConfiguration(
        source_id=source_id,
        base_url=payload.base_url,
        headers=payload.headers,
        parser=payload.parser,
        connector_config=payload.connector_config,
        refresh_policy=payload.refresh_policy,
        custom_cron=payload.custom_cron,
        timeout_seconds=payload.timeout_seconds,
        retry_count=payload.retry_count,
        rate_limit_per_minute=payload.rate_limit_per_minute,
        backoff_policy=payload.backoff_policy,
        freshness_window_minutes=payload.freshness_window_minutes,
        confidence_weight=confidence_weight,
        trust_level=payload.trust_level,
        verification_required=payload.verification_required,
        parser_version=payload.parser_version,
        connector_version=payload.connector_version,
        last_verified_at=payload.last_verified_at,
        last_modified_by_user_id=actor_id,
        notes=payload.notes,
    )


def _apply_configuration(configuration: SourceConfiguration, payload: SourceConfigurationInput, actor_id: int, tier: str) -> None:
    configuration.base_url = payload.base_url
    configuration.headers = payload.headers
    configuration.parser = payload.parser
    configuration.connector_config = payload.connector_config
    configuration.refresh_policy = payload.refresh_policy
    configuration.custom_cron = payload.custom_cron
    configuration.timeout_seconds = payload.timeout_seconds
    configuration.retry_count = payload.retry_count
    configuration.rate_limit_per_minute = payload.rate_limit_per_minute
    configuration.backoff_policy = payload.backoff_policy
    configuration.freshness_window_minutes = payload.freshness_window_minutes
    configuration.confidence_weight = payload.confidence_weight if payload.confidence_weight is not None else default_confidence_for_tier(tier)
    configuration.trust_level = payload.trust_level
    configuration.verification_required = payload.verification_required
    configuration.parser_version = payload.parser_version
    configuration.connector_version = payload.connector_version
    configuration.last_verified_at = payload.last_verified_at
    configuration.last_modified_by_user_id = actor_id
    configuration.notes = payload.notes


def _replace_credentials(db: Session, source: Source, credentials: list[SourceCredentialInput]) -> None:
    existing_by_key = {credential.key: credential for credential in source.credentials}
    incoming_keys = {credential.key for credential in credentials}
    for key, credential in list(existing_by_key.items()):
        if key not in incoming_keys:
            db.delete(credential)
    for item in credentials:
        credential = existing_by_key.get(item.key)
        secret_hash = _hash_secret(item.secret_value) if item.secret_value else None
        if credential is None:
            db.add(
                SourceCredential(
                    source_id=source.id,
                    key=item.key,
                    label=item.label,
                    secret_type=item.secret_type,
                    secret_reference=item.secret_reference,
                    encrypted_value=secret_hash,
                    is_configured=bool(item.secret_value or item.secret_reference),
                    last_rotated_at=datetime.now(UTC) if item.secret_value else None,
                )
            )
        else:
            credential.label = item.label
            credential.secret_type = item.secret_type
            credential.secret_reference = item.secret_reference
            if item.secret_value:
                credential.encrypted_value = secret_hash
                credential.is_configured = True
                credential.last_rotated_at = datetime.now(UTC)
            elif item.secret_reference:
                credential.is_configured = True


def _credential_read(credential: SourceCredential):
    from app.schemas.source_registry import SourceCredentialRead

    return SourceCredentialRead(
        id=credential.id,
        key=credential.key,
        label=credential.label,
        secret_type=credential.secret_type,
        secret_reference=credential.secret_reference,
        is_configured=credential.is_configured,
        masked_value="********" if credential.is_configured else "",
        last_rotated_at=credential.last_rotated_at,
    )


def _hash_secret(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_snapshot(source: Source) -> dict[str, Any]:
    configuration = source.configuration
    return {
        "id": source.id,
        "name": source.name,
        "display_name": source.display_name,
        "category": source.category,
        "tier": source.tier,
        "organization": source.organization,
        "classification": source.classification,
        "supported_capabilities": source.supported_capabilities or [],
        "connector_type": source.connector_type,
        "connector_id": source.connector_id,
        "authentication_type": source.authentication_type,
        "status": source.status,
        "is_active": source.is_active,
        "configuration": {
            "base_url": configuration.base_url,
            "refresh_policy": configuration.refresh_policy,
            "timeout_seconds": configuration.timeout_seconds,
            "retry_count": configuration.retry_count,
            "rate_limit_per_minute": configuration.rate_limit_per_minute,
            "confidence_weight": configuration.confidence_weight,
            "trust_level": configuration.trust_level,
            "verification_required": configuration.verification_required,
            "parser_version": configuration.parser_version,
            "connector_version": configuration.connector_version,
        }
        if configuration
        else None,
        "credentials": [{"key": credential.key, "secret_type": credential.secret_type, "is_configured": credential.is_configured} for credential in source.credentials],
    }


def _next_version(source: Source) -> int:
    if not source.versions:
        return 1
    return max(version.version for version in source.versions) + 1


def _record_version(db: Session, source: Source, actor: User, change_type: str, previous: dict[str, Any] | None, new: dict[str, Any] | None, reason: str | None, request_id: str | None) -> None:
    db.add(
        SourceVersion(
            source_id=source.id,
            version=_next_version(source),
            actor_user_id=actor.id,
            change_type=change_type,
            reason=reason,
            previous_values=previous,
            new_values=new,
            request_id=request_id,
        )
    )


def _audit(db: Session, actor: User, action: str, source: Source, reason: str | None, request_id: str | None, ip_address: str | None, previous: dict[str, Any] | None, new: dict[str, Any] | None) -> None:
    record_audit_event(
        db,
        actor=actor,
        action=action,
        target_type="source",
        target_id=str(source.id),
        result="success",
        reason=reason,
        request_id=request_id,
        ip_address=ip_address,
        metadata={"previous": previous, "new": new},
        commit=False,
    )



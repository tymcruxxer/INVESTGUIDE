"""Audit service helpers for privileged operations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def record_audit_event(
    db: Session,
    *,
    actor: User | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    result: str = "success",
    reason: str | None = None,
    ip_address: str | None = None,
    request_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> AuditLog:
    """Record an auditable privileged action."""
    event = AuditLog(
        actor_user_id=actor.id if actor else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        result=result,
        reason=reason,
        ip_address=ip_address,
        request_id=request_id,
        occurred_at=datetime.now(UTC),
        metadata_json=metadata,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    return event

"""Sensitive action infrastructure for future privileged workflows."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.models.user import User


class SensitiveActionStatus(StrEnum):
    """Lifecycle values for future confirmation workflows."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SensitiveActionRequest(TimestampMixin, Base):
    """Future-ready request record for re-auth/MFA/confirmation flows."""

    __tablename__ = "sensitive_action_requests"
    __table_args__ = (
        Index("ix_sensitive_action_requests_user_id", "user_id"),
        Index("ix_sensitive_action_requests_action", "action"),
        Index("ix_sensitive_action_requests_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(150), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=SensitiveActionStatus.PENDING.value)
    confirmation_token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    required_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship("User")

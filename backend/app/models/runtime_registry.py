"""Execution Runtime Registry models.

Runtime definitions describe how connector implementations will execute in the
future. They are metadata and contract records only; no connector execution is
performed by this registry.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.connector_registry import Connector
    from app.models.user import User


class RuntimeStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class RuntimeCapabilityName(StrEnum):
    CONFIGURATION_VALIDATION = "configuration_validation"
    RUNTIME_PREPARATION = "runtime_preparation"
    CONNECTOR_ACQUISITION = "connector_acquisition"
    ABSTRACT_EXECUTION = "abstract_execution"
    RESULT_COLLECTION = "result_collection"
    OUTPUT_VALIDATION = "output_validation"
    PROVENANCE_TRACKING = "provenance_tracking"
    DRY_RUN = "dry_run"
    MANUAL_EXECUTION_CONTRACT = "manual_execution_contract"
    AUTOMATIC_EXECUTION_CONTRACT = "automatic_execution_contract"


class RuntimeValidationStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class RuntimeExecutionState(StrEnum):
    CREATED = "created"
    VALIDATED = "validated"
    PREPARED = "prepared"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RuntimeResultStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    PARTIAL = "partial"
    VALIDATION_FAILED = "validation_failed"


class RuntimeCompatibilityStatus(StrEnum):
    COMPATIBLE = "compatible"
    WARNING = "warning"
    INCOMPATIBLE = "incompatible"


class RuntimeDefinition(TimestampMixin, Base):
    """Reusable execution runtime definition."""

    __tablename__ = "runtime_definitions"
    __table_args__ = (
        UniqueConstraint("name", name="uq_runtime_definitions_name"),
        Index("ix_runtime_definitions_status", "status"),
        Index("ix_runtime_definitions_runtime_class", "runtime_class"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False, default="1.0.0", server_default="1.0.0")
    runtime_class: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=RuntimeStatus.DRAFT.value, server_default=RuntimeStatus.DRAFT.value)
    supported_connector_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    lifecycle_states: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=lambda: [item.value for item in RuntimeExecutionState])
    result_statuses: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=lambda: [item.value for item in RuntimeResultStatus])
    runtime_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    classification: Mapped[str | None] = mapped_column(String(120), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    archived_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    capabilities: Mapped[list["RuntimeCapability"]] = relationship(back_populates="runtime", cascade="all, delete-orphan")
    compatibilities: Mapped[list["RuntimeCompatibility"]] = relationship(back_populates="runtime", cascade="all, delete-orphan")
    versions: Mapped[list["RuntimeVersion"]] = relationship(back_populates="runtime", cascade="all, delete-orphan", order_by="RuntimeVersion.id.desc()")
    validations: Mapped[list["RuntimeValidation"]] = relationship(back_populates="runtime", cascade="all, delete-orphan", order_by="RuntimeValidation.id.desc()")
    archived_by: Mapped["User | None"] = relationship("User")


class RuntimeCapability(TimestampMixin, Base):
    """Capability supported by a runtime implementation contract."""

    __tablename__ = "runtime_capabilities"
    __table_args__ = (
        UniqueConstraint("runtime_id", "capability", name="uq_runtime_capabilities_runtime_capability"),
        Index("ix_runtime_capabilities_capability", "capability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    runtime_id: Mapped[int] = mapped_column(ForeignKey("runtime_definitions.id", ondelete="CASCADE"), nullable=False)
    capability: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    runtime: Mapped[RuntimeDefinition] = relationship(back_populates="capabilities")


class RuntimeCompatibility(TimestampMixin, Base):
    """Compatibility metadata between a runtime and connector definition."""

    __tablename__ = "runtime_compatibilities"
    __table_args__ = (
        UniqueConstraint("runtime_id", "connector_id", name="uq_runtime_compatibilities_runtime_connector"),
        Index("ix_runtime_compatibilities_connector_id", "connector_id"),
        Index("ix_runtime_compatibilities_status", "compatibility_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    runtime_id: Mapped[int] = mapped_column(ForeignKey("runtime_definitions.id", ondelete="CASCADE"), nullable=False)
    connector_id: Mapped[int] = mapped_column(ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(80), nullable=False)
    compatibility_status: Mapped[str] = mapped_column(String(40), nullable=False, default=RuntimeCompatibilityStatus.COMPATIBLE.value, server_default=RuntimeCompatibilityStatus.COMPATIBLE.value)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    runtime: Mapped[RuntimeDefinition] = relationship(back_populates="compatibilities")
    connector: Mapped["Connector"] = relationship("Connector")


class RuntimeVersion(TimestampMixin, Base):
    """Immutable runtime definition version record."""

    __tablename__ = "runtime_versions"
    __table_args__ = (
        Index("ix_runtime_versions_runtime_id", "runtime_id"),
        Index("ix_runtime_versions_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    runtime_id: Mapped[int] = mapped_column(ForeignKey("runtime_definitions.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_type: Mapped[str] = mapped_column(String(80), nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    runtime: Mapped[RuntimeDefinition] = relationship(back_populates="versions")
    actor: Mapped["User | None"] = relationship("User")


class RuntimeValidation(TimestampMixin, Base):
    """Stored validation-only runtime readiness result."""

    __tablename__ = "runtime_validations"
    __table_args__ = (
        Index("ix_runtime_validations_runtime_id", "runtime_id"),
        Index("ix_runtime_validations_status", "status"),
        Index("ix_runtime_validations_request_id", "request_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    runtime_id: Mapped[int | None] = mapped_column(ForeignKey("runtime_definitions.id", ondelete="SET NULL"), nullable=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    connector_id: Mapped[int | None] = mapped_column(ForeignKey("connectors.id", ondelete="SET NULL"), nullable=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    errors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    checked_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    execution_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    result_contract: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    runtime: Mapped[RuntimeDefinition | None] = relationship(back_populates="validations")
    actor: Mapped["User | None"] = relationship("User")

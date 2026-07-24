"""Execution Runtime Registry schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.runtime_registry import (
    RuntimeCapabilityName,
    RuntimeExecutionState,
    RuntimeResultStatus,
    RuntimeStatus,
    RuntimeValidationStatus,
)

RuntimeStatusValue = Literal["draft", "active", "deprecated", "disabled", "archived"]
RuntimeCapabilityValue = Literal[
    "configuration_validation",
    "runtime_preparation",
    "connector_acquisition",
    "abstract_execution",
    "result_collection",
    "output_validation",
    "provenance_tracking",
    "dry_run",
    "manual_execution_contract",
    "automatic_execution_contract",
]
RuntimeValidationStatusValue = Literal["passed", "warning", "failed"]
RuntimeExecutionStateValue = Literal["created", "validated", "prepared", "executing", "completed", "failed", "cancelled"]
RuntimeResultStatusValue = Literal["success", "failure", "cancelled", "partial", "validation_failed"]


class ExecutionContextContract(BaseModel):
    """Canonical runtime context passed to future runtime implementations."""

    job_id: int | None = None
    source_id: int | None = None
    connector_id: int | None = None
    execution_id: int | None = None
    trigger_type: str = Field(default="manual", max_length=80)
    correlation_id: str | None = Field(default=None, max_length=120)
    request_id: str | None = Field(default=None, max_length=120)
    operator_user_id: int | None = None
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    timeout_seconds: int = Field(default=30, ge=1, le=3600)
    retry_number: int = Field(default=0, ge=0, le=20)
    priority: str = Field(default="normal", max_length=40)
    dry_run: bool = True
    manual: bool = True


class ExecutionResultContract(BaseModel):
    """Standard future execution result envelope without payload data."""

    status: RuntimeResultStatusValue
    duration_ms: int | None = Field(default=None, ge=0)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    output_metadata: dict[str, Any] = Field(default_factory=dict)
    provenance_reference: str | None = None


class RuntimeCapabilityInput(BaseModel):
    capability: RuntimeCapabilityValue
    description: str | None = None


class RuntimeBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    display_name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    version: str = Field(default="1.0.0", min_length=1, max_length=80)
    runtime_class: str = Field(min_length=3, max_length=255)
    status: RuntimeStatusValue = RuntimeStatus.DRAFT.value
    supported_connector_types: list[str] = Field(default_factory=list)
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    vendor: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    change_summary: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
        if not normalized:
            raise ValueError("Runtime name is required")
        return normalized

    @field_validator("supported_connector_types")
    @classmethod
    def normalize_connector_types(cls, value: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in value if item.strip()})


class RuntimeCreate(RuntimeBase):
    capabilities: list[RuntimeCapabilityInput] = Field(default_factory=list)
    reason: str = Field(min_length=3, max_length=1000)


class RuntimeUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    version: str | None = Field(default=None, min_length=1, max_length=80)
    runtime_class: str | None = Field(default=None, min_length=3, max_length=255)
    status: RuntimeStatusValue | None = None
    supported_connector_types: list[str] | None = None
    runtime_metadata: dict[str, Any] | None = None
    vendor: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    change_summary: str | None = None
    capabilities: list[RuntimeCapabilityInput] | None = None
    reason: str = Field(min_length=3, max_length=1000)

    @field_validator("supported_connector_types")
    @classmethod
    def normalize_optional_connector_types(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return sorted({item.strip().lower() for item in value if item.strip()})


class RuntimeValidationRequest(BaseModel):
    """Validation request. It never executes a connector or contacts a source."""

    runtime_id: int | None = None
    source_id: int | None = None
    connector_id: int | None = None
    job_id: int | None = None
    execution_id: int | None = None
    context: ExecutionContextContract = Field(default_factory=ExecutionContextContract)
    reason: str = Field(default="Runtime metadata validation", min_length=3, max_length=1000)


class RuntimeCapabilityRead(BaseModel):
    id: int
    capability: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RuntimeCompatibilityRead(BaseModel):
    id: int
    connector_id: int
    connector_type: str
    compatibility_status: str
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RuntimeVersionRead(BaseModel):
    id: int
    version: str
    change_type: str
    change_summary: str | None = None
    previous_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    request_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RuntimeValidationRead(BaseModel):
    id: int
    runtime_id: int | None = None
    source_id: int | None = None
    connector_id: int | None = None
    status: str
    summary: str
    errors: list[str]
    warnings: list[str]
    checked_fields: list[str]
    execution_context: dict[str, Any]
    result_contract: dict[str, Any]
    request_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RuntimeSummary(BaseModel):
    id: int
    name: str
    display_name: str
    version: str
    runtime_class: str
    status: str
    supported_connector_types: list[str]
    capabilities: list[str]
    compatible_connector_count: int
    last_updated_at: datetime | None = None


class RuntimeRead(RuntimeSummary):
    description: str | None = None
    runtime_metadata: dict[str, Any]
    vendor: str | None = None
    author: str | None = None
    classification: str | None = None
    lifecycle_states: list[str]
    result_statuses: list[str]
    change_summary: str | None = None
    is_active: bool
    capability_details: list[RuntimeCapabilityRead] = Field(default_factory=list)
    compatibility_details: list[RuntimeCompatibilityRead] = Field(default_factory=list)
    version_history: list[RuntimeVersionRead] = Field(default_factory=list)
    validation_history: list[RuntimeValidationRead] = Field(default_factory=list)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RuntimeListPayload(BaseModel):
    runtimes: list[RuntimeSummary]
    total: int
    page: int
    limit: int
    has_next: bool = False
    has_prev: bool = False


class RuntimeCapabilitiesPayload(BaseModel):
    runtime_statuses: list[str]
    lifecycle_states: list[str]
    result_statuses: list[str]
    validation_statuses: list[str]
    capabilities: list[str]
    supported_connector_types: list[str]


RUNTIME_METADATA = RuntimeCapabilitiesPayload(
    runtime_statuses=[item.value for item in RuntimeStatus],
    lifecycle_states=[item.value for item in RuntimeExecutionState],
    result_statuses=[item.value for item in RuntimeResultStatus],
    validation_statuses=[item.value for item in RuntimeValidationStatus],
    capabilities=[item.value for item in RuntimeCapabilityName],
    supported_connector_types=[
        "csv_importer",
        "html_scraper",
        "json_feed",
        "pdf_extractor",
        "rest_api",
        "rss",
        "xml_feed",
    ],
)

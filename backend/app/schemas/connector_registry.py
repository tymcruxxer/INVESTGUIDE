"""Connector Registry schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.connector_registry import (
    ConnectorAuthStrategy,
    ConnectorCapabilityName,
    ConnectorKind,
    ConnectorLifecycle,
    ConnectorValidationStatus,
)

ConnectorKindValue = Literal[
    "rest_api",
    "graphql",
    "rss",
    "html_scraper",
    "pdf_extractor",
    "csv_importer",
    "json_feed",
    "xml_feed",
    "database",
    "file_upload",
    "manual",
    "future_custom_connector",
]
ConnectorLifecycleValue = Literal["draft", "active", "deprecated", "disabled", "archived"]
ConnectorAuthStrategyValue = Literal["none", "api_key", "bearer_token", "oauth2", "username_password", "cookie", "custom"]
ConnectorValidationStatusValue = Literal["passed", "warning", "failed"]
ConnectorCapabilityValue = Literal[
    "market_prices",
    "company_filings",
    "annual_reports",
    "interim_reports",
    "trading_updates",
    "corporate_actions",
    "dividends",
    "news",
    "macroeconomic_indicators",
    "currency_rates",
    "commodity_prices",
    "weather",
    "research_reports",
    "esg_data",
]

SECRET_FIELD_HINTS = ("secret", "password", "token", "credential", "private_key")


class ConnectorCapabilityInput(BaseModel):
    """Connector capability assignment."""

    capability: ConnectorCapabilityValue
    description: str | None = None


class ConnectorConfigurationSchemaInput(BaseModel):
    """Configuration metadata for a connector implementation."""

    schema: dict[str, Any] = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)
    endpoint_templates: dict[str, Any] = Field(default_factory=dict)
    headers_schema: dict[str, Any] = Field(default_factory=dict)
    pagination_strategy: str | None = Field(default=None, max_length=120)
    parser_identifier: str | None = Field(default=None, max_length=255)
    rate_limit_policy: dict[str, Any] = Field(default_factory=dict)
    default_timeout_seconds: int = Field(default=30, ge=1, le=300)
    default_retry_count: int = Field(default=3, ge=0, le=10)
    request_method: str = Field(default="GET", max_length=20)
    compression: str | None = Field(default=None, max_length=80)
    user_agent: str | None = Field(default="InvestGuideConnector/1.0", max_length=255)

    @field_validator("request_method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"GET", "POST", "PUT", "PATCH", "HEAD"}:
            raise ValueError("Unsupported request method")
        return normalized

    @field_validator("required_fields")
    @classmethod
    def normalize_required_fields(cls, value: list[str]) -> list[str]:
        return sorted({item.strip() for item in value if item.strip()})


class ConnectorConfigurationSchemaRead(ConnectorConfigurationSchemaInput):
    id: int
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConnectorBase(BaseModel):
    """Shared connector identity fields."""

    name: str = Field(min_length=2, max_length=120)
    display_name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    version: str = Field(default="1.0.0", min_length=1, max_length=80)
    vendor: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    connector_type: ConnectorKindValue
    lifecycle: ConnectorLifecycleValue = ConnectorLifecycle.DRAFT.value
    authentication_strategy: ConnectorAuthStrategyValue = ConnectorAuthStrategy.NONE.value
    configuration_schema: dict[str, Any] = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)
    supported_source_categories: list[str] = Field(default_factory=list)
    compatibility_notes: str | None = None
    deprecation_status: bool = False
    change_summary: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
        if not normalized:
            raise ValueError("Connector name is required")
        return normalized

    @field_validator("required_fields", "supported_source_categories")
    @classmethod
    def normalize_list(cls, value: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in value if item.strip()})


class ConnectorCreate(ConnectorBase):
    """Create connector request."""

    capabilities: list[ConnectorCapabilityInput] = Field(default_factory=list)
    configuration_contract: ConnectorConfigurationSchemaInput = Field(default_factory=ConnectorConfigurationSchemaInput)
    reason: str = Field(min_length=3, max_length=1000)


class ConnectorUpdate(BaseModel):
    """Patch connector request."""

    display_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    version: str | None = Field(default=None, min_length=1, max_length=80)
    vendor: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    connector_type: ConnectorKindValue | None = None
    lifecycle: ConnectorLifecycleValue | None = None
    authentication_strategy: ConnectorAuthStrategyValue | None = None
    configuration_schema: dict[str, Any] | None = None
    required_fields: list[str] | None = None
    supported_source_categories: list[str] | None = None
    compatibility_notes: str | None = None
    deprecation_status: bool | None = None
    change_summary: str | None = None
    capabilities: list[ConnectorCapabilityInput] | None = None
    configuration_contract: ConnectorConfigurationSchemaInput | None = None
    reason: str = Field(min_length=3, max_length=1000)

    @field_validator("required_fields", "supported_source_categories")
    @classmethod
    def normalize_optional_list(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return sorted({item.strip().lower() for item in value if item.strip()})


class ConnectorStatusUpdate(BaseModel):
    """Patch connector lifecycle request."""

    lifecycle: ConnectorLifecycleValue
    reason: str = Field(min_length=3, max_length=1000)


class ConnectorValidationRequest(BaseModel):
    """Connector validation request. This is metadata-only and never connects outbound."""

    configuration: dict[str, Any] = Field(default_factory=dict)
    source_id: int | None = None
    reason: str = Field(default="Connector metadata validation", min_length=3, max_length=1000)


class ConnectorCapabilityRead(BaseModel):
    id: int
    capability: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ConnectorVersionRead(BaseModel):
    id: int
    version: str
    change_type: str
    change_summary: str | None = None
    compatibility_notes: str | None = None
    previous_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    request_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConnectorValidationRead(BaseModel):
    id: int
    status: str
    summary: str
    errors: list[str]
    warnings: list[str]
    checked_fields: list[str]
    requested_config: dict[str, Any]
    request_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConnectorSourceBinding(BaseModel):
    id: int
    name: str
    display_name: str
    category: str
    status: str
    connector_type: str


class ConnectorSummary(BaseModel):
    id: int
    name: str
    display_name: str
    version: str
    connector_type: str
    lifecycle: str
    authentication_strategy: str
    classification: str | None = None
    capabilities: list[str]
    compatible_source_count: int
    last_updated_at: datetime | None = None


class ConnectorRead(ConnectorSummary):
    description: str | None = None
    vendor: str | None = None
    author: str | None = None
    configuration_schema: dict[str, Any]
    required_fields: list[str]
    supported_source_categories: list[str]
    compatibility_notes: str | None = None
    deprecation_status: bool
    change_summary: str | None = None
    is_active: bool
    configuration_contract: ConnectorConfigurationSchemaRead | None = None
    capability_details: list[ConnectorCapabilityRead] = Field(default_factory=list)
    version_history: list[ConnectorVersionRead] = Field(default_factory=list)
    validation_history: list[ConnectorValidationRead] = Field(default_factory=list)
    compatible_sources: list[ConnectorSourceBinding] = Field(default_factory=list)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConnectorListPayload(BaseModel):
    connectors: list[ConnectorSummary]
    total: int
    page: int
    limit: int
    has_next: bool = False
    has_prev: bool = False


class ConnectorCapabilitiesPayload(BaseModel):
    connector_types: list[str]
    lifecycle_states: list[str]
    authentication_strategies: list[str]
    capabilities: list[str]
    validation_statuses: list[str]


CONNECTOR_METADATA = ConnectorCapabilitiesPayload(
    connector_types=[item.value for item in ConnectorKind],
    lifecycle_states=[item.value for item in ConnectorLifecycle],
    authentication_strategies=[item.value for item in ConnectorAuthStrategy],
    capabilities=[item.value for item in ConnectorCapabilityName],
    validation_statuses=[item.value for item in ConnectorValidationStatus],
)

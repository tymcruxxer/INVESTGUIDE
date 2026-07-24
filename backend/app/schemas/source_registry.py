"""Data source registry schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.source_registry import (
    AuthenticationType,
    ConnectorType,
    RefreshPolicy,
    SourceCapability,
    SourceCategory,
    SourceStatus,
    SourceTier,
)

SourceCategoryValue = Literal[
    "market",
    "government",
    "regulator",
    "company",
    "research",
    "news",
    "international",
    "commodity",
    "currency",
    "weather",
    "alternative_intelligence",
    "esg",
    "corporate_registry",
]
SourceTierValue = Literal["tier_1", "tier_2", "tier_3"]
SourceStatusValue = Literal["enabled", "disabled", "maintenance", "deleted"]
ConnectorTypeValue = Literal[
    "rest_api",
    "rss",
    "website",
    "html_scraper",
    "pdf",
    "csv",
    "json",
    "xml",
    "manual_upload",
    "database",
    "future_connector",
]
AuthenticationTypeValue = Literal["none", "api_key", "oauth", "username_password", "token", "cookie", "custom"]
RefreshPolicyValue = Literal["manual", "hourly", "daily", "weekly", "monthly", "custom_cron"]
SourceCapabilityValue = Literal[
    "market_prices",
    "corporate_actions",
    "dividends",
    "annual_reports",
    "interim_reports",
    "trading_updates",
    "news",
    "economic_indicators",
    "exchange_rates",
    "commodity_prices",
    "weather",
    "research_reports",
]


def default_confidence_for_tier(tier: str) -> float:
    """Return the default confidence weight for a trust tier."""
    return {SourceTier.TIER_1.value: 1.0, SourceTier.TIER_2.value: 0.85, SourceTier.TIER_3.value: 0.7}.get(tier, 0.7)


class SourceCredentialInput(BaseModel):
    """Credential input. Secret value is write-only and never returned."""

    key: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=255)
    secret_type: AuthenticationTypeValue
    secret_value: str | None = Field(default=None, max_length=4000)
    secret_reference: str | None = Field(default=None, max_length=255)

    @field_validator("key")
    @classmethod
    def normalize_key(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "_")


class SourceCredentialRead(BaseModel):
    """Safe credential metadata response."""

    id: int
    key: str
    label: str
    secret_type: str
    secret_reference: str | None = None
    is_configured: bool
    masked_value: str = "********"
    last_rotated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SourceConfigurationInput(BaseModel):
    """Configurable source connector and operational settings."""

    base_url: str | None = Field(default=None, max_length=1000)
    headers: dict[str, Any] = Field(default_factory=dict)
    parser: dict[str, Any] = Field(default_factory=dict)
    connector_config: dict[str, Any] = Field(default_factory=dict)
    refresh_policy: RefreshPolicyValue = RefreshPolicy.MANUAL.value
    custom_cron: str | None = Field(default=None, max_length=120)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=10000)
    backoff_policy: str | None = Field(default="exponential", max_length=120)
    freshness_window_minutes: int | None = Field(default=None, ge=1)
    confidence_weight: float | None = Field(default=None, ge=0, le=1)
    trust_level: str = Field(default="standard", max_length=120)
    verification_required: bool = True
    parser_version: str = Field(default="1", max_length=80)
    connector_version: str = Field(default="1", max_length=80)
    last_verified_at: datetime | None = None
    notes: str | None = None


class SourceConfigurationRead(BaseModel):
    """Source configuration response."""

    id: int
    base_url: str | None = None
    headers: dict[str, Any]
    parser: dict[str, Any]
    connector_config: dict[str, Any]
    refresh_policy: str
    custom_cron: str | None = None
    timeout_seconds: int
    retry_count: int
    rate_limit_per_minute: int | None = None
    backoff_policy: str | None = None
    freshness_window_minutes: int | None = None
    confidence_weight: float
    trust_level: str
    verification_required: bool
    parser_version: str
    connector_version: str
    last_verified_at: datetime | None = None
    notes: str | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SourceBase(BaseModel):
    """Shared source identity fields."""

    name: str = Field(min_length=2, max_length=120)
    display_name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    category: SourceCategoryValue
    tier: SourceTierValue
    organization: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    supported_capabilities: list[SourceCapabilityValue] = Field(default_factory=list)
    connector_type: ConnectorTypeValue
    connector_id: int | None = None
    authentication_type: AuthenticationTypeValue = AuthenticationType.NONE.value
    status: SourceStatusValue = SourceStatus.DISABLED.value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
        if not normalized:
            raise ValueError("Source name is required")
        return normalized

    @field_validator("supported_capabilities")
    @classmethod
    def normalize_capabilities(cls, value: list[str]) -> list[str]:
        return sorted(set(value))


class SourceCreate(SourceBase):
    """Create source request."""

    configuration: SourceConfigurationInput = Field(default_factory=SourceConfigurationInput)
    credentials: list[SourceCredentialInput] = Field(default_factory=list)
    reason: str = Field(min_length=3, max_length=1000)


class SourceUpdate(BaseModel):
    """Patch source request."""

    display_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    category: SourceCategoryValue | None = None
    tier: SourceTierValue | None = None
    organization: str | None = Field(default=None, max_length=255)
    classification: str | None = Field(default=None, max_length=120)
    supported_capabilities: list[SourceCapabilityValue] | None = None
    connector_type: ConnectorTypeValue | None = None
    connector_id: int | None = None
    authentication_type: AuthenticationTypeValue | None = None
    configuration: SourceConfigurationInput | None = None
    credentials: list[SourceCredentialInput] | None = None
    reason: str = Field(min_length=3, max_length=1000)


class SourceStatusUpdate(BaseModel):
    """Patch source operational status request."""

    status: Literal["enabled", "disabled", "maintenance"]
    reason: str = Field(min_length=3, max_length=1000)


class SourceVersionRead(BaseModel):
    """Source version history response."""

    id: int
    version: int
    change_type: str
    reason: str | None = None
    previous_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    request_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SourceSummary(BaseModel):
    """Source list row."""

    id: int
    name: str
    display_name: str
    category: str
    tier: str
    status: str
    connector_type: str
    connector_id: int | None = None
    authentication_type: str
    supported_capabilities: list[str] = Field(default_factory=list)
    refresh_policy: str
    confidence_weight: float
    last_updated_at: datetime | None = None


class SourceRead(SourceSummary):
    """Full source detail response."""

    description: str | None = None
    organization: str | None = None
    classification: str | None = None
    is_active: bool
    configuration: SourceConfigurationRead | None = None
    credentials: list[SourceCredentialRead] = Field(default_factory=list)
    version_history: list[SourceVersionRead] = Field(default_factory=list)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SourceListPayload(BaseModel):
    """Paginated source list payload."""

    sources: list[SourceSummary]
    total: int
    page: int
    limit: int
    has_next: bool = False
    has_prev: bool = False


class SourceMetadataPayload(BaseModel):
    """Enum metadata for source registry UI."""

    categories: list[str]
    tiers: list[str]
    statuses: list[str]
    connector_types: list[str]
    authentication_types: list[str]
    refresh_policies: list[str]
    capabilities: list[str]


SOURCE_METADATA = SourceMetadataPayload(
    categories=[item.value for item in SourceCategory],
    tiers=[item.value for item in SourceTier],
    statuses=[item.value for item in SourceStatus if item != SourceStatus.DELETED],
    connector_types=[item.value for item in ConnectorType],
    authentication_types=[item.value for item in AuthenticationType],
    refresh_policies=[item.value for item in RefreshPolicy],
    capabilities=[item.value for item in SourceCapability],
)





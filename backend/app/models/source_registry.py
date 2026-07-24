"""Data source registry models for configurable ingestion sources."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.connector_registry import Connector
    from app.models.user import User


class SourceCategory(StrEnum):
    MARKET = "market"
    GOVERNMENT = "government"
    REGULATOR = "regulator"
    COMPANY = "company"
    RESEARCH = "research"
    NEWS = "news"
    INTERNATIONAL = "international"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    WEATHER = "weather"
    ALTERNATIVE_INTELLIGENCE = "alternative_intelligence"
    ESG = "esg"
    CORPORATE_REGISTRY = "corporate_registry"


class SourceTier(StrEnum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class SourceStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    DELETED = "deleted"


class ConnectorType(StrEnum):
    REST_API = "rest_api"
    RSS = "rss"
    WEBSITE = "website"
    HTML_SCRAPER = "html_scraper"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    MANUAL_UPLOAD = "manual_upload"
    DATABASE = "database"
    FUTURE_CONNECTOR = "future_connector"


class AuthenticationType(StrEnum):
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    USERNAME_PASSWORD = "username_password"
    TOKEN = "token"
    COOKIE = "cookie"
    CUSTOM = "custom"


class RefreshPolicy(StrEnum):
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM_CRON = "custom_cron"


class SourceCapability(StrEnum):
    MARKET_PRICES = "market_prices"
    CORPORATE_ACTIONS = "corporate_actions"
    DIVIDENDS = "dividends"
    ANNUAL_REPORTS = "annual_reports"
    INTERIM_REPORTS = "interim_reports"
    TRADING_UPDATES = "trading_updates"
    NEWS = "news"
    ECONOMIC_INDICATORS = "economic_indicators"
    EXCHANGE_RATES = "exchange_rates"
    COMMODITY_PRICES = "commodity_prices"
    WEATHER = "weather"
    RESEARCH_REPORTS = "research_reports"


class Source(TimestampMixin, Base):
    """External source identity and trust classification."""

    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("name", name="uq_sources_name"),
        Index("ix_sources_category", "category"),
        Index("ix_sources_tier", "tier"),
        Index("ix_sources_status", "status"),
        Index("ix_sources_connector_type", "connector_type"),
        Index("ix_sources_connector_id", "connector_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    tier: Mapped[str] = mapped_column(String(40), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    classification: Mapped[str | None] = mapped_column(String(120), nullable=True)
    supported_capabilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    connector_type: Mapped[str] = mapped_column(String(80), nullable=False)
    connector_id: Mapped[int | None] = mapped_column(ForeignKey("connectors.id", ondelete="SET NULL"), nullable=True)
    authentication_type: Mapped[str] = mapped_column(String(80), nullable=False, default=AuthenticationType.NONE.value, server_default=AuthenticationType.NONE.value)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=SourceStatus.DISABLED.value, server_default=SourceStatus.DISABLED.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    deleted_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    configuration: Mapped["SourceConfiguration"] = relationship(back_populates="source", cascade="all, delete-orphan", uselist=False)
    credentials: Mapped[list["SourceCredential"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    versions: Mapped[list["SourceVersion"]] = relationship(back_populates="source", cascade="all, delete-orphan", order_by="SourceVersion.id.desc()")
    connector: Mapped["Connector | None"] = relationship("Connector", back_populates="sources")
    deleted_by: Mapped["User | None"] = relationship("User")


class SourceConfiguration(TimestampMixin, Base):
    """Operational, connector, parser, and provenance configuration."""

    __tablename__ = "source_configurations"
    __table_args__ = (UniqueConstraint("source_id", name="uq_source_configurations_source_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    headers: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    parser: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    connector_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    refresh_policy: Mapped[str] = mapped_column(String(40), nullable=False, default=RefreshPolicy.MANUAL.value, server_default=RefreshPolicy.MANUAL.value)
    custom_cron: Mapped[str | None] = mapped_column(String(120), nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    rate_limit_per_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    backoff_policy: Mapped[str | None] = mapped_column(String(120), nullable=True)
    freshness_window_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.7, server_default="0.7")
    trust_level: Mapped[str] = mapped_column(String(120), nullable=False, default="standard", server_default="standard")
    verification_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    parser_version: Mapped[str] = mapped_column(String(80), nullable=False, default="1", server_default="1")
    connector_version: Mapped[str] = mapped_column(String(80), nullable=False, default="1", server_default="1")
    last_verified_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_modified_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[Source] = relationship(back_populates="configuration")
    last_modified_by: Mapped["User | None"] = relationship("User")


class SourceCredential(TimestampMixin, Base):
    """Credential metadata and encrypted/hashed secret placeholders.

    Secret values are never serialized back through admin APIs.
    """

    __tablename__ = "source_credentials"
    __table_args__ = (
        UniqueConstraint("source_id", "key", name="uq_source_credentials_source_key"),
        Index("ix_source_credentials_source_id", "source_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_type: Mapped[str] = mapped_column(String(80), nullable=False)
    secret_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_configured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    last_rotated_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source: Mapped[Source] = relationship(back_populates="credentials")


class SourceVersion(TimestampMixin, Base):
    """Versioned source configuration change summary."""

    __tablename__ = "source_versions"
    __table_args__ = (
        Index("ix_source_versions_source_id", "source_id"),
        Index("ix_source_versions_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_type: Mapped[str] = mapped_column(String(80), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    source: Mapped[Source] = relationship(back_populates="versions")
    actor: Mapped["User | None"] = relationship("User")



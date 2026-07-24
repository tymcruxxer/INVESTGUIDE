"""Connector Registry models for reusable ingestion execution contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.source_registry import Source
    from app.models.user import User


class ConnectorKind(StrEnum):
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    RSS = "rss"
    HTML_SCRAPER = "html_scraper"
    PDF_EXTRACTOR = "pdf_extractor"
    CSV_IMPORTER = "csv_importer"
    JSON_FEED = "json_feed"
    XML_FEED = "xml_feed"
    DATABASE = "database"
    FILE_UPLOAD = "file_upload"
    MANUAL = "manual"
    FUTURE_CUSTOM_CONNECTOR = "future_custom_connector"


class ConnectorLifecycle(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class ConnectorAuthStrategy(StrEnum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    USERNAME_PASSWORD = "username_password"
    COOKIE = "cookie"
    CUSTOM = "custom"


class ConnectorCapabilityName(StrEnum):
    MARKET_PRICES = "market_prices"
    COMPANY_FILINGS = "company_filings"
    ANNUAL_REPORTS = "annual_reports"
    INTERIM_REPORTS = "interim_reports"
    TRADING_UPDATES = "trading_updates"
    CORPORATE_ACTIONS = "corporate_actions"
    DIVIDENDS = "dividends"
    NEWS = "news"
    MACROECONOMIC_INDICATORS = "macroeconomic_indicators"
    CURRENCY_RATES = "currency_rates"
    COMMODITY_PRICES = "commodity_prices"
    WEATHER = "weather"
    RESEARCH_REPORTS = "research_reports"
    ESG_DATA = "esg_data"


class ConnectorValidationStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class Connector(TimestampMixin, Base):
    """Reusable connector definition independent of a specific source."""

    __tablename__ = "connectors"
    __table_args__ = (
        UniqueConstraint("name", name="uq_connectors_name"),
        Index("ix_connectors_connector_type", "connector_type"),
        Index("ix_connectors_lifecycle", "lifecycle"),
        Index("ix_connectors_classification", "classification"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False, default="1.0.0", server_default="1.0.0")
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    classification: Mapped[str | None] = mapped_column(String(120), nullable=True)
    connector_type: Mapped[str] = mapped_column(String(80), nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(40), nullable=False, default=ConnectorLifecycle.DRAFT.value, server_default=ConnectorLifecycle.DRAFT.value)
    authentication_strategy: Mapped[str] = mapped_column(String(80), nullable=False, default=ConnectorAuthStrategy.NONE.value, server_default=ConnectorAuthStrategy.NONE.value)
    configuration_schema: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    required_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    supported_source_categories: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    compatibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deprecation_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    archived_at: Mapped[Any | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    capabilities: Mapped[list["ConnectorCapability"]] = relationship(back_populates="connector", cascade="all, delete-orphan")
    configuration_contract: Mapped["ConnectorConfigurationSchema"] = relationship(back_populates="connector", cascade="all, delete-orphan", uselist=False)
    versions: Mapped[list["ConnectorVersion"]] = relationship(back_populates="connector", cascade="all, delete-orphan", order_by="ConnectorVersion.id.desc()")
    validations: Mapped[list["ConnectorValidation"]] = relationship(back_populates="connector", cascade="all, delete-orphan", order_by="ConnectorValidation.id.desc()")
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="connector")
    archived_by: Mapped["User | None"] = relationship("User")


class ConnectorCapability(TimestampMixin, Base):
    """Capability supported by a connector."""

    __tablename__ = "connector_capabilities"
    __table_args__ = (
        UniqueConstraint("connector_id", "capability", name="uq_connector_capabilities_connector_capability"),
        Index("ix_connector_capabilities_capability", "capability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    connector_id: Mapped[int] = mapped_column(ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    capability: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    connector: Mapped[Connector] = relationship(back_populates="capabilities")


class ConnectorConfigurationSchema(TimestampMixin, Base):
    """Configuration contract metadata. Secret values are never stored here."""

    __tablename__ = "connector_configuration_schemas"
    __table_args__ = (UniqueConstraint("connector_id", name="uq_connector_configuration_schemas_connector_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    connector_id: Mapped[int] = mapped_column(ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    schema: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    required_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    endpoint_templates: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    headers_schema: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pagination_strategy: Mapped[str | None] = mapped_column(String(120), nullable=True)
    parser_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rate_limit_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    default_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    default_retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    request_method: Mapped[str] = mapped_column(String(20), nullable=False, default="GET", server_default="GET")
    compression: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    connector: Mapped[Connector] = relationship(back_populates="configuration_contract")


class ConnectorVersion(TimestampMixin, Base):
    """Immutable connector version change record."""

    __tablename__ = "connector_versions"
    __table_args__ = (
        Index("ix_connector_versions_connector_id", "connector_id"),
        Index("ix_connector_versions_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    connector_id: Mapped[int] = mapped_column(ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_type: Mapped[str] = mapped_column(String(80), nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    compatibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    connector: Mapped[Connector] = relationship(back_populates="versions")
    actor: Mapped["User | None"] = relationship("User")


class ConnectorValidation(TimestampMixin, Base):
    """Stored connector validation result. Validation never performs network I/O."""

    __tablename__ = "connector_validations"
    __table_args__ = (
        Index("ix_connector_validations_connector_id", "connector_id"),
        Index("ix_connector_validations_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    connector_id: Mapped[int] = mapped_column(ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    errors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    checked_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    requested_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    connector: Mapped[Connector] = relationship(back_populates="validations")
    actor: Mapped["User | None"] = relationship("User")

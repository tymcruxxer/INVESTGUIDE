"""Development-only connector registry seed catalogue."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.connector_registry import Connector
from app.models.rbac import Role, UserRole
from app.models.source_registry import Source
from app.models.user import User
from app.schemas.connector_registry import ConnectorCapabilityInput, ConnectorConfigurationSchemaInput, ConnectorCreate
from app.services.connector_registry_service import create_connector
from app.services.rbac_service import OWNER_ROLE

logger = get_logger(__name__)

CONNECTOR_CATALOGUE: tuple[dict[str, object], ...] = (
    {
        "name": "generic_rest_api",
        "display_name": "Generic REST API Connector",
        "connector_type": "rest_api",
        "authentication_strategy": "api_key",
        "capabilities": ["market_prices", "macroeconomic_indicators", "currency_rates", "commodity_prices", "research_reports"],
        "source_categories": ["market", "government", "international", "commodity", "currency"],
        "schema": {"base_url": "string", "endpoint_templates": "object", "auth_reference": "secret_reference"},
        "required_fields": ["base_url"],
        "parser_identifier": "generic.rest.v1",
        "request_method": "GET",
    },
    {
        "name": "generic_rss_feed",
        "display_name": "Generic RSS Feed Connector",
        "connector_type": "rss",
        "authentication_strategy": "none",
        "capabilities": ["news", "corporate_actions", "dividends", "trading_updates"],
        "source_categories": ["news", "market", "company"],
        "schema": {"base_url": "string", "feed_path": "string"},
        "required_fields": ["base_url"],
        "parser_identifier": "generic.rss.v1",
        "request_method": "GET",
    },
    {
        "name": "generic_html_scraper",
        "display_name": "Generic HTML Scraper Connector",
        "connector_type": "html_scraper",
        "authentication_strategy": "none",
        "capabilities": ["company_filings", "annual_reports", "interim_reports", "trading_updates", "news"],
        "source_categories": ["market", "company", "government", "regulator"],
        "schema": {"base_url": "string", "selectors": "object", "robots_policy": "metadata"},
        "required_fields": ["base_url"],
        "parser_identifier": "generic.html.v1",
        "request_method": "GET",
    },
    {
        "name": "generic_pdf_extractor",
        "display_name": "Generic PDF Extractor Connector",
        "connector_type": "pdf_extractor",
        "authentication_strategy": "none",
        "capabilities": ["annual_reports", "interim_reports", "research_reports", "macroeconomic_indicators"],
        "source_categories": ["research", "government", "company"],
        "schema": {"document_url_template": "string", "extractor_profile": "string"},
        "required_fields": [],
        "parser_identifier": "generic.pdf.v1",
        "request_method": "GET",
    },
    {
        "name": "generic_csv_importer",
        "display_name": "Generic CSV Importer Connector",
        "connector_type": "csv_importer",
        "authentication_strategy": "none",
        "capabilities": ["market_prices", "dividends", "corporate_actions", "macroeconomic_indicators"],
        "source_categories": ["market", "government", "company"],
        "schema": {"columns": "object", "delimiter": "string", "encoding": "string"},
        "required_fields": [],
        "parser_identifier": "generic.csv.v1",
        "request_method": "GET",
    },
)


@dataclass(frozen=True)
class ConnectorSeedResult:
    """Summary of connector registry seed execution."""

    inserted: int
    skipped: int
    bound_sources: int


def seed_connectors(db: Session) -> ConnectorSeedResult:
    """Seed reusable connector definitions and bind existing development sources."""
    ensure_development_data_allowed()
    actor = _owner_user(db)
    inserted = 0
    skipped = 0
    bound_sources = 0
    try:
        connectors_by_name: dict[str, Connector] = {}
        for item in CONNECTOR_CATALOGUE:
            name = str(item["name"])
            connector = db.scalar(select(Connector).where(Connector.name == name))
            if connector is None:
                connector = create_connector(
                    db,
                    actor=actor,
                    payload=ConnectorCreate(
                        name=name,
                        display_name=str(item["display_name"]),
                        description=f"Development connector contract for {item['display_name']}. It defines metadata only and performs no live work.",
                        version="1.0.0",
                        vendor="InvestGuide",
                        author="InvestGuide Platform",
                        classification="development_framework",
                        connector_type=str(item["connector_type"]),
                        lifecycle="active",
                        authentication_strategy=str(item["authentication_strategy"]),
                        configuration_schema=dict(item["schema"]),
                        required_fields=list(item["required_fields"]),
                        supported_source_categories=list(item["source_categories"]),
                        compatibility_notes="Framework connector for future ingestion workers; no runtime execution is implemented.",
                        change_summary="Initial development connector seed",
                        capabilities=[ConnectorCapabilityInput(capability=str(capability), description=f"Supports {capability} payload contracts.") for capability in item["capabilities"]],
                        configuration_contract=ConnectorConfigurationSchemaInput(
                            schema=dict(item["schema"]),
                            required_fields=list(item["required_fields"]),
                            endpoint_templates={},
                            headers_schema={"allowed_headers": ["Accept", "User-Agent"]},
                            pagination_strategy="contract_defined",
                            parser_identifier=str(item["parser_identifier"]),
                            rate_limit_policy={"requests_per_minute": 30, "burst": 5},
                            default_timeout_seconds=30,
                            default_retry_count=3,
                            request_method=str(item["request_method"]),
                            user_agent="InvestGuideConnector/1.0",
                        ),
                        reason="Development connector registry seed",
                    ),
                )
                inserted += 1
            else:
                skipped += 1
            connectors_by_name[name] = connector

        db.flush()
        for source in db.scalars(select(Source)).all():
            connector = connectors_by_name.get(_connector_name_for_source(source))
            if connector is not None and source.connector_id != connector.id:
                source.connector_id = connector.id
                bound_sources += 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Connector registry seed failed; transaction rolled back")
        raise
    logger.info("Connector registry seed completed: %s inserted, %s skipped, %s sources bound", inserted, skipped, bound_sources)
    return ConnectorSeedResult(inserted=inserted, skipped=skipped, bound_sources=bound_sources)


def _connector_name_for_source(source: Source) -> str:
    if source.connector_type == "rss":
        return "generic_rss_feed"
    if source.connector_type in {"website", "html_scraper"}:
        return "generic_html_scraper"
    if source.connector_type == "pdf":
        return "generic_pdf_extractor"
    if source.connector_type == "csv":
        return "generic_csv_importer"
    return "generic_rest_api"


def _owner_user(db: Session) -> User:
    owner = db.scalar(select(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(Role.slug == OWNER_ROLE, UserRole.is_active.is_(True)))
    if owner is None:
        raise RuntimeError("RBAC Owner must be bootstrapped before seeding connector registry")
    return owner

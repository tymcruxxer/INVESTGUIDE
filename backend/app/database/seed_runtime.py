"""Development-only execution runtime registry seed catalogue."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.connector_registry import Connector
from app.models.rbac import Role, UserRole
from app.models.runtime_registry import RuntimeCompatibility, RuntimeDefinition
from app.models.user import User
from app.schemas.runtime_registry import RuntimeCapabilityInput, RuntimeCreate
from app.services.rbac_service import OWNER_ROLE
from app.services.runtime_registry_service import create_runtime

logger = get_logger(__name__)

RUNTIME_CATALOGUE: tuple[dict[str, object], ...] = (
    {
        "name": "generic_rest_runtime",
        "display_name": "Generic REST Runtime",
        "runtime_class": "investguide.runtime.GenericRestRuntime",
        "supported_connector_types": ["rest_api", "graphql", "json_feed"],
        "capabilities": ["configuration_validation", "runtime_preparation", "connector_acquisition", "abstract_execution", "result_collection", "output_validation", "provenance_tracking", "dry_run"],
    },
    {
        "name": "generic_rss_runtime",
        "display_name": "Generic RSS Runtime",
        "runtime_class": "investguide.runtime.GenericRssRuntime",
        "supported_connector_types": ["rss", "xml_feed"],
        "capabilities": ["configuration_validation", "runtime_preparation", "connector_acquisition", "abstract_execution", "result_collection", "output_validation", "provenance_tracking", "dry_run"],
    },
    {
        "name": "generic_html_runtime",
        "display_name": "Generic HTML Runtime",
        "runtime_class": "investguide.runtime.GenericHtmlRuntime",
        "supported_connector_types": ["html_scraper"],
        "capabilities": ["configuration_validation", "runtime_preparation", "connector_acquisition", "abstract_execution", "result_collection", "output_validation", "provenance_tracking", "dry_run"],
    },
    {
        "name": "generic_pdf_runtime",
        "display_name": "Generic PDF Runtime",
        "runtime_class": "investguide.runtime.GenericPdfRuntime",
        "supported_connector_types": ["pdf_extractor"],
        "capabilities": ["configuration_validation", "runtime_preparation", "connector_acquisition", "abstract_execution", "result_collection", "output_validation", "provenance_tracking", "dry_run"],
    },
    {
        "name": "generic_csv_runtime",
        "display_name": "Generic CSV Runtime",
        "runtime_class": "investguide.runtime.GenericCsvRuntime",
        "supported_connector_types": ["csv_importer"],
        "capabilities": ["configuration_validation", "runtime_preparation", "connector_acquisition", "abstract_execution", "result_collection", "output_validation", "provenance_tracking", "dry_run"],
    },
)


@dataclass(frozen=True)
class RuntimeSeedResult:
    """Summary of runtime registry seed execution."""

    inserted: int
    skipped: int
    compatible_connectors: int


def seed_runtimes(db: Session) -> RuntimeSeedResult:
    """Seed reusable runtime definitions and connector compatibility metadata."""
    ensure_development_data_allowed()
    actor = _owner_user(db)
    inserted = 0
    skipped = 0
    compatible_connectors = 0
    try:
        for item in RUNTIME_CATALOGUE:
            name = str(item["name"])
            runtime = db.scalar(select(RuntimeDefinition).where(RuntimeDefinition.name == name))
            if runtime is None:
                runtime = create_runtime(
                    db,
                    actor=actor,
                    payload=RuntimeCreate(
                        name=name,
                        display_name=str(item["display_name"]),
                        description=f"Development runtime contract for {item['display_name']}. It defines lifecycle and result contracts only.",
                        version="1.0.0",
                        runtime_class=str(item["runtime_class"]),
                        status="active",
                        supported_connector_types=list(item["supported_connector_types"]),
                        runtime_metadata={
                            "execution_implemented": False,
                            "network_allowed": False,
                            "result_payloads_persisted": False,
                            "lifecycle": ["created", "validated", "prepared", "executing", "completed", "failed", "cancelled"],
                        },
                        vendor="InvestGuide",
                        author="InvestGuide Platform",
                        classification="development_framework",
                        change_summary="Initial development runtime seed",
                        capabilities=[RuntimeCapabilityInput(capability=str(capability), description=f"Supports {capability} runtime contract.") for capability in item["capabilities"]],
                        reason="Development runtime registry seed",
                    ),
                )
                inserted += 1
            else:
                skipped += 1
            compatible_connectors += _bind_compatible_connectors(db, runtime)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Execution runtime registry seed failed; transaction rolled back")
        raise
    logger.info("Runtime registry seed completed: %s inserted, %s skipped, %s connector compatibilities", inserted, skipped, compatible_connectors)
    return RuntimeSeedResult(inserted=inserted, skipped=skipped, compatible_connectors=compatible_connectors)


def _bind_compatible_connectors(db: Session, runtime: RuntimeDefinition) -> int:
    bound = 0
    supported_types = set(runtime.supported_connector_types or [])
    for connector in db.scalars(select(Connector).where(Connector.connector_type.in_(supported_types))).all():
        existing = db.scalar(select(RuntimeCompatibility).where(RuntimeCompatibility.runtime_id == runtime.id, RuntimeCompatibility.connector_id == connector.id))
        if existing is None:
            db.add(
                RuntimeCompatibility(
                    runtime_id=runtime.id,
                    connector_id=connector.id,
                    connector_type=connector.connector_type,
                    compatibility_status="compatible",
                    notes="Seeded metadata-only runtime compatibility. No connector execution is implemented.",
                )
            )
            bound += 1
    return bound


def _owner_user(db: Session) -> User:
    owner = db.scalar(select(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(Role.slug == OWNER_ROLE, UserRole.is_active.is_(True)))
    if owner is None:
        raise RuntimeError("RBAC Owner must be bootstrapped before seeding runtime registry")
    return owner

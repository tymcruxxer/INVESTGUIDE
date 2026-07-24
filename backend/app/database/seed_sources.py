"""Development-only source registry seed catalogue."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.rbac import Role, UserRole
from app.models.source_registry import Source
from app.models.user import User
from app.schemas.source_registry import SourceConfigurationInput, SourceCreate, SourceCredentialInput
from app.services.rbac_service import OWNER_ROLE
from app.services.source_registry_service import create_source

logger = get_logger(__name__)

SOURCE_CATALOGUE: tuple[dict[str, object], ...] = (
    {"name": "zimbabwe_stock_exchange", "display_name": "Zimbabwe Stock Exchange", "category": "market", "tier": "tier_1", "organization": "Zimbabwe Stock Exchange", "connector_type": "website", "base_url": "https://www.zse.co.zw", "refresh_policy": "daily"},
    {"name": "victoria_falls_stock_exchange", "display_name": "Victoria Falls Stock Exchange", "category": "market", "tier": "tier_1", "organization": "VFEX", "connector_type": "website", "base_url": "https://www.vfex.exchange", "refresh_policy": "daily"},
    {"name": "reserve_bank_of_zimbabwe", "display_name": "Reserve Bank of Zimbabwe", "category": "government", "tier": "tier_1", "organization": "RBZ", "connector_type": "website", "base_url": "https://www.rbz.co.zw", "refresh_policy": "daily"},
    {"name": "zimstat", "display_name": "ZIMSTAT", "category": "government", "tier": "tier_1", "organization": "Zimbabwe National Statistics Agency", "connector_type": "pdf", "base_url": "https://www.zimstat.co.zw", "refresh_policy": "monthly"},
    {"name": "secz", "display_name": "SECZ", "category": "regulator", "tier": "tier_1", "organization": "Securities and Exchange Commission of Zimbabwe", "connector_type": "website", "base_url": "https://seczim.co.zw", "refresh_policy": "weekly"},
    {"name": "ministry_of_finance", "display_name": "Ministry of Finance", "category": "government", "tier": "tier_1", "organization": "Government of Zimbabwe", "connector_type": "website", "base_url": "https://www.zimtreasury.gov.zw", "refresh_policy": "weekly"},
    {"name": "ipec", "display_name": "IPEC", "category": "regulator", "tier": "tier_1", "organization": "Insurance and Pensions Commission", "connector_type": "website", "base_url": "https://www.ipec.co.zw", "refresh_policy": "weekly"},
    {"name": "central_depository_company", "display_name": "Central Depository Company", "category": "market", "tier": "tier_1", "organization": "CDC", "connector_type": "website", "base_url": "https://www.cdczimbabwe.com", "refresh_policy": "weekly"},
    {"name": "ih_securities", "display_name": "IH Securities", "category": "research", "tier": "tier_2", "organization": "IH Securities", "connector_type": "pdf", "base_url": "https://ihsecurities.com", "refresh_policy": "weekly"},
    {"name": "mmc_capital", "display_name": "MMC Capital", "category": "research", "tier": "tier_2", "organization": "MMC Capital", "connector_type": "pdf", "base_url": None, "refresh_policy": "weekly"},
    {"name": "morgan_and_co", "display_name": "Morgan & Co", "category": "research", "tier": "tier_2", "organization": "Morgan & Co", "connector_type": "pdf", "base_url": None, "refresh_policy": "weekly"},
    {"name": "old_mutual_research", "display_name": "Old Mutual Research", "category": "research", "tier": "tier_2", "organization": "Old Mutual", "connector_type": "pdf", "base_url": None, "refresh_policy": "monthly"},
    {"name": "abc_stockbrokers", "display_name": "ABC Stockbrokers", "category": "research", "tier": "tier_2", "organization": "ABC Stockbrokers", "connector_type": "pdf", "base_url": None, "refresh_policy": "weekly"},
    {"name": "herald_business", "display_name": "Herald Business", "category": "news", "tier": "tier_3", "organization": "The Herald", "connector_type": "rss", "base_url": "https://www.herald.co.zw", "refresh_policy": "daily"},
    {"name": "newsday_business", "display_name": "NewsDay Business", "category": "news", "tier": "tier_3", "organization": "NewsDay", "connector_type": "rss", "base_url": "https://www.newsday.co.zw", "refresh_policy": "daily"},
    {"name": "zimbabwe_independent", "display_name": "Zimbabwe Independent", "category": "news", "tier": "tier_3", "organization": "Zimbabwe Independent", "connector_type": "rss", "base_url": "https://www.theindependent.co.zw", "refresh_policy": "daily"},
    {"name": "business_weekly", "display_name": "Business Weekly", "category": "news", "tier": "tier_3", "organization": "Business Weekly", "connector_type": "rss", "base_url": "https://www.businessweekly.co.zw", "refresh_policy": "daily"},
    {"name": "chronicle_business", "display_name": "Chronicle Business", "category": "news", "tier": "tier_3", "organization": "Chronicle", "connector_type": "rss", "base_url": "https://www.chronicle.co.zw", "refresh_policy": "daily"},
    {"name": "imf", "display_name": "International Monetary Fund", "category": "international", "tier": "tier_2", "organization": "IMF", "connector_type": "rest_api", "base_url": "https://www.imf.org", "refresh_policy": "monthly"},
    {"name": "world_bank", "display_name": "World Bank", "category": "international", "tier": "tier_2", "organization": "World Bank", "connector_type": "rest_api", "base_url": "https://data.worldbank.org", "refresh_policy": "monthly"},
    {"name": "afdb", "display_name": "African Development Bank", "category": "international", "tier": "tier_2", "organization": "AfDB", "connector_type": "rest_api", "base_url": "https://www.afdb.org", "refresh_policy": "monthly"},
    {"name": "unctad", "display_name": "UNCTAD", "category": "international", "tier": "tier_2", "organization": "UNCTAD", "connector_type": "rest_api", "base_url": "https://unctad.org", "refresh_policy": "monthly"},
    {"name": "commodity_prices", "display_name": "Commodity Prices", "category": "commodity", "tier": "tier_3", "organization": "Future commodity provider", "connector_type": "future_connector", "base_url": None, "refresh_policy": "manual"},
    {"name": "weather_intelligence", "display_name": "Weather Intelligence", "category": "weather", "tier": "tier_3", "organization": "Future weather provider", "connector_type": "future_connector", "base_url": None, "refresh_policy": "manual"},
    {"name": "google_trends", "display_name": "Google Trends", "category": "alternative_intelligence", "tier": "tier_3", "organization": "Google", "connector_type": "future_connector", "base_url": None, "refresh_policy": "manual"},
    {"name": "social_sentiment", "display_name": "Social Sentiment", "category": "alternative_intelligence", "tier": "tier_3", "organization": "Future social signal provider", "connector_type": "future_connector", "base_url": None, "refresh_policy": "manual"},
)


@dataclass(frozen=True)
class SourceSeedResult:
    """Summary of source registry seed execution."""

    inserted: int
    skipped: int


def seed_sources(db: Session) -> SourceSeedResult:
    """Seed development source registry entries without duplicate inserts."""
    ensure_development_data_allowed()
    actor = _owner_user(db)
    inserted = 0
    skipped = 0
    try:
        for item in SOURCE_CATALOGUE:
            name = str(item["name"])
            existing = db.scalar(select(Source).where(Source.name == name))
            if existing is not None:
                skipped += 1
                continue
            credential_inputs = []
            if item["connector_type"] in {"rest_api", "rss"}:
                credential_inputs.append(
                    SourceCredentialInput(
                        key="development_placeholder",
                        label="Development placeholder credential",
                        secret_type="api_key",
                        secret_reference=f"dev/{name}/api-key",
                    )
                )
            create_source(
                db,
                actor=actor,
                payload=SourceCreate(
                    name=name,
                    display_name=str(item["display_name"]),
                    description=f"Development registry entry for {item['display_name']}.",
                    category=str(item["category"]),
                    tier=str(item["tier"]),
                    organization=str(item["organization"]) if item.get("organization") else None,
                    classification="development_catalogue",
                    supported_capabilities=_capabilities_for_item(item),
                    connector_type=str(item["connector_type"]),
                    authentication_type="api_key" if credential_inputs else "none",
                    status="disabled",
                    configuration=SourceConfigurationInput(
                        base_url=str(item["base_url"]) if item.get("base_url") else None,
                        refresh_policy=str(item["refresh_policy"]),
                        parser={"version": "development", "mode": "placeholder"},
                        connector_config={"live_enabled": False},
                        notes="Development catalogue entry. No live connector is active.",
                    ),
                    credentials=credential_inputs,
                    reason="Development source registry seed",
                ),
            )
            inserted += 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Source registry seed failed; transaction rolled back")
        raise
    logger.info("Source registry seed completed: %s inserted, %s skipped", inserted, skipped)
    return SourceSeedResult(inserted=inserted, skipped=skipped)




def _capabilities_for_item(item: dict[str, object]) -> list[str]:
    category = str(item.get("category") or "")
    name = str(item.get("name") or "")
    connector = str(item.get("connector_type") or "")
    if category == "market":
        return ["market_prices", "corporate_actions", "dividends", "trading_updates", "news"]
    if category in {"government", "regulator"}:
        capabilities = ["economic_indicators", "exchange_rates", "annual_reports", "news"]
        if name in {"reserve_bank_of_zimbabwe", "ministry_of_finance"}:
            capabilities.append("trading_updates")
        return sorted(set(capabilities))
    if category == "research":
        return ["research_reports", "annual_reports", "interim_reports", "trading_updates"]
    if category == "news":
        return ["news", "corporate_actions", "dividends", "trading_updates"]
    if category == "international":
        return ["economic_indicators", "exchange_rates", "commodity_prices", "research_reports"]
    if category == "commodity":
        return ["commodity_prices"]
    if category == "currency":
        return ["exchange_rates"]
    if category == "weather":
        return ["weather"]
    if category == "alternative_intelligence":
        return ["news", "research_reports"] if connector == "future_connector" else ["news"]
    return []
def _owner_user(db: Session) -> User:
    owner = db.scalar(select(User).join(UserRole, UserRole.user_id == User.id).join(Role, Role.id == UserRole.role_id).where(Role.slug == OWNER_ROLE, UserRole.is_active.is_(True)))
    if owner is None:
        raise RuntimeError("RBAC Owner must be bootstrapped before seeding source registry")
    return owner



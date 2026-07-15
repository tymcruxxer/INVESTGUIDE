"""Entity registry for verified data ingestion components."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.importers.records import (
    AssetImporter,
    BalanceSheetImporter,
    CashFlowStatementImporter,
    CompanyImporter,
    CompanyProfileImporter,
    CorporateActionImporter,
    DividendImporter,
    IncomeStatementImporter,
    MarketSnapshotImporter,
    NewsImporter,
)
from app.services.ingestion.normalizers.records import (
    AssetNormalizer,
    BalanceSheetNormalizer,
    CashFlowStatementNormalizer,
    CompanyNormalizer,
    CompanyProfileNormalizer,
    CorporateActionNormalizer,
    DividendNormalizer,
    IncomeStatementNormalizer,
    MarketSnapshotNormalizer,
    NewsNormalizer,
)
from app.services.ingestion.pipeline import Importer, Normalizer, Validator
from app.services.ingestion.types import EntityType
from app.services.ingestion.validators.records import (
    AssetValidator,
    BalanceSheetValidator,
    CashFlowStatementValidator,
    CompanyProfileValidator,
    CompanyValidator,
    CorporateActionValidator,
    DividendValidator,
    IncomeStatementValidator,
    MarketSnapshotValidator,
    NewsValidator,
)


@dataclass(frozen=True)
class EntityRegistration:
    """Registered components for one entity type."""

    normalizer: Normalizer
    validator: Validator
    importer: Importer


class IngestionRegistry:
    """Registry that maps entities to normalizer, validator, and importer components."""

    def __init__(self) -> None:
        self._registrations: dict[EntityType, EntityRegistration] = {}

    def register(self, entity: EntityType, registration: EntityRegistration) -> None:
        """Register entity components."""
        self._registrations[entity] = registration

    def unregister(self, entity: EntityType) -> None:
        """Remove entity components."""
        self._registrations.pop(entity, None)

    def get(self, entity: EntityType) -> EntityRegistration:
        """Return entity components or raise for unsupported entities."""
        try:
            return self._registrations[entity]
        except KeyError as exc:
            available = ", ".join(entity.value for entity in self.supported_entities())
            raise KeyError(f"No ingestion components registered for {entity.value}. Available: {available}") from exc

    def supported_entities(self) -> list[EntityType]:
        """Return supported entity types."""
        return sorted(self._registrations, key=lambda item: item.value)


def build_default_registry() -> IngestionRegistry:
    """Build the default runtime ingestion registry."""
    registry = IngestionRegistry()
    registry.register(EntityType.COMPANIES, EntityRegistration(CompanyNormalizer(), CompanyValidator(), CompanyImporter()))
    registry.register(EntityType.ASSETS, EntityRegistration(AssetNormalizer(), AssetValidator(), AssetImporter()))
    registry.register(EntityType.COMPANY_PROFILES, EntityRegistration(CompanyProfileNormalizer(), CompanyProfileValidator(), CompanyProfileImporter()))
    registry.register(EntityType.INCOME_STATEMENTS, EntityRegistration(IncomeStatementNormalizer(), IncomeStatementValidator(), IncomeStatementImporter()))
    registry.register(EntityType.BALANCE_SHEETS, EntityRegistration(BalanceSheetNormalizer(), BalanceSheetValidator(), BalanceSheetImporter()))
    registry.register(EntityType.CASH_FLOW_STATEMENTS, EntityRegistration(CashFlowStatementNormalizer(), CashFlowStatementValidator(), CashFlowStatementImporter()))
    registry.register(EntityType.DIVIDENDS, EntityRegistration(DividendNormalizer(), DividendValidator(), DividendImporter()))
    registry.register(EntityType.CORPORATE_ACTIONS, EntityRegistration(CorporateActionNormalizer(), CorporateActionValidator(), CorporateActionImporter()))
    registry.register(EntityType.NEWS, EntityRegistration(NewsNormalizer(), NewsValidator(), NewsImporter()))
    registry.register(EntityType.MARKET_SNAPSHOTS, EntityRegistration(MarketSnapshotNormalizer(), MarketSnapshotValidator(), MarketSnapshotImporter()))
    return registry

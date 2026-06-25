"""Source registry and metadata for InvestGuide scrapers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

from scrapers.pipeline.source_trust import SourceTier


class SourceCategory(StrEnum):
    """Supported source categories."""

    OFFICIAL = "official"
    INSTITUTIONAL = "institutional"
    FINANCIAL_JOURNALISM = "financial_journalism"


@dataclass(frozen=True)
class SourceDefinition:
    """Metadata required to register a scraper source."""

    id: str
    display_name: str
    category: SourceCategory
    priority: int
    enabled: bool
    trust_tier: SourceTier
    homepage: str
    robots_url: str
    scraper_class: type[Any] | str | None = None


class SourceRegistry:
    """Registry for scraper source metadata."""

    def __init__(self, sources: list[SourceDefinition] | None = None) -> None:
        self._sources: dict[str, SourceDefinition] = {}
        for source in sources or []:
            self.register(source)

    def register(self, source: SourceDefinition) -> None:
        """Register a source and validate source id/display name uniqueness."""
        normalized_id = self._normalize(source.id)
        if normalized_id in self._sources:
            raise ValueError(f"Duplicate source id: {source.id}")
        if any(self._normalize(existing.display_name) == self._normalize(source.display_name) for existing in self._sources.values()):
            raise ValueError(f"Duplicate source display name: {source.display_name}")
        self._sources[normalized_id] = source

    def all(self, include_disabled: bool = True) -> list[SourceDefinition]:
        """Return registered sources ordered by priority."""
        sources = list(self._sources.values())
        if not include_disabled:
            sources = [source for source in sources if source.enabled]
        return sorted(sources, key=lambda source: source.priority)

    def get(self, source_id: str) -> SourceDefinition | None:
        """Look up a source by id."""
        return self._sources.get(self._normalize(source_id))

    def get_by_display_name(self, display_name: str) -> SourceDefinition | None:
        """Look up a source by display name."""
        normalized = self._normalize(display_name)
        return next((source for source in self._sources.values() if self._normalize(source.display_name) == normalized), None)

    def by_category(self, category: SourceCategory | str, include_disabled: bool = True) -> list[SourceDefinition]:
        """Return sources matching a category."""
        category_value = SourceCategory(category)
        return [source for source in self.all(include_disabled=include_disabled) if source.category == category_value]

    def by_priority(self, max_priority: int, include_disabled: bool = True) -> list[SourceDefinition]:
        """Return sources up to a priority value."""
        return [source for source in self.all(include_disabled=include_disabled) if source.priority <= max_priority]

    def enable(self, source_id: str) -> SourceDefinition:
        """Enable a source."""
        return self._set_enabled(source_id, True)

    def disable(self, source_id: str) -> SourceDefinition:
        """Disable a source."""
        return self._set_enabled(source_id, False)

    def validate_unique(self) -> None:
        """Validate registered source ids and display names are unique."""
        ids = [self._normalize(source.id) for source in self._sources.values()]
        names = [self._normalize(source.display_name) for source in self._sources.values()]
        if len(ids) != len(set(ids)) or len(names) != len(set(names)):
            raise ValueError("Source registry contains duplicate ids or display names")

    def _set_enabled(self, source_id: str, enabled: bool) -> SourceDefinition:
        normalized_id = self._normalize(source_id)
        source = self._sources.get(normalized_id)
        if source is None:
            raise KeyError(source_id)
        updated = replace(source, enabled=enabled)
        self._sources[normalized_id] = updated
        return updated

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().lower().replace("_", "-").split())


def _source(
    source_id: str,
    display_name: str,
    category: SourceCategory,
    priority: int,
    trust_tier: SourceTier,
    homepage: str,
    scraper_class: type[Any] | str | None = None,
) -> SourceDefinition:
    homepage = homepage.rstrip("/")
    return SourceDefinition(
        id=source_id,
        display_name=display_name,
        category=category,
        priority=priority,
        enabled=True,
        trust_tier=trust_tier,
        homepage=homepage,
        robots_url=f"{homepage}/robots.txt",
        scraper_class=scraper_class,
    )


DEFAULT_SOURCES: list[SourceDefinition] = [
    _source("zse", "ZSE", SourceCategory.OFFICIAL, 10, SourceTier.TIER_1_OFFICIAL, "https://www.zse.co.zw", "scrapers.zse.announcements_scraper.ZSEAnnouncementsScraper"),
    _source("vfex", "VFEX", SourceCategory.OFFICIAL, 20, SourceTier.TIER_1_OFFICIAL, "https://www.vfex.exchange", "scrapers.vfex.market_scraper.VFEXMarketScraper"),
    _source("rbz", "RBZ", SourceCategory.OFFICIAL, 30, SourceTier.TIER_1_OFFICIAL, "https://www.rbz.co.zw", "scrapers.rbz.macro_scraper.RBZMacroScraper"),
    _source("zimstat", "ZIMSTAT", SourceCategory.OFFICIAL, 40, SourceTier.TIER_1_OFFICIAL, "https://www.zimstat.co.zw"),
    _source("ih-securities", "IH Securities", SourceCategory.INSTITUTIONAL, 110, SourceTier.TIER_2_INSTITUTIONAL, "https://ihsecurities.com", "scrapers.research.ih_securities.IHSecuritiesScraper"),
    _source("mmc-capital", "MMC Capital", SourceCategory.INSTITUTIONAL, 120, SourceTier.TIER_2_INSTITUTIONAL, "https://www.mmccapital.co.zw", "scrapers.research.mmc_capital.MMCCapitalScraper"),
    _source("old-mutual-investment-group", "Old Mutual Investment Group", SourceCategory.INSTITUTIONAL, 130, SourceTier.TIER_2_INSTITUTIONAL, "https://www.oldmutual.co.zw"),
    _source("abc-stockbrokers", "ABC Stockbrokers", SourceCategory.INSTITUTIONAL, 140, SourceTier.TIER_2_INSTITUTIONAL, "https://abcstockbrokers.co.zw"),
    _source("financial-gazette", "Financial Gazette", SourceCategory.FINANCIAL_JOURNALISM, 210, SourceTier.TIER_3_JOURNALISM, "https://fingaz.co.zw", "scrapers.news.financial_gazette.FinancialGazetteScraper"),
    _source("newsday-business", "NewsDay Business", SourceCategory.FINANCIAL_JOURNALISM, 220, SourceTier.TIER_3_JOURNALISM, "https://www.newsday.co.zw", "scrapers.news.newsday_business.NewsdayBusinessScraper"),
    _source("herald-business", "Herald Business", SourceCategory.FINANCIAL_JOURNALISM, 230, SourceTier.TIER_3_JOURNALISM, "https://www.herald.co.zw", "scrapers.news.herald_business.HeraldBusinessScraper"),
]


def default_source_registry() -> SourceRegistry:
    """Return a registry preloaded with InvestGuide source metadata."""
    return SourceRegistry(DEFAULT_SOURCES)
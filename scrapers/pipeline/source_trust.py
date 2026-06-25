"""Source trust metadata for scraper ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SourceTier(StrEnum):
    """Source trust tiers used by InvestGuide ingestion."""

    TIER_1_OFFICIAL = "Tier 1 - Official Sources"
    TIER_2_INSTITUTIONAL = "Tier 2 - Institutional Research"
    TIER_3_JOURNALISM = "Tier 3 - Financial Journalism"
    TIER_4_GENERAL = "Tier 4 - General Web Sources"


@dataclass(frozen=True)
class SourceTrustMetadata:
    """Trust metadata attached to normalized ingestion payloads."""

    tier: SourceTier
    score: float


TIER_SCORES: dict[SourceTier, float] = {
    SourceTier.TIER_1_OFFICIAL: 1.0,
    SourceTier.TIER_2_INSTITUTIONAL: 0.85,
    SourceTier.TIER_3_JOURNALISM: 0.7,
    SourceTier.TIER_4_GENERAL: 0.4,
}

_SOURCE_TIER_MAP: dict[str, SourceTier] = {
    "zse": SourceTier.TIER_1_OFFICIAL,
    "zimbabwe stock exchange": SourceTier.TIER_1_OFFICIAL,
    "zimbabwe stock exchange announcements": SourceTier.TIER_1_OFFICIAL,
    "vfex": SourceTier.TIER_1_OFFICIAL,
    "victoria falls stock exchange": SourceTier.TIER_1_OFFICIAL,
    "rbz": SourceTier.TIER_1_OFFICIAL,
    "reserve bank of zimbabwe": SourceTier.TIER_1_OFFICIAL,
    "zimstat": SourceTier.TIER_1_OFFICIAL,
    "ih securities": SourceTier.TIER_2_INSTITUTIONAL,
    "mmc capital": SourceTier.TIER_2_INSTITUTIONAL,
    "old mutual investment group": SourceTier.TIER_2_INSTITUTIONAL,
    "abc stockbrokers": SourceTier.TIER_2_INSTITUTIONAL,
    "financial gazette": SourceTier.TIER_3_JOURNALISM,
    "newsday business": SourceTier.TIER_3_JOURNALISM,
    "herald business": SourceTier.TIER_3_JOURNALISM,
}


def _normalize_source_name(source_name: str) -> str:
    return " ".join(source_name.strip().lower().split())


def get_source_tier(source_name: str) -> SourceTier:
    """Return the configured trust tier for a source name."""
    return _SOURCE_TIER_MAP.get(_normalize_source_name(source_name), SourceTier.TIER_4_GENERAL)


def get_source_trust_score(source_name: str) -> float:
    """Return the numeric trust score for a source name."""
    return TIER_SCORES[get_source_tier(source_name)]


def get_source_trust_metadata(source_name: str) -> SourceTrustMetadata:
    """Return full trust metadata for a source name."""
    tier = get_source_tier(source_name)
    return SourceTrustMetadata(tier=tier, score=TIER_SCORES[tier])
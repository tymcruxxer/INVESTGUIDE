"""Asset linking contract for normalized article text."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable


@dataclass(frozen=True)
class AssetMetadata:
    """Minimal asset metadata required by the scraper linker."""

    ticker: str
    company_name: str
    aliases: tuple[str, ...] = field(default_factory=tuple)


DEFAULT_ASSET_METADATA: tuple[AssetMetadata, ...] = (
    AssetMetadata("DELTA", "Delta Corporation", ("Delta Corporation Limited",)),
    AssetMetadata("ECO", "Econet Wireless", ("Econet Wireless Zimbabwe",)),
    AssetMetadata("CBZ", "CBZ Holdings", ("CBZ Holdings Limited",)),
    AssetMetadata("INN", "Innscor Africa", ("Innscor Africa Limited",)),
    AssetMetadata("TIGERE", "Tigere REIT", ("Tigere Real Estate Investment Trust",)),
    AssetMetadata("FMREIT", "First Mutual REIT", ("First Mutual Real Estate Investment Trust",)),
    AssetMetadata("SEED", "Seed Co International", ("Seed Co",)),
    AssetMetadata("CMCL", "Caledonia Mining", ("Caledonia Mining Corporation",)),
    AssetMetadata("PHL", "Padenga Holdings", ("Padenga Holdings Limited",)),
)


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def link_assets(text: str, assets: Iterable[AssetMetadata] = DEFAULT_ASSET_METADATA) -> list[str]:
    """Return likely related tickers using explicit company-name keyword matches.

    Exchange-level terms such as ZSE or VFEX are deliberately not mapped to all
    assets. Future sprints can replace this with a richer entity linker.
    """
    normalized_text = text.lower()
    matched: list[str] = []
    for asset in assets:
        phrases = (asset.company_name, *asset.aliases)
        if any(_contains_phrase(normalized_text, phrase) for phrase in phrases):
            matched.append(asset.ticker.upper())
    return matched
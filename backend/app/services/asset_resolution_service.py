"""Asset resolution helpers for news ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus


@dataclass(frozen=True)
class AssetResolutionResult:
    """Result of resolving incoming ticker symbols to active assets."""

    found_assets: list[Asset] = field(default_factory=list)
    missing_tickers: list[str] = field(default_factory=list)
    inactive_tickers: list[str] = field(default_factory=list)

    @property
    def linked_tickers(self) -> list[str]:
        """Return tickers that can be safely attached to the article."""
        return [asset.ticker for asset in self.found_assets]


def _normalize_tickers(tickers: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for ticker in tickers:
        value = str(ticker).strip().upper()
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def resolve_assets(db: Session, tickers: list[str]) -> AssetResolutionResult:
    """Resolve asset tickers to active Asset records."""
    normalized = _normalize_tickers(tickers)
    if not normalized:
        return AssetResolutionResult()

    assets = db.scalars(select(Asset).where(func.upper(Asset.ticker).in_(normalized))).all()
    assets_by_ticker = {asset.ticker.upper(): asset for asset in assets}

    found_assets: list[Asset] = []
    inactive_tickers: list[str] = []
    missing_tickers: list[str] = []

    for ticker in normalized:
        asset = assets_by_ticker.get(ticker)
        if asset is None:
            missing_tickers.append(ticker)
            continue
        if asset.status != AssetStatus.ACTIVE:
            inactive_tickers.append(ticker)
            continue
        found_assets.append(asset)

    return AssetResolutionResult(
        found_assets=found_assets,
        missing_tickers=missing_tickers,
        inactive_tickers=inactive_tickers,
    )
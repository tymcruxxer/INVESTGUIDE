"""Macro indicator retrieval with verified-over-development precedence."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.development_data_guard import get_development_data_policy
from app.models.macro import MacroIndicator, MacroIndicatorType

_INDICATOR_ROUTE_MAP: dict[str, MacroIndicatorType] = {
    "inflation": MacroIndicatorType.INFLATION,
    "interest-rates": MacroIndicatorType.INTEREST_RATE,
    "interest_rate": MacroIndicatorType.INTEREST_RATE,
    "exchange-rates": MacroIndicatorType.EXCHANGE_RATE,
    "exchange_rate": MacroIndicatorType.EXCHANGE_RATE,
    "gdp": MacroIndicatorType.GDP,
    "commodities": MacroIndicatorType.COMMODITY_PRICE,
    "commodity_price": MacroIndicatorType.COMMODITY_PRICE,
}


def resolve_indicator_type(value: str) -> MacroIndicatorType | None:
    """Resolve a route slug or persisted value to an indicator type."""
    key = value.strip().lower().replace(" ", "-")
    if key in _INDICATOR_ROUTE_MAP:
        return _INDICATOR_ROUTE_MAP[key]
    normalized = key.replace("-", "_")
    try:
        return MacroIndicatorType(normalized)
    except ValueError:
        return None


def list_macro_indicators(db: Session) -> list[MacroIndicator]:
    """Return latest acceptable row per macro type/name/country/currency."""
    rows = list(
        db.scalars(
            select(MacroIndicator).order_by(
                MacroIndicator.indicator_type.asc(),
                MacroIndicator.name.asc(),
                MacroIndicator.reporting_period.desc(),
                MacroIndicator.id.desc(),
            )
        ).all()
    )
    return _select_acceptable_latest(rows)


def get_indicators_by_type(db: Session, indicator_type: MacroIndicatorType) -> list[MacroIndicator]:
    """Return latest acceptable rows for one macro indicator family."""
    rows = list(
        db.scalars(
            select(MacroIndicator)
            .where(MacroIndicator.indicator_type == indicator_type)
            .order_by(MacroIndicator.reporting_period.desc(), MacroIndicator.id.desc())
        ).all()
    )
    return _select_acceptable_latest(rows)


def get_latest_indicator(db: Session, indicator_type: MacroIndicatorType) -> MacroIndicator | None:
    """Return the latest acceptable indicator row for one type."""
    rows = get_indicators_by_type(db, indicator_type)
    return max(rows, key=lambda item: (item.reporting_period, item.id)) if rows else None


def _select_acceptable_latest(rows: Iterable[MacroIndicator]) -> list[MacroIndicator]:
    policy = get_development_data_policy()
    grouped: dict[tuple[str, str, str, str | None, str | None], list[MacroIndicator]] = defaultdict(list)
    for row in rows:
        grouped[(row.indicator_type.value, row.name.lower(), row.country, row.currency, row.commodity)].append(row)

    selected: list[MacroIndicator] = []
    for group_rows in grouped.values():
        verified = [row for row in group_rows if not row.is_development_data]
        if verified:
            selected.append(max(verified, key=lambda item: (item.reporting_period, item.id)))
            continue
        if policy.permits_fixtures:
            selected.append(max(group_rows, key=lambda item: (item.reporting_period, item.id)))
    return sorted(selected, key=lambda item: (item.indicator_type.value, item.name))


def serialize_indicator(row: MacroIndicator) -> dict[str, object]:
    """Serialize one macro indicator row into an API-safe dictionary."""
    return {
        "id": row.id,
        "indicator_type": row.indicator_type.value,
        "name": row.name,
        "value": float(row.value),
        "unit": row.unit,
        "reporting_period": row.reporting_period.isoformat(),
        "country": row.country,
        "currency": row.currency,
        "commodity": row.commodity,
        "notes": row.notes,
        "source_name": row.source_name,
        "source_type": row.source_type,
        "source_url": row.source_url,
        "imported_at": row.imported_at.isoformat() if row.imported_at else None,
        "verified_at": row.verified_at.isoformat() if row.verified_at else None,
        "verification_status": row.verification_status,
        "dataset_version": row.dataset_version,
        "is_development_data": row.is_development_data,
        "data_origin": "Development Preview" if row.is_development_data else "Persisted Backend",
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }

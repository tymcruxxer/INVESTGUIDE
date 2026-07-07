"""Shared helpers for deterministic investment intelligence engines."""

from __future__ import annotations

from typing import Any


def asset_value(asset: Any, field: str, default: str | None = None) -> Any:
    """Read a field from ORM objects, namespaces, or dictionaries."""
    if isinstance(asset, dict):
        return asset.get(field, default)
    return getattr(asset, field, default)


def normalized_value(asset: Any, field: str, default: str = "") -> str:
    """Return a string value suitable for deterministic matching."""
    value = asset_value(asset, field, default)
    if value is None:
        return default
    raw = getattr(value, "value", value)
    return str(raw).strip()


def unique_ordered(items: list[str]) -> list[str]:
    """Return unique strings while preserving first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(item.split())
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result
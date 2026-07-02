"""Analytics context object for all future intelligence calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AnalyticsContext:
    """Container for all inputs an analytics module may need.

    Inputs are optional because Sprint 026 establishes the architecture before
    historical prices, macro series, statements, portfolios, and other modules
    are fully implemented.
    """

    asset: Any | None = None
    historical_prices: list[Any] | None = None
    news: list[Any] | None = None
    macro_data: Any | None = None
    financial_statements: Any | None = None
    user_profile: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_required_data(self, required_fields: list[str] | tuple[str, ...]) -> bool:
        """Return true when all required context fields contain usable data."""
        return not self.missing_inputs(required_fields)

    def missing_inputs(self, required_fields: list[str] | tuple[str, ...]) -> list[str]:
        """Return required context field names that are absent or empty."""
        missing: list[str] = []
        for field_name in required_fields:
            value = getattr(self, field_name, None)
            if value in (None, [], {}, ""):
                missing.append(field_name)
        return missing

    def available_inputs(self) -> list[str]:
        """Return context fields currently populated with usable values."""
        fields = (
            "asset",
            "historical_prices",
            "news",
            "macro_data",
            "financial_statements",
            "user_profile",
        )
        return [field_name for field_name in fields if getattr(self, field_name) not in (None, [], {}, "")]

    def asset_identifier(self) -> str | None:
        """Return a stable asset label when the asset is dict-like or model-like."""
        if self.asset is None:
            return None
        if isinstance(self.asset, dict):
            value = self.asset.get("ticker") or self.asset.get("id") or self.asset.get("company_name")
            return str(value) if value is not None else None
        for attr in ("ticker", "id", "company_name"):
            value = getattr(self.asset, attr, None)
            if value is not None:
                return str(value)
        return None
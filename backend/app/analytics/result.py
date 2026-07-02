"""Standard analytics result object."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.analytics.version import ENGINE_VERSION


@dataclass(slots=True)
class AnalyticsResult:
    """Standard analytics output envelope used by every analytics module."""

    metric_name: str
    value: Any = None
    confidence: float = 0.0
    methodology: str = "Methodology documented; calculation not implemented yet"
    inputs_used: tuple[str, ...] | list[str] = field(default_factory=tuple)
    warnings: tuple[str, ...] | list[str] = field(default_factory=tuple)
    timestamp: datetime | None = None
    version: str = ENGINE_VERSION

    def __post_init__(self) -> None:
        """Populate timestamp and validate confidence bounds."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the result for APIs, AI context, and future frontend use."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "confidence": self.confidence,
            "methodology": self.methodology,
            "inputs_used": list(self.inputs_used),
            "warnings": list(self.warnings),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "version": self.version,
        }
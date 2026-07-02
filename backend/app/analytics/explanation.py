"""Human-readable analytics explanation templates."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnalyticsExplanation:
    """Template-driven explanation for analytics results.

    This layer is intentionally not AI. It provides deterministic language that
    future AI and frontend modules can consume safely.
    """

    metric_name: str
    summary: str
    details: tuple[str, ...] | list[str] = field(default_factory=tuple)
    confidence_label: str = "Not available"
    missing_inputs: tuple[str, ...] | list[str] = field(default_factory=tuple)

    def to_text(self) -> str:
        """Render a deterministic plain-language explanation."""
        lines = [f"{self.metric_name}: {self.summary}"]
        if self.details:
            lines.append("Why this matters:")
            lines.extend(f"- {detail}" for detail in self.details)
        lines.append(f"Confidence: {self.confidence_label}")
        if self.missing_inputs:
            lines.append("Missing inputs:")
            lines.extend(f"- {item}" for item in self.missing_inputs)
        return "\n".join(lines)

    @classmethod
    def from_result(cls, result: object) -> "AnalyticsExplanation":
        """Create a generic explanation from an AnalyticsResult-like object."""
        metric_name = getattr(result, "metric_name")
        warnings = tuple(getattr(result, "warnings", ()) or ())
        confidence = float(getattr(result, "confidence", 0.0))
        if confidence >= 0.75:
            label = "High"
        elif confidence >= 0.4:
            label = "Medium"
        elif confidence > 0:
            label = "Low"
        else:
            label = "Not available"
        return cls(
            metric_name=metric_name,
            summary="Analytics architecture is available; calculation is not implemented yet.",
            details=warnings,
            confidence_label=label,
        )
"""Scoring helpers for deterministic research engines."""

from __future__ import annotations


def clamp_score(value: int, minimum: int = 0, maximum: int = 100) -> int:
    """Clamp a score into the supported 0-100 range."""
    return max(minimum, min(maximum, value))


def score_from_factors(base: int, positive_factors: int, caution_factors: int) -> int:
    """Build a simple deterministic score from factor counts."""
    return clamp_score(base + positive_factors * 8 - caution_factors * 7)


def confidence_label(score: int) -> str:
    """Map a numeric score to a plain-language confidence label."""
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Moderate"
    if score >= 35:
        return "Limited"
    return "Experimental"

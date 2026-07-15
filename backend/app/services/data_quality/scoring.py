"""Shared data-quality scoring contracts."""

from __future__ import annotations

from dataclasses import dataclass, field


def clamp_score(value: float) -> int:
    """Clamp a numeric score to the 0-100 scale."""
    return max(0, min(100, int(round(value))))


def score_label(score: int) -> str:
    """Return a stable quality label for a score."""
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Strong"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Moderate"
    if score >= 30:
        return "Weak"
    return "Critical"


@dataclass(frozen=True)
class QualityScore:
    """Deterministic quality score with explanation."""

    score: int
    label: str
    reasons: list[str] = field(default_factory=list)

    @classmethod
    def from_value(cls, value: float, reasons: list[str]) -> "QualityScore":
        score = clamp_score(value)
        return cls(score=score, label=score_label(score), reasons=reasons)

    def to_dict(self) -> dict[str, object]:
        return {"score": self.score, "label": self.label, "reasons": self.reasons}


def average_scores(scores: list[QualityScore], reasons: list[str] | None = None) -> QualityScore:
    """Average component scores into an overall score."""
    if not scores:
        return QualityScore(score=0, label="Critical", reasons=["No score components were available."])
    return QualityScore.from_value(sum(score.score for score in scores) / len(scores), reasons or ["Overall score averages completeness, validity, provenance, freshness, and consistency."])

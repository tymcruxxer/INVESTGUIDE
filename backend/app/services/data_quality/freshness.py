"""Freshness targets and scoring for ingestion operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.services.data_quality.scoring import QualityScore

FRESHNESS_TARGET_DAYS: dict[str, int] = {
    "market_snapshots": 1,
    "news": 1,
    "company_profiles": 90,
    "companies": 90,
    "assets": 90,
    "income_statements": 365,
    "balance_sheets": 365,
    "cash_flow_statements": 365,
    "dividends": 365,
    "corporate_actions": 365,
}


@dataclass(frozen=True)
class FreshnessResult:
    latest_update: str | None
    target_days: int
    age_days: int | None
    status: str
    score: QualityScore
    explanation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "latest_update": self.latest_update,
            "target_days": self.target_days,
            "age_days": self.age_days,
            "status": self.status,
            "score": self.score.to_dict(),
            "explanation": self.explanation,
        }


def _as_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    return None


def score_freshness(entity_type: str, latest_update: object, development_only: bool = False) -> FreshnessResult:
    """Score freshness against the central target table."""
    target = FRESHNESS_TARGET_DAYS.get(entity_type, 90)
    latest = _as_datetime(latest_update)
    if latest is None:
        return FreshnessResult(
            latest_update=None,
            target_days=target,
            age_days=None,
            status="Unknown",
            score=QualityScore(score=0, label="Critical", reasons=["No update timestamp is available."]),
            explanation="Freshness cannot be determined because no update timestamp is available.",
        )
    now = datetime.now(timezone.utc)
    age_days = max(0, (now - latest).days)
    if development_only:
        status = "Unknown"
        value = 35
        reason = "Only development fixture data is available; it is not treated as fresh production data."
    elif age_days <= target:
        status = "Fresh"
        value = 100
        reason = f"Latest update is {age_days} day(s) old, within the {target}-day target."
    elif age_days <= target * 2:
        status = "Aging"
        value = 65
        reason = f"Latest update is {age_days} day(s) old, beyond the {target}-day target but not critically stale."
    else:
        status = "Stale"
        value = 30
        reason = f"Latest update is {age_days} day(s) old, more than twice the {target}-day target."
    return FreshnessResult(
        latest_update=latest.isoformat(),
        target_days=target,
        age_days=age_days,
        status=status,
        score=QualityScore.from_value(value, [reason]),
        explanation=reason,
    )

"""Provenance scoring for operational data quality."""

from __future__ import annotations

from app.services.data_quality.scoring import QualityScore


def provenance_label(source_name: object, source_type: object, is_development_data: bool, verified_at: object | None) -> str:
    """Return stable provenance label aligned with data-origin precedence."""
    if is_development_data:
        return "Development Preview"
    if verified_at is not None:
        return "Verified Source"
    if source_name and source_type:
        return "Validated Import"
    if source_name:
        return "Manual Curated"
    return "Unknown"


def score_provenance(records: list[object]) -> QualityScore:
    """Score source metadata quality over records."""
    if not records:
        return QualityScore(score=0, label="Critical", reasons=["No records are available for provenance scoring."])
    possible = len(records) * 5
    points = 0
    development = 0
    missing: set[str] = set()
    for record in records:
        source_name = getattr(record, "source_name", None) or getattr(record, "source", None)
        source_type = getattr(record, "source_type", None)
        source_url = getattr(record, "source_url", None) or getattr(record, "url", None)
        imported_at = getattr(record, "imported_at", None) or getattr(record, "created_at", None)
        verified_at = getattr(record, "verified_at", None) or getattr(record, "last_verified", None)
        is_development = bool(getattr(record, "is_development_data", False))
        if source_name:
            points += 1
        else:
            missing.add("source_name")
        if source_type or source_name:
            points += 1
        else:
            missing.add("source_type")
        if source_url:
            points += 1
        else:
            missing.add("source_url")
        if imported_at:
            points += 1
        else:
            missing.add("imported_at")
        if verified_at and not is_development:
            points += 1
        elif is_development:
            development += 1
        else:
            missing.add("verified_at")
    score = (points / possible) * 100 if possible else 0
    if development:
        score = min(score, 65)
    reasons = [f"{points} of {possible} provenance checks are present."]
    if development:
        reasons.append(f"{development} record(s) are development fixture data and cannot receive full production provenance credit.")
    if missing:
        reasons.append("Missing provenance fields: " + ", ".join(sorted(missing)) + ".")
    return QualityScore.from_value(score, reasons)

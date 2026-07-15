"""Completeness scoring rules for operational data quality."""

from __future__ import annotations

from app.services.data_quality.scoring import QualityScore

ENTITY_REQUIRED_FIELDS: dict[str, list[str]] = {
    "companies": ["name", "ticker", "exchange", "sector", "industry", "country"],
    "company_profiles": ["business_summary", "primary_business", "products_services", "industry", "source_name", "research_status"],
    "assets": ["ticker", "company_id", "exchange", "currency", "asset_type", "status"],
    "income_statements": ["company_id", "fiscal_year", "period", "currency", "source_name"],
    "balance_sheets": ["company_id", "fiscal_year", "period", "currency", "source_name"],
    "cash_flow_statements": ["company_id", "fiscal_year", "period", "currency", "source_name"],
    "dividends": ["company_id", "dividend_type", "dividend_per_share", "currency", "source_name"],
    "news": ["title", "source", "published_at"],
    "market_snapshots": ["asset_id", "snapshot_date", "price", "currency", "source_name"],
}


def is_present(value: object) -> bool:
    """Return whether a field has usable content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def score_records(entity_type: str, records: list[object]) -> QualityScore:
    """Score required-field completeness over a sample of records."""
    fields = ENTITY_REQUIRED_FIELDS.get(entity_type, [])
    if not records:
        return QualityScore(score=0, label="Critical", reasons=[f"No {entity_type} records are available."])
    if not fields:
        return QualityScore(score=50, label="Moderate", reasons=[f"No specific completeness rules are configured for {entity_type}."])
    possible = len(records) * len(fields)
    present = 0
    missing_fields: set[str] = set()
    for record in records:
        for field in fields:
            value = getattr(record, field, None)
            if is_present(value):
                present += 1
            else:
                missing_fields.add(field)
    score = (present / possible) * 100 if possible else 0
    reasons = [f"{present} of {possible} required field checks are present."]
    if missing_fields:
        reasons.append("Missing or incomplete fields: " + ", ".join(sorted(missing_fields)) + ".")
    else:
        reasons.append("All configured required fields are present in the sampled records.")
    return QualityScore.from_value(score, reasons)

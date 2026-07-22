"""Manual development macro indicator seed command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.macro import MacroIndicator, MacroIndicatorType
from app.services.ingestion.normalizers.helpers import clean_string, normalize_currency, parse_date, parse_datetime, parse_decimal
from app.services.ingestion.normalizers.records import normalize_macro_indicator_type
from app.services.ingestion.types import SourceType, VerificationStatus, build_external_key

logger = get_logger(__name__)
FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ingestion" / "macro_indicators.json"


@dataclass(frozen=True)
class MacroSeedResult:
    """Summary of macro development seed execution."""

    inserted: int
    updated: int
    skipped: int


def _load_fixture_records() -> list[dict[str, object]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))


def seed_macro_indicators(db: Session, records: list[dict[str, object]] | None = None) -> MacroSeedResult:
    """Seed development macro indicators without overwriting verified records."""
    ensure_development_data_allowed()
    inserted = updated = skipped = 0
    for record in records or _load_fixture_records():
        indicator_type = MacroIndicatorType(normalize_macro_indicator_type(record.get("indicator_type")))
        name = clean_string(record.get("name")) or indicator_type.value.replace("_", " ").title()
        reporting_period = parse_date(record.get("reporting_period"))
        if reporting_period is None:
            skipped += 1
            logger.warning("Skipping macro seed without reporting period: %s", name)
            continue
        currency = normalize_currency(record.get("currency"))
        source_type = clean_string(record.get("source_type")) or SourceType.DEVELOPMENT_FIXTURE.value
        existing = db.scalar(
            select(MacroIndicator).where(
                MacroIndicator.indicator_type == indicator_type,
                func.lower(MacroIndicator.name) == name.lower(),
                MacroIndicator.reporting_period == reporting_period,
                MacroIndicator.country == (clean_string(record.get("country")) or "Zimbabwe"),
                MacroIndicator.currency == currency,
                MacroIndicator.source_type == source_type,
            )
        )
        if existing and existing.is_development_data is False:
            skipped += 1
            continue
        value = parse_decimal(record.get("value"))
        if value is None:
            skipped += 1
            logger.warning("Skipping macro seed without value: %s", name)
            continue
        values = {
            "indicator_type": indicator_type,
            "name": name,
            "value": float(value),
            "unit": clean_string(record.get("unit")) or "value",
            "reporting_period": reporting_period,
            "country": clean_string(record.get("country")) or "Zimbabwe",
            "currency": currency,
            "commodity": clean_string(record.get("commodity")),
            "notes": clean_string(record.get("notes")),
            "source_name": clean_string(record.get("source_name")) or "Development Macro Fixture",
            "source_type": source_type,
            "source_url": clean_string(record.get("source_url")),
            "imported_at": parse_datetime(record.get("imported_at")),
            "verified_at": parse_datetime(record.get("verified_at")),
            "verification_status": VerificationStatus.DEVELOPMENT.value,
            "dataset_version": clean_string(record.get("dataset_version")) or "development-preview-v1",
            "external_key": build_external_key(source_type, indicator_type.value, name, reporting_period, record.get("country"), currency, record.get("commodity")),
            "is_development_data": True,
        }
        if existing is None:
            db.add(MacroIndicator(**values))
            inserted += 1
        else:
            changed = False
            for field, value_item in values.items():
                if getattr(existing, field) != value_item:
                    setattr(existing, field, value_item)
                    changed = True
            updated += 1 if changed else 0
            skipped += 0 if changed else 1
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Macro seed failed; transaction rolled back")
        raise
    logger.info("Macro seed completed: %s inserted, %s updated, %s skipped", inserted, updated, skipped)
    return MacroSeedResult(inserted=inserted, updated=updated, skipped=skipped)


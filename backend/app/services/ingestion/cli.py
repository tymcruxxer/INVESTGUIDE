"""CLI for source-agnostic verified data ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.database.session import SessionLocal
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.registry import build_default_registry
from app.services.ingestion.sources import CsvSourceAdapter, JsonSourceAdapter
from app.services.ingestion.types import EntityType, IngestionMode, SourceType


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run a verified data ingestion pipeline.")
    parser.add_argument("--entity", required=True, choices=[entity.value for entity in EntityType])
    parser.add_argument("--source-file", required=True)
    parser.add_argument("--source-name", default="Local Fixture")
    parser.add_argument("--source-type", default=SourceType.JSON_IMPORT.value, choices=[item.value for item in SourceType])
    parser.add_argument("--mode", default=IngestionMode.DRY_RUN.value, choices=[item.value for item in IngestionMode])
    parser.add_argument("--dataset-version", default=None)
    parser.add_argument("--development-data", action="store_true")
    parser.add_argument("--strict-validation", action="store_true")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    """Execute the ingestion CLI."""
    args = build_parser().parse_args(argv)
    entity = EntityType(args.entity)
    source_type = SourceType(args.source_type)
    mode = IngestionMode.STRICT if args.strict_validation else IngestionMode(args.mode)
    source_file = Path(args.source_file)
    source = (
        CsvSourceAdapter(
            source_file,
            source_name=args.source_name,
            source_type=source_type,
            dataset_version=args.dataset_version,
            is_development_data=args.development_data,
        )
        if source_file.suffix.lower() == ".csv"
        else JsonSourceAdapter(
            source_file,
            source_name=args.source_name,
            source_type=source_type,
            dataset_version=args.dataset_version,
            is_development_data=args.development_data,
        )
    )

    registry = build_default_registry()
    registration = registry.get(entity)
    pipeline = IngestionPipeline(
        entity=entity,
        source=source,
        normalizer=registration.normalizer,
        validator=registration.validator,
        importer=registration.importer,
    )
    with SessionLocal() as db:
        result = pipeline.run(db, mode=mode)

    print(
        json.dumps(
            {
                "run_id": result.run_id,
                "entity": result.entity.value,
                "mode": result.mode.value,
                "source": result.source.source_name,
                "total_records": result.total_records,
                "valid_records": result.valid_records,
                "rejected_records": result.rejected_records,
                "inserted": result.import_result.inserted,
                "updated": result.import_result.updated,
                "skipped": result.import_result.skipped,
                "errors": result.import_result.errors,
                "warnings": result.import_result.warnings,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if result.import_result.errors else 0


def main() -> None:
    """CLI entry point."""
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()

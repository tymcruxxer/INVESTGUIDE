"""CLI diagnostics for verified ingestion operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.database.session import SessionLocal
from app.services.data_quality import (
    company_quality_report,
    data_quality_summary,
    export_issues,
    get_run_detail,
    list_issues,
    list_runs,
    source_health,
)


def _print(data: Any, output_format: str = "table") -> None:
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str))
        return
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(" | ".join(f"{key}={value}" for key, value in item.items() if key in {"id", "entity", "source_name", "status", "current_health", "quality_score", "freshness_status"}))
            else:
                print(item)
        return
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect InvestGuide ingestion operations and data quality.")
    sub = parser.add_subparsers(dest="command", required=True)

    runs = sub.add_parser("runs")
    runs.add_argument("--format", choices=["table", "json"], default="table")
    runs.add_argument("--limit", type=int, default=25)

    sources = sub.add_parser("sources")
    sources.add_argument("--format", choices=["table", "json"], default="table")

    quality = sub.add_parser("quality")
    quality.add_argument("--format", choices=["table", "json"], default="table")

    company = sub.add_parser("company")
    company.add_argument("ticker")
    company.add_argument("--format", choices=["table", "json"], default="table")

    issues = sub.add_parser("issues")
    issues.add_argument("--run-id", type=int)
    issues.add_argument("--format", choices=["table", "json", "csv"], default="table")
    issues.add_argument("--output")

    detail = sub.add_parser("run")
    detail.add_argument("run_id", type=int)
    detail.add_argument("--format", choices=["table", "json"], default="table")

    args = parser.parse_args()
    with SessionLocal() as db:
        if args.command == "runs":
            result = list_runs(db, limit=args.limit).items
            _print(result, args.format)
        elif args.command == "sources":
            _print(source_health(db), args.format)
        elif args.command == "quality":
            result = data_quality_summary(db)
            _print(result if args.format == "json" else result["entities"], args.format)
        elif args.command == "company":
            result = company_quality_report(db, args.ticker)
            if result is None:
                raise SystemExit(f"Company {args.ticker} not found.")
            _print(result, args.format)
        elif args.command == "issues":
            if args.format in {"csv", "json"} and args.output:
                rendered = export_issues(db, run_id=args.run_id, output_format=args.format)
                Path(args.output).write_text(rendered, encoding="utf-8")
                print(f"Exported issues to {args.output}")
            elif args.format in {"csv", "json"}:
                print(export_issues(db, run_id=args.run_id, output_format=args.format))
            else:
                _print(list_issues(db, run_id=args.run_id).items, "table")
        elif args.command == "run":
            result = get_run_detail(db, args.run_id)
            if result is None:
                raise SystemExit(f"Run {args.run_id} not found.")
            _print(result, args.format)


if __name__ == "__main__":
    main()

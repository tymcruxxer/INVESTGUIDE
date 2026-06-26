"""CLI entrypoint for controlled backend submission."""

from __future__ import annotations

from dataclasses import asdict
import json

from scrapers.core.context_factory import ScraperContextFactory
from scrapers.pipeline.backend_client import BackendSubmissionClient, SubmissionReport
from scrapers.pipeline.ingestion_orchestrator import run_dry_ingestion
from scrapers.run_dry_ingestion import build_default_scrapers


def run_submission() -> SubmissionReport:
    """Run fixture ingestion flow and submit only if configured mode permits it."""
    report = run_dry_ingestion(build_default_scrapers())
    context = ScraperContextFactory().build("backend-submission")
    client = BackendSubmissionClient(context)
    return client.submit_payloads(report.payloads)


def format_submission_report(report: SubmissionReport) -> str:
    """Format a submission report as readable JSON."""
    return json.dumps(asdict(report), indent=2, sort_keys=True)


def main() -> None:
    """Run the controlled backend submission workflow."""
    print(format_submission_report(run_submission()))


if __name__ == "__main__":
    main()

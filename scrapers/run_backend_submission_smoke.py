"""Operator-run local DRY_RUN smoke test for backend submission."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Mapping

from scrapers.core.context_factory import ScraperContextFactory
from scrapers.core.http_client import HttpResponse, Transport
from scrapers.pipeline.backend_client import BackendSubmissionClient, SubmissionReport
from scrapers.pipeline.ingestion_orchestrator import run_dry_ingestion
from scrapers.run_dry_ingestion import build_default_scrapers


@dataclass(frozen=True)
class BackendSubmissionSmokeReport:
    """Operator-facing result for local backend DRY_RUN smoke validation."""

    backend_url: str
    health_url: str
    backend_available: bool
    attempted_submission: bool
    submission_report: SubmissionReport | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def build_smoke_context(env: Mapping[str, str] | None = None, transport: Transport | None = None):
    """Build a backend-submission context for smoke validation."""
    return ScraperContextFactory(env=env, transport=transport).build("backend-submission")


def health_url(context) -> str:
    """Return the backend health endpoint for the configured context."""
    return f"{context.config.backend_url.rstrip('/')}/api/{context.config.backend_api_version.strip('/')}/health"


def check_backend_health(context) -> tuple[bool, list[str]]:
    """Check backend health without raising on unavailable services."""
    url = health_url(context)
    try:
        response: HttpResponse = context.http_client.get(url)
    except Exception as exc:  # noqa: BLE001 - operator smoke should exit cleanly.
        return False, [f"Backend health check failed: {context.logger._sanitize(str(exc))}"]
    if response.status_code >= 400:
        return False, [f"Backend health check returned status {response.status_code}"]
    return True, []


def run_smoke(env: Mapping[str, str] | None = None, transport: Transport | None = None) -> BackendSubmissionSmokeReport:
    """Run local backend DRY_RUN smoke validation without ever using WRITE mode."""
    context = build_smoke_context(env=env, transport=transport)
    warnings: list[str] = []
    if context.config.backend_submission_mode != "DRY_RUN":
        return BackendSubmissionSmokeReport(
            backend_url=context.config.backend_url,
            health_url=health_url(context),
            backend_available=False,
            attempted_submission=False,
            warnings=["Smoke validation requires BACKEND_SUBMISSION_MODE=DRY_RUN; no submission attempted."],
        )

    available, errors = check_backend_health(context)
    if not available:
        return BackendSubmissionSmokeReport(
            backend_url=context.config.backend_url,
            health_url=health_url(context),
            backend_available=False,
            attempted_submission=False,
            errors=errors,
        )

    report = run_dry_ingestion(build_default_scrapers())
    submission_report = BackendSubmissionClient(context).submit_payloads(report.payloads)
    if submission_report.effective_mode != "DRY_RUN":
        warnings.append(f"Expected DRY_RUN submission, got {submission_report.effective_mode}; review configuration.")
    return BackendSubmissionSmokeReport(
        backend_url=context.config.backend_url,
        health_url=health_url(context),
        backend_available=True,
        attempted_submission=True,
        submission_report=submission_report,
        warnings=warnings,
    )


def format_smoke_report(report: BackendSubmissionSmokeReport) -> str:
    """Format the smoke report as stable JSON."""
    return json.dumps(asdict(report), indent=2, sort_keys=True)


def main() -> None:
    """Run the operator-controlled backend DRY_RUN smoke test."""
    print(format_smoke_report(run_smoke()))


if __name__ == "__main__":
    main()

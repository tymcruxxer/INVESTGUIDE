"""CLI entrypoint for backend ingestion handoff previews."""

from __future__ import annotations

import json

from scrapers.pipeline.backend_handoff import BackendHandoffPreview, build_backend_handoff_preview
from scrapers.pipeline.ingestion_orchestrator import IngestionDryRunReport, run_dry_ingestion
from scrapers.run_dry_ingestion import build_default_scrapers


def build_handoff_preview() -> BackendHandoffPreview:
    """Run fixture scrapers and build a backend ingestion request preview."""
    report = run_dry_ingestion(build_default_scrapers())
    return build_backend_handoff_preview(report.payloads, mode="DRY_RUN")


def format_preview(preview: BackendHandoffPreview) -> str:
    """Format the handoff preview as stable JSON for review."""
    return json.dumps(
        {
            "endpoint": preview.endpoint,
            "request": preview.request,
        },
        indent=2,
        sort_keys=True,
    )


def main() -> None:
    """Print the backend ingestion request preview without sending it."""
    print(format_preview(build_handoff_preview()))


if __name__ == "__main__":
    main()

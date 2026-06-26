"""Controlled backend submission client for scraper handoff payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from time import perf_counter
from typing import Any
from urllib.parse import urljoin

from scrapers.core.context import ScraperContext
from scrapers.core.http_client import HttpResponse
from scrapers.core.source_config import BackendSubmissionMode
from scrapers.pipeline.backend_handoff import (
    BACKEND_INGESTION_ENDPOINT,
    BackendIngestionRequest,
    build_backend_ingestion_request,
)
from scrapers.pipeline.ingestion_orchestrator import IngestionDryRunPayload


@dataclass(frozen=True)
class SubmissionReport:
    """Summary of a controlled backend submission attempt."""

    payload_count: int
    accepted: int = 0
    rejected: int = 0
    duplicates: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    backend_execution_time: float | None = None
    request_duration: float = 0.0
    mode: BackendSubmissionMode = "OFF"
    effective_mode: BackendSubmissionMode = "OFF"
    submitted: bool = False
    status_code: int | None = None


class BackendSubmissionClient:
    """Submit scraper payloads to the backend ingestion endpoint when enabled."""

    def __init__(self, context: ScraperContext) -> None:
        self.context = context

    def submit_payloads(self, payloads: list[IngestionDryRunPayload]) -> SubmissionReport:
        """Build and optionally send a backend ingestion request from dry-run payloads."""
        configured_mode = self.context.config.backend_submission_mode
        effective_mode, warnings = self._effective_mode(configured_mode)
        if effective_mode == "OFF":
            self._log_info("backend submission skipped", {"mode": configured_mode, "payload_count": len(payloads)})
            return SubmissionReport(
                payload_count=len(payloads),
                warnings=warnings,
                mode=configured_mode,
                effective_mode=effective_mode,
                submitted=False,
            )

        request_payload = build_backend_ingestion_request(payloads, mode=effective_mode)
        return self.submit_request(request_payload, configured_mode=configured_mode, warnings=warnings)

    def submit_request(
        self,
        request_payload: BackendIngestionRequest,
        configured_mode: BackendSubmissionMode | None = None,
        warnings: list[str] | None = None,
    ) -> SubmissionReport:
        """Send an already-built backend ingestion request through the shared HTTP client."""
        requested_mode = configured_mode or request_payload.get("mode", "OFF")
        effective_mode, mode_warnings = self._effective_mode(requested_mode)
        all_warnings = [*(warnings or []), *mode_warnings]
        request_payload = {"mode": effective_mode, "articles": request_payload["articles"]}
        if effective_mode == "OFF":
            return SubmissionReport(
                payload_count=len(request_payload["articles"]),
                warnings=all_warnings,
                mode=requested_mode,
                effective_mode=effective_mode,
                submitted=False,
            )

        endpoint = self.ingestion_url()
        start = perf_counter()
        self._log_info("backend submission started", {"endpoint": endpoint, "mode": effective_mode, "payload_count": len(request_payload["articles"])})
        try:
            response = self.context.http_client.post_json(endpoint, request_payload)
        except Exception as exc:  # noqa: BLE001 - convert transport failures into reports.
            duration = perf_counter() - start
            message = self.context.logger._sanitize(str(exc))
            self._log_error("backend submission failed", {"error": message, "request_duration": duration})
            return SubmissionReport(
                payload_count=len(request_payload["articles"]),
                rejected=len(request_payload["articles"]),
                warnings=all_warnings,
                errors=[message],
                request_duration=duration,
                mode=requested_mode,
                effective_mode=effective_mode,
                submitted=True,
            )

        duration = perf_counter() - start
        report = self._report_from_response(response, request_payload, requested_mode, effective_mode, all_warnings, duration)
        self._log_info("backend submission completed", {"status_code": response.status_code, "accepted": report.accepted, "rejected": report.rejected})
        return report

    def ingestion_url(self) -> str:
        """Return the configured backend ingestion endpoint URL."""
        base = self.context.config.backend_url.rstrip("/") + "/"
        path = f"api/{self.context.config.backend_api_version.strip('/')}/ingestion/news"
        return urljoin(base, path)

    def _effective_mode(self, configured_mode: str) -> tuple[BackendSubmissionMode, list[str]]:
        mode = configured_mode.strip().upper()
        if mode not in {"OFF", "DRY_RUN", "WRITE"}:
            return "OFF", [f"Unsupported backend submission mode {mode}; using OFF."]
        if mode == "WRITE" and not self.context.config.live_enabled:
            return "DRY_RUN", ["WRITE mode downgraded to DRY_RUN because SCRAPER_LIVE_ENABLED is not true."]
        return mode, []  # type: ignore[return-value]

    def _report_from_response(
        self,
        response: HttpResponse,
        request_payload: BackendIngestionRequest,
        configured_mode: BackendSubmissionMode,
        effective_mode: BackendSubmissionMode,
        warnings: list[str],
        request_duration: float,
    ) -> SubmissionReport:
        payload_count = len(request_payload["articles"])
        if response.status_code >= 400:
            return SubmissionReport(
                payload_count=payload_count,
                rejected=payload_count,
                warnings=warnings,
                errors=[f"Backend returned status {response.status_code}"],
                request_duration=request_duration,
                mode=configured_mode,
                effective_mode=effective_mode,
                submitted=True,
                status_code=response.status_code,
            )
        try:
            body = json.loads(response.text or "{}")
        except json.JSONDecodeError:
            return SubmissionReport(
                payload_count=payload_count,
                rejected=payload_count,
                warnings=warnings,
                errors=["Backend returned invalid JSON"],
                request_duration=request_duration,
                mode=configured_mode,
                effective_mode=effective_mode,
                submitted=True,
                status_code=response.status_code,
            )
        data = body.get("data", body) if isinstance(body, dict) else {}
        return SubmissionReport(
            payload_count=payload_count,
            accepted=int(data.get("articles_received", payload_count)) - int(data.get("failed_articles", 0)),
            rejected=int(data.get("failed_articles", 0)),
            duplicates=int(data.get("duplicates_skipped", 0)),
            warnings=[*warnings, *list(data.get("warnings", []))],
            errors=list(data.get("errors", [])),
            backend_execution_time=data.get("execution_time"),
            request_duration=request_duration,
            mode=configured_mode,
            effective_mode=effective_mode,
            submitted=True,
            status_code=response.status_code,
        )

    def _log_info(self, message: str, extra: dict[str, Any]) -> None:
        self.context.logger.logger.info(message, extra=extra)

    def _log_error(self, message: str, extra: dict[str, Any]) -> None:
        sanitized = {key: self.context.logger._sanitize(str(value)) for key, value in extra.items()}
        self.context.logger.logger.error(message, extra=sanitized)

"""Backend submission smoke command tests."""

from __future__ import annotations

import json

from scrapers.core.http_client import HttpRequest, HttpResponse
from scrapers.run_backend_submission_smoke import format_smoke_report, run_smoke


def _health_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status_code=200, text=json.dumps({"success": True}), url=request.url)


def _ingestion_response(request: HttpRequest) -> HttpResponse:
    body = {
        "success": True,
        "data": {
            "articles_received": 8,
            "articles_written": 0,
            "duplicates_skipped": 0,
            "failed_articles": 0,
            "assets_linked": 0,
            "execution_time": 0.03,
            "warnings": [],
            "errors": [],
            "mode": "DRY_RUN",
            "results": [],
        },
    }
    return HttpResponse(status_code=200, text=json.dumps(body), url=request.url)


def test_smoke_command_importability_and_default_safety() -> None:
    report = run_smoke(env={})
    output = format_smoke_report(report)

    assert report.attempted_submission is False
    assert "BACKEND_SUBMISSION_MODE=DRY_RUN" in report.warnings[0]
    assert '"attempted_submission": false' in output


def test_backend_unavailable_handling() -> None:
    def transport(request: HttpRequest) -> HttpResponse:
        raise ConnectionError("backend unavailable")

    report = run_smoke(env={"BACKEND_SUBMISSION_MODE": "DRY_RUN"}, transport=transport)

    assert report.backend_available is False
    assert report.attempted_submission is False
    assert "backend unavailable" in report.errors[0]


def test_smoke_submits_dry_run_request_mode() -> None:
    requests: list[HttpRequest] = []

    def transport(request: HttpRequest) -> HttpResponse:
        requests.append(request)
        if request.url.endswith("/health"):
            return _health_response(request)
        return _ingestion_response(request)

    report = run_smoke(env={"BACKEND_SUBMISSION_MODE": "DRY_RUN", "BACKEND_URL": "http://backend.test"}, transport=transport)
    sent = json.loads(requests[1].body.decode("utf-8"))

    assert report.backend_available is True
    assert report.attempted_submission is True
    assert report.submission_report is not None
    assert report.submission_report.effective_mode == "DRY_RUN"
    assert sent["mode"] == "DRY_RUN"
    assert requests[0].method == "GET"
    assert requests[1].method == "POST"


def test_smoke_response_parsing() -> None:
    def transport(request: HttpRequest) -> HttpResponse:
        if request.url.endswith("/health"):
            return _health_response(request)
        return _ingestion_response(request)

    report = run_smoke(env={"BACKEND_SUBMISSION_MODE": "DRY_RUN"}, transport=transport)

    assert report.submission_report is not None
    assert report.submission_report.accepted == 8
    assert report.submission_report.backend_execution_time == 0.03


def test_smoke_never_uses_write_mode() -> None:
    calls: list[HttpRequest] = []

    def transport(request: HttpRequest) -> HttpResponse:
        calls.append(request)
        return _health_response(request)

    report = run_smoke(env={"BACKEND_SUBMISSION_MODE": "WRITE", "SCRAPER_LIVE_ENABLED": "true"}, transport=transport)

    assert report.attempted_submission is False
    assert "DRY_RUN" in report.warnings[0]
    assert calls == []


"""Controlled backend submission client tests."""
from __future__ import annotations
import json
from scrapers.core.context_factory import ScraperContextFactory
from scrapers.core.http_client import HttpRequest, HttpResponse
from scrapers.pipeline.backend_client import BackendSubmissionClient
from scrapers.pipeline.ingestion_orchestrator import run_dry_ingestion
from scrapers.run_backend_submission import format_submission_report, run_submission
from scrapers.zse.live_announcements_scraper import ZSELiveAnnouncementsScraper

def _payloads():
    class FixtureZSEScraper(ZSELiveAnnouncementsScraper):
        def fetch(self):
            return '<a href="/delta-dividend-notice/">Delta Corporation Dividend Notice</a>'
    return run_dry_ingestion([FixtureZSEScraper()]).payloads

def _backend_response(request: HttpRequest, status_code: int = 200) -> HttpResponse:
    body = {"success": True, "data": {"articles_received": 1, "articles_written": 0, "duplicates_skipped": 0, "failed_articles": 0, "execution_time": 0.12, "warnings": ["dry-run only"], "errors": []}}
    return HttpResponse(status_code=status_code, text=json.dumps(body), url=request.url)

def test_off_mode_skips_backend_submission() -> None:
    calls: list[HttpRequest] = []
    context = ScraperContextFactory(env={"BACKEND_SUBMISSION_MODE": "OFF"}, transport=lambda request: calls.append(request)).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    assert report.effective_mode == "OFF"
    assert report.submitted is False
    assert report.payload_count == 1
    assert calls == []

def test_dry_run_mode_constructs_backend_request() -> None:
    calls: list[HttpRequest] = []
    def transport(request: HttpRequest) -> HttpResponse:
        calls.append(request)
        return _backend_response(request)
    env = {"BACKEND_SUBMISSION_MODE": "DRY_RUN", "BACKEND_URL": "http://backend.test", "BACKEND_API_VERSION": "v1"}
    context = ScraperContextFactory(env=env, transport=transport).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    sent = json.loads(calls[0].body.decode("utf-8"))
    assert report.submitted is True
    assert report.effective_mode == "DRY_RUN"
    assert report.accepted == 1
    assert calls[0].method == "POST"
    assert calls[0].url == "http://backend.test/api/v1/ingestion/news"
    assert calls[0].headers["Content-Type"] == "application/json"
    assert sent["mode"] == "DRY_RUN"
    assert sent["articles"][0]["source"] == "ZSE"

def test_write_mode_downgrades_without_live_enabled() -> None:
    calls: list[HttpRequest] = []
    def transport(request: HttpRequest) -> HttpResponse:
        calls.append(request)
        return _backend_response(request)
    context = ScraperContextFactory(env={"BACKEND_SUBMISSION_MODE": "WRITE"}, transport=transport).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    sent = json.loads(calls[0].body.decode("utf-8"))
    assert report.mode == "WRITE"
    assert report.effective_mode == "DRY_RUN"
    assert "downgraded" in report.warnings[0]
    assert sent["mode"] == "DRY_RUN"

def test_write_mode_allowed_when_live_enabled() -> None:
    calls: list[HttpRequest] = []
    def transport(request: HttpRequest) -> HttpResponse:
        calls.append(request)
        return _backend_response(request)
    env = {"BACKEND_SUBMISSION_MODE": "WRITE", "SCRAPER_LIVE_ENABLED": "true"}
    context = ScraperContextFactory(env=env, transport=transport).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    sent = json.loads(calls[0].body.decode("utf-8"))
    assert report.effective_mode == "WRITE"
    assert sent["mode"] == "WRITE"

def test_retry_handling_uses_context_retry_policy() -> None:
    calls = 0
    def transport(request: HttpRequest) -> HttpResponse:
        nonlocal calls
        calls += 1
        if calls == 1:
            return HttpResponse(status_code=503, text="temporary", url=request.url)
        return _backend_response(request)
    env = {"BACKEND_SUBMISSION_MODE": "DRY_RUN", "SCRAPER_BACKEND_SUBMISSION_RETRY_COUNT": "2"}
    context = ScraperContextFactory(env=env, transport=transport).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    assert calls == 2
    assert report.accepted == 1

def test_response_parsing_reports_errors() -> None:
    def transport(request: HttpRequest) -> HttpResponse:
        return HttpResponse(status_code=500, text="failed", url=request.url)
    context = ScraperContextFactory(env={"BACKEND_SUBMISSION_MODE": "DRY_RUN"}, transport=transport).build("backend-submission")
    report = BackendSubmissionClient(context).submit_payloads(_payloads())
    assert report.rejected == 1
    assert report.errors == ["Backend returned status 500"]

def test_cli_default_off_mode_makes_no_network_call(monkeypatch) -> None:
    monkeypatch.delenv("BACKEND_SUBMISSION_MODE", raising=False)
    report = run_submission()
    output = format_submission_report(report)
    assert report.effective_mode == "OFF"
    assert report.submitted is False
    assert '"effective_mode": "OFF"' in output

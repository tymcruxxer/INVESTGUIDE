
"""Backend handoff preview tests for scraper payloads."""


from __future__ import annotations

from pathlib import Path
import builtins
import socket

from scrapers.core.context_factory import ScraperContextFactory
from scrapers.core.http_client import HttpRequest, HttpResponse
from scrapers.pipeline.backend_handoff import BACKEND_INGESTION_ENDPOINT, build_backend_handoff_preview, build_backend_ingestion_request
from scrapers.pipeline.ingestion_orchestrator import run_dry_ingestion
from scrapers.run_handoff_preview import build_handoff_preview, format_preview
from scrapers.zse.live_announcements_scraper import ZSELiveAnnouncementsScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "zse_announcements_sample.html"

class FixtureZSEScraper(ZSELiveAnnouncementsScraper):
    def fetch(self):
        return FIXTURE_PATH.read_text(encoding="utf-8")

def test_backend_handoff_payload_shape() -> None:
    report = run_dry_ingestion([FixtureZSEScraper()])
    request = build_backend_ingestion_request(report.payloads)
    assert request["mode"] == "DRY_RUN"
    assert len(request["articles"]) == 3
    payload = request["articles"][0]
    assert payload["source"] == "ZSE"
    assert payload["asset_tickers"] == ["DELTA"]
    assert payload["credibility_score"] == "1.0"
    assert payload["published_at"] == "2026-06-20T07:30:00+00:00"
    assert payload["content_hash"]

def test_zse_output_is_compatible_with_handoff_preview() -> None:
    report = run_dry_ingestion([FixtureZSEScraper()])
    preview = build_backend_handoff_preview(report.payloads)
    assert preview.endpoint == BACKEND_INGESTION_ENDPOINT
    assert preview.request["articles"][0]["source"] == "ZSE"
    assert preview.request["articles"][0]["asset_tickers"] == ["DELTA"]

def test_handoff_preview_command_importability() -> None:
    preview = build_handoff_preview()
    output = format_preview(preview)
    assert preview.endpoint == "/api/v1/ingestion/news"
    assert "\"articles\"" in output
    assert "\"mode\": \"DRY_RUN\"" in output

def test_handoff_preview_makes_no_backend_http_call(monkeypatch) -> None:
    def fail_network(*args, **kwargs):
        raise AssertionError("backend HTTP calls are not allowed")
    monkeypatch.setattr(socket, "create_connection", fail_network)
    preview = build_handoff_preview()
    assert preview.request["mode"] == "DRY_RUN"
    assert len(preview.request["articles"]) > 0

def test_handoff_adapter_does_not_import_database(monkeypatch) -> None:
    original_import = builtins.__import__
    def guarded_import(name, *args, **kwargs):
        if name.startswith("backend") or name.startswith("app.database"):
            raise AssertionError("database imports are not allowed in scraper handoff")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    preview = build_handoff_preview()
    assert preview.request["mode"] == "DRY_RUN"

def test_live_mode_remains_disabled_by_default_for_handoff() -> None:
    requests: list[HttpRequest] = []
    def fake_transport(request: HttpRequest) -> HttpResponse:
        requests.append(request)
        return HttpResponse(status_code=200, text="unexpected", url=request.url)
    context = ScraperContextFactory(transport=fake_transport, env={}).build("zse")
    result = ZSELiveAnnouncementsScraper(context=context).run()
    assert context.config.live_enabled is False
    assert result.articles == []
    assert requests == []

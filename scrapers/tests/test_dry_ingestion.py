"""Dry-run ingestion orchestration tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import socket

from scrapers.base_scraper import BaseScraper
from scrapers.fixtures import FixtureScraper, sample_article
from scrapers.news.financial_gazette import FinancialGazetteScraper
from scrapers.news.newsday_business import NewsDayBusinessScraper
from scrapers.pipeline.ingestion_orchestrator import run_dry_ingestion
from scrapers.pipeline.source_trust import SourceTier, get_source_tier, get_source_trust_score
from scrapers.run_dry_ingestion import build_default_scrapers, format_report


class FailingDryRunScraper(BaseScraper):
    """Failing scraper used to verify orchestration error handling."""

    source_name = "Failing Fixture"
    source_url = "fixture://failing"

    def fetch(self):
        raise RuntimeError("fixture failure")

    def parse(self, raw_content):
        return []


class DuplicateFixtureScraper(FixtureScraper):
    """Fixture scraper that returns a duplicate of Financial Gazette output."""

    source_name = "Financial Gazette"
    source_url = "https://www.financialgazette.co.zw/"
    fixture_articles = [
        sample_article(
            title="Sample: Financial Gazette market news placeholder for Delta Corporation",
            source=source_name,
            url="fixture://financial-gazette/delta-market-placeholder",
            summary="Local fixture for future Financial Gazette business news ingestion.",
            content="This fixture mentions Delta Corporation for asset-linking tests only.",
        )
    ]


def test_source_trust_scoring() -> None:
    """Source trust maps known sources to expected tiers and scores."""
    assert get_source_tier("ZSE") == SourceTier.TIER_1_OFFICIAL
    assert get_source_trust_score("Reserve Bank of Zimbabwe") == 1.0
    assert get_source_tier("IH Securities") == SourceTier.TIER_2_INSTITUTIONAL
    assert get_source_trust_score("MMC Capital") == 0.85
    assert get_source_tier("Financial Gazette") == SourceTier.TIER_3_JOURNALISM
    assert get_source_trust_score("NewsDay Business") == 0.7
    assert get_source_tier("Unknown Blog") == SourceTier.TIER_4_GENERAL
    assert get_source_trust_score("Unknown Blog") == 0.4


def test_dry_run_orchestrator_success_path(monkeypatch) -> None:
    """Orchestrator runs fixture sources and returns report payloads."""

    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are not allowed")

    monkeypatch.setattr(socket, "create_connection", fail_network)

    report = run_dry_ingestion([FinancialGazetteScraper(), NewsDayBusinessScraper()])

    assert report.total_sources == 2
    assert report.successful_sources == 2
    assert report.failed_sources == 0
    assert report.total_articles_scraped == 2
    assert report.total_articles_after_deduplication == 2
    assert report.duplicates_removed == 0
    assert report.errors == []
    assert {payload.source for payload in report.payloads} == {"Financial Gazette", "NewsDay Business"}


def test_failed_scraper_handling() -> None:
    """Failed scrapers are represented in errors and source summaries."""
    report = run_dry_ingestion([FinancialGazetteScraper(), FailingDryRunScraper()])

    assert report.total_sources == 2
    assert report.successful_sources == 1
    assert report.failed_sources == 1
    assert report.errors == ["Failing Fixture: fixture failure"]
    failing_summary = report.source_summary[1]
    assert failing_summary.success is False
    assert failing_summary.errors == ["fixture failure"]


def test_deduplication_during_orchestration() -> None:
    """Duplicate articles are removed across source runs."""
    report = run_dry_ingestion([FinancialGazetteScraper(), DuplicateFixtureScraper()])

    assert report.total_articles_scraped == 2
    assert report.total_articles_after_deduplication == 1
    assert report.duplicates_removed == 1
    assert report.source_summary[1].duplicate_count == 1


def test_credibility_score_and_asset_ticker_linking_inside_payloads() -> None:
    """Payloads include source trust scores, content hashes, and linked tickers."""
    report = run_dry_ingestion([FinancialGazetteScraper(), NewsDayBusinessScraper()])
    payload_by_source = {payload.source: payload for payload in report.payloads}

    financial_gazette = payload_by_source["Financial Gazette"]
    assert financial_gazette.credibility_score == Decimal("0.7")
    assert financial_gazette.asset_tickers == ["DELTA"]
    assert financial_gazette.content_hash

    newsday = payload_by_source["NewsDay Business"]
    assert newsday.credibility_score == Decimal("0.7")
    assert newsday.asset_tickers == ["ECO"]


def test_cli_command_importability_and_report_format() -> None:
    """CLI helpers are importable and produce readable summaries."""
    scrapers = build_default_scrapers()
    report = run_dry_ingestion(scrapers)
    output = format_report(report)

    assert len(scrapers) == 8
    assert "InvestGuide News Ingestion Dry Run" in output
    assert "Sources run: 8" in output
    assert "Duplicates removed:" in output
    assert "credibility=" in output
    assert "Errors: none" in output


def test_orchestrator_does_not_require_database(monkeypatch) -> None:
    """The dry-run orchestrator does not import or call backend database sessions."""
    import builtins

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("backend") or name.startswith("app.database"):
            raise AssertionError("database imports are not allowed in dry-run ingestion")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    report = run_dry_ingestion([FinancialGazetteScraper()])

    assert report.total_articles_after_deduplication == 1
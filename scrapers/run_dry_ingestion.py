"""CLI entrypoint for dry-run news ingestion."""

from __future__ import annotations

from scrapers.news.financial_gazette import FinancialGazetteScraper
from scrapers.news.herald_business import HeraldBusinessScraper
from scrapers.news.newsday_business import NewsDayBusinessScraper
from scrapers.pipeline.ingestion_orchestrator import IngestionDryRunReport, run_dry_ingestion
from scrapers.rbz.macro_scraper import RBZMacroScraper
from scrapers.research.ih_securities import IHSecuritiesScraper
from scrapers.research.mmc_capital import MMCCapitalScraper
from scrapers.vfex.market_scraper import VFEXMarketScraper
from scrapers.zse.announcements_scraper import ZSEAnnouncementsScraper


def build_default_scrapers():
    """Return all fixture-only scraper sources for dry-run validation."""
    return [
        FinancialGazetteScraper(),
        NewsDayBusinessScraper(),
        HeraldBusinessScraper(),
        ZSEAnnouncementsScraper(),
        VFEXMarketScraper(),
        RBZMacroScraper(),
        IHSecuritiesScraper(),
        MMCCapitalScraper(),
    ]


def format_report(report: IngestionDryRunReport) -> str:
    """Format a readable dry-run ingestion report."""
    lines = [
        "InvestGuide News Ingestion Dry Run",
        "===================================",
        f"Sources run: {report.total_sources}",
        f"Successful sources: {report.successful_sources}",
        f"Failed sources: {report.failed_sources}",
        f"Articles scraped: {report.total_articles_scraped}",
        f"Articles after deduplication: {report.total_articles_after_deduplication}",
        f"Duplicates removed: {report.duplicates_removed}",
        "",
        "Source summary:",
    ]

    for summary in report.source_summary:
        status = "ok" if summary.success else "failed"
        lines.append(
            f"- {summary.source_name}: {status}; scraped={summary.scraped_count}; "
            f"payloads={summary.payload_count}; duplicates={summary.duplicate_count}; "
            f"trust={summary.trust_score:.2f} ({summary.trust_tier})"
        )

    lines.extend(["", "Payloads:"])
    for payload in report.payloads:
        tickers = ", ".join(payload.asset_tickers) if payload.asset_tickers else "none"
        lines.append(
            f"- {payload.title} | source={payload.source} | tickers={tickers} | "
            f"credibility={payload.credibility_score} | hash={payload.content_hash[:12]}"
        )

    if report.errors:
        lines.extend(["", "Errors:"])
        lines.extend(f"- {error}" for error in report.errors)
    else:
        lines.extend(["", "Errors: none"])

    return "\n".join(lines)


def main() -> None:
    """Run all fixture scrapers and print a dry-run report."""
    report = run_dry_ingestion(build_default_scrapers())
    print(format_report(report))


if __name__ == "__main__":
    main()
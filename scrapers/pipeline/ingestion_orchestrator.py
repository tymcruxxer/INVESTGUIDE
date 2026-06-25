"""Dry-run news ingestion orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from scrapers.base_scraper import BaseScraper, ScrapedArticle
from scrapers.pipeline.deduplicator import DeduplicationIndex
from scrapers.pipeline.ingestion_contract import NormalizedArticlePayload, build_ingestion_payload
from scrapers.pipeline.normalizer import normalize_article
from scrapers.pipeline.source_trust import SourceTier, get_source_tier, get_source_trust_score


@dataclass(frozen=True)
class IngestionDryRunPayload:
    """Report-safe payload describing what would be persisted."""

    title: str
    source: str
    url: str | None
    published_at: datetime
    asset_tickers: list[str]
    credibility_score: Decimal
    content_hash: str
    source_tier: SourceTier


@dataclass(frozen=True)
class SourceDryRunSummary:
    """Per-source dry-run summary."""

    source_name: str
    source_url: str
    success: bool
    scraped_count: int = 0
    payload_count: int = 0
    duplicate_count: int = 0
    errors: list[str] = field(default_factory=list)
    trust_tier: SourceTier = SourceTier.TIER_4_GENERAL
    trust_score: float = 0.4


@dataclass(frozen=True)
class IngestionDryRunReport:
    """Dry-run ingestion report for scraper output."""

    total_sources: int
    successful_sources: int
    failed_sources: int
    total_articles_scraped: int
    total_articles_after_deduplication: int
    duplicates_removed: int
    payloads: list[IngestionDryRunPayload]
    errors: list[str]
    source_summary: list[SourceDryRunSummary]


def _payload_from_normalized_article(article: ScrapedArticle) -> NormalizedArticlePayload:
    payload = build_ingestion_payload(article)
    trust_score = Decimal(str(get_source_trust_score(article.source)))
    return NormalizedArticlePayload(
        title=payload.title,
        source=payload.source,
        published_at=payload.published_at,
        summary=payload.summary,
        content=payload.content,
        url=payload.url,
        image_url=payload.image_url,
        author=payload.author,
        language=payload.language,
        asset_tickers=payload.asset_tickers,
        sentiment=payload.sentiment,
        relevance_score=payload.relevance_score,
        credibility_score=trust_score,
        content_hash=payload.content_hash,
    )


def _report_payload(payload: NormalizedArticlePayload) -> IngestionDryRunPayload:
    if payload.content_hash is None:
        raise ValueError("Ingestion payload content_hash is required for dry-run reporting")
    if payload.credibility_score is None:
        raise ValueError("Ingestion payload credibility_score is required for dry-run reporting")
    return IngestionDryRunPayload(
        title=payload.title,
        source=payload.source,
        url=payload.url,
        published_at=payload.published_at,
        asset_tickers=payload.asset_tickers,
        credibility_score=payload.credibility_score,
        content_hash=payload.content_hash,
        source_tier=get_source_tier(payload.source),
    )


def run_dry_ingestion(scrapers: Iterable[BaseScraper]) -> IngestionDryRunReport:
    """Run fixture scrapers through normalization, deduplication, and payload building.

    This function intentionally performs no database writes and has no external
    network behavior of its own. Source scrapers are expected to be fixture-only
    until live fetching is introduced in a later sprint.
    """
    scraper_list = list(scrapers)
    dedupe_index = DeduplicationIndex.empty()
    payloads: list[IngestionDryRunPayload] = []
    errors: list[str] = []
    source_summaries: list[SourceDryRunSummary] = []
    total_articles_scraped = 0
    duplicates_removed = 0
    successful_sources = 0

    for scraper in scraper_list:
        result = scraper.run()
        trust_tier = get_source_tier(result.source_name)
        trust_score = get_source_trust_score(result.source_name)
        scraped_count = len(result.articles)
        total_articles_scraped += scraped_count

        if not result.success:
            source_errors = [f"{result.source_name}: {error}" for error in result.errors]
            errors.extend(source_errors)
            source_summaries.append(
                SourceDryRunSummary(
                    source_name=result.source_name,
                    source_url=result.source_url,
                    success=False,
                    scraped_count=scraped_count,
                    errors=result.errors,
                    trust_tier=trust_tier,
                    trust_score=trust_score,
                )
            )
            continue

        successful_sources += 1
        source_payload_count = 0
        source_duplicate_count = 0

        for raw_article in result.articles:
            article = normalize_article(raw_article)
            if dedupe_index.is_duplicate(article):
                duplicates_removed += 1
                source_duplicate_count += 1
                continue
            dedupe_index.add(article)
            payload = _payload_from_normalized_article(article)
            payloads.append(_report_payload(payload))
            source_payload_count += 1

        source_summaries.append(
            SourceDryRunSummary(
                source_name=result.source_name,
                source_url=result.source_url,
                success=True,
                scraped_count=scraped_count,
                payload_count=source_payload_count,
                duplicate_count=source_duplicate_count,
                trust_tier=trust_tier,
                trust_score=trust_score,
            )
        )

    return IngestionDryRunReport(
        total_sources=len(scraper_list),
        successful_sources=successful_sources,
        failed_sources=len(scraper_list) - successful_sources,
        total_articles_scraped=total_articles_scraped,
        total_articles_after_deduplication=len(payloads),
        duplicates_removed=duplicates_removed,
        payloads=payloads,
        errors=errors,
        source_summary=source_summaries,
    )
"""Internal news ingestion adapter."""

from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.news import News
from app.schemas.ingestion_report import (
    IngestionArticlePayload,
    IngestionArticleResult,
    IngestionMode,
    IngestionReport,
)
from app.services.asset_resolution_service import resolve_assets
from app.services.duplicate_service import check_news_duplicate, incoming_content_hash


def _resolve_mode(mode: str | None) -> IngestionMode:
    resolved = (mode or get_settings().ingestion_mode).strip().upper()
    if resolved not in {"DRY_RUN", "WRITE"}:
        raise ValueError("INGESTION_MODE must be DRY_RUN or WRITE")
    return resolved  # type: ignore[return-value]


def _payload_to_news(payload: IngestionArticlePayload, assets: list[Any], content_hash: str) -> News:
    return News(
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        content_hash=content_hash,
        source=payload.source,
        author=payload.author,
        published_at=payload.published_at,
        url=payload.url,
        image_url=payload.image_url,
        language=payload.language,
        sentiment=payload.sentiment,
        relevance_score=payload.relevance_score,
        credibility_score=payload.credibility_score,
        assets=assets,
    )


def ingest_news_payloads(
    db: Session,
    payloads: Sequence[IngestionArticlePayload | dict[str, Any]],
    mode: str | None = None,
) -> IngestionReport:
    """Validate, deduplicate, resolve assets, and optionally persist news payloads."""
    start = perf_counter()
    resolved_mode = _resolve_mode(mode)
    results: list[IngestionArticleResult] = []
    errors: list[str] = []
    warnings: list[str] = []
    articles_written = 0
    duplicates_skipped = 0
    failed_articles = 0
    assets_linked_count = 0

    for raw_payload in payloads:
        try:
            payload = IngestionArticlePayload.model_validate(raw_payload)
        except ValidationError as exc:
            failed_articles += 1
            message = f"Invalid ingestion payload: {exc.errors()}"
            errors.append(message)
            results.append(IngestionArticleResult(status="FAILED", errors=[message]))
            continue

        article_warnings: list[str] = []
        article_errors: list[str] = []

        try:
            content_hash = incoming_content_hash(payload)
            duplicate_status = check_news_duplicate(db, payload)
            if duplicate_status in {"DUPLICATE", "POSSIBLE_DUPLICATE"}:
                duplicates_skipped += 1
                message = f"Article skipped as {duplicate_status.lower().replace('_', ' ')}"
                article_warnings.append(message)
                warnings.append(f"{payload.title}: {message}")
                results.append(
                    IngestionArticleResult(
                        title=payload.title,
                        source=payload.source,
                        url=payload.url,
                        status=duplicate_status,
                        duplicate_status=duplicate_status,
                        asset_tickers=payload.asset_tickers,
                        warnings=article_warnings,
                    )
                )
                continue

            asset_resolution = resolve_assets(db, payload.asset_tickers)
            if asset_resolution.missing_tickers:
                message = f"Missing asset tickers: {', '.join(asset_resolution.missing_tickers)}"
                article_warnings.append(message)
                warnings.append(f"{payload.title}: {message}")
            if asset_resolution.inactive_tickers:
                message = f"Inactive asset tickers skipped: {', '.join(asset_resolution.inactive_tickers)}"
                article_warnings.append(message)
                warnings.append(f"{payload.title}: {message}")

            if resolved_mode == "DRY_RUN":
                assets_linked_count += len(asset_resolution.found_assets)
                results.append(
                    IngestionArticleResult(
                        title=payload.title,
                        source=payload.source,
                        url=payload.url,
                        status="DRY_RUN",
                        duplicate_status="NEW",
                        asset_tickers=payload.asset_tickers,
                        assets_linked=asset_resolution.linked_tickers,
                        warnings=article_warnings,
                    )
                )
                continue

            article = _payload_to_news(payload, asset_resolution.found_assets, content_hash)
            db.add(article)
            db.commit()
            db.refresh(article)
            articles_written += 1
            assets_linked_count += len(asset_resolution.found_assets)
            results.append(
                IngestionArticleResult(
                    title=payload.title,
                    source=payload.source,
                    url=payload.url,
                    status="WRITTEN",
                    duplicate_status="NEW",
                    news_id=article.id,
                    asset_tickers=payload.asset_tickers,
                    assets_linked=asset_resolution.linked_tickers,
                    warnings=article_warnings,
                )
            )
        except Exception as exc:  # noqa: BLE001 - report ingestion failures without crashing batch processing.
            db.rollback()
            failed_articles += 1
            message = f"Failed to ingest '{payload.title}': {exc}"
            article_errors.append(message)
            errors.append(message)
            results.append(
                IngestionArticleResult(
                    title=payload.title,
                    source=payload.source,
                    url=payload.url,
                    status="FAILED",
                    duplicate_status=None,
                    asset_tickers=payload.asset_tickers,
                    warnings=article_warnings,
                    errors=article_errors,
                )
            )

    return IngestionReport(
        articles_received=len(payloads),
        articles_written=articles_written,
        duplicates_skipped=duplicates_skipped,
        failed_articles=failed_articles,
        assets_linked=assets_linked_count,
        execution_time=round(perf_counter() - start, 6),
        errors=errors,
        warnings=warnings,
        mode=resolved_mode,
        results=results,
    )
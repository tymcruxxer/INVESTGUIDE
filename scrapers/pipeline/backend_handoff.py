"""Backend ingestion handoff formatting for scraper dry-run payloads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Literal, TypedDict

from scrapers.pipeline.ingestion_orchestrator import IngestionDryRunPayload

BackendIngestionMode = Literal["DRY_RUN", "WRITE"]
BACKEND_INGESTION_ENDPOINT = "/api/v1/ingestion/news"


class BackendArticlePayload(TypedDict, total=False):
    """JSON-compatible article payload for the backend ingestion endpoint."""

    title: str
    source: str
    published_at: str
    summary: str | None
    content: str | None
    url: str | None
    image_url: str | None
    author: str | None
    language: str
    asset_tickers: list[str]
    sentiment: str | None
    relevance_score: str | None
    credibility_score: str | None
    content_hash: str


class BackendIngestionRequest(TypedDict):
    """JSON-compatible request body for /api/v1/ingestion/news."""

    mode: BackendIngestionMode
    articles: list[BackendArticlePayload]


@dataclass(frozen=True)
class BackendHandoffPreview:
    """Preview object describing the request that would be sent later."""

    endpoint: str
    request: BackendIngestionRequest


def _decimal_to_json(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _datetime_to_json(value: datetime) -> str:
    return value.isoformat()


def dry_run_payload_to_backend_article(payload: IngestionDryRunPayload) -> BackendArticlePayload:
    """Convert one dry-run payload into the backend ingestion article contract."""
    return {
        "title": payload.title,
        "source": payload.source,
        "published_at": _datetime_to_json(payload.published_at),
        "summary": None,
        "content": None,
        "url": payload.url,
        "image_url": None,
        "author": None,
        "language": "en",
        "asset_tickers": list(payload.asset_tickers),
        "sentiment": None,
        "relevance_score": None,
        "credibility_score": _decimal_to_json(payload.credibility_score),
        "content_hash": payload.content_hash,
    }


def build_backend_ingestion_request(
    payloads: Iterable[IngestionDryRunPayload],
    mode: BackendIngestionMode = "DRY_RUN",
) -> BackendIngestionRequest:
    """Build the backend ingestion request body without sending it."""
    return {
        "mode": mode,
        "articles": [dry_run_payload_to_backend_article(payload) for payload in payloads],
    }


def build_backend_handoff_preview(
    payloads: Iterable[IngestionDryRunPayload],
    mode: BackendIngestionMode = "DRY_RUN",
) -> BackendHandoffPreview:
    """Return endpoint metadata and request JSON for operator review."""
    return BackendHandoffPreview(
        endpoint=BACKEND_INGESTION_ENDPOINT,
        request=build_backend_ingestion_request(payloads, mode=mode),
    )

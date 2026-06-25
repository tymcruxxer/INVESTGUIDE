"""News ingestion adapter tests."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.news import News
from app.schemas.ingestion_report import IngestionArticlePayload
from app.services.asset_resolution_service import resolve_assets
from app.services.duplicate_service import check_news_duplicate
from app.services.ingestion_service import ingest_news_payloads
from app.utils.hashing import generate_content_hash


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    session.add_all(
        [
            Asset(
                ticker="DLTA",
                company_name="Delta Corporation Limited",
                exchange=Exchange.ZSE,
                sector="Consumer Staples",
                industry="Beverages",
                asset_type=AssetType.EQUITY,
                currency=Currency.ZWG,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                ticker="ECO",
                company_name="Econet Wireless Zimbabwe Limited",
                exchange=Exchange.ZSE,
                sector="Telecommunications",
                industry="Mobile Telecommunications",
                asset_type=AssetType.EQUITY,
                currency=Currency.ZWG,
                status=AssetStatus.SUSPENDED,
            ),
        ]
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def make_payload(**overrides: object) -> IngestionArticlePayload:
    """Create a normalized ingestion payload for tests."""
    data = {
        "title": "Delta Corporation market update",
        "summary": "Development-only market context for Delta.",
        "content": "Sample normalized article for backend ingestion testing.",
        "source": "Financial Gazette",
        "published_at": datetime(2026, 6, 25, 8, 0, tzinfo=UTC),
        "url": "https://example.com/delta-update",
        "language": "en",
        "asset_tickers": ["DLTA"],
        "credibility_score": "0.7",
    }
    data.update(overrides)
    payload = IngestionArticlePayload.model_validate(data)
    if payload.content_hash is None:
        payload = payload.model_copy(
            update={
                "content_hash": generate_content_hash(
                    payload.title,
                    payload.summary,
                    payload.content,
                )
            }
        )
    return payload


def test_ingestion_route_is_registered() -> None:
    """Internal ingestion route is mounted under the versioned API."""
    routes = {route.path for route in app.routes}

    assert "/api/v1/ingestion/news" in routes


def test_asset_resolution_reports_active_missing_and_inactive_assets(db_session: Session) -> None:
    """Asset resolution links only active assets and reports unresolved tickers."""
    result = resolve_assets(db_session, ["dlta", "eco", "missing", "DLTA"])

    assert result.linked_tickers == ["DLTA"]
    assert result.inactive_tickers == ["ECO"]
    assert result.missing_tickers == ["MISSING"]


def test_duplicate_service_detects_url_hash_and_possible_title_duplicates(db_session: Session) -> None:
    """Duplicate checks cover URL, content hash, and possible title matches."""
    payload = make_payload()
    db_session.add(
        News(
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            source=payload.source,
            published_at=payload.published_at,
            url=payload.url,
        )
    )
    db_session.commit()

    assert check_news_duplicate(db_session, payload) == "DUPLICATE"

    hash_duplicate = make_payload(url="https://example.com/different-url")
    assert check_news_duplicate(db_session, hash_duplicate) == "DUPLICATE"

    possible_duplicate = make_payload(
        title="Delta Corporation market update",
        content="Different body text.",
        url="https://example.com/new-title-match",
        published_at=datetime(2026, 6, 26, 8, 0, tzinfo=UTC),
        content_hash="different-hash",
    )
    assert check_news_duplicate(db_session, possible_duplicate) == "POSSIBLE_DUPLICATE"


def test_ingestion_service_dry_run_does_not_write_to_database(db_session: Session) -> None:
    """Dry-run mode produces a report without inserting news rows."""
    report = ingest_news_payloads(db_session, [make_payload()], mode="DRY_RUN")

    assert report.mode == "DRY_RUN"
    assert report.articles_received == 1
    assert report.articles_written == 0
    assert report.assets_linked == 1
    assert report.results[0].status == "DRY_RUN"
    assert db_session.scalar(select(func.count()).select_from(News)) == 0


def test_ingestion_service_write_mode_persists_article_and_links_assets(db_session: Session) -> None:
    """Write mode persists a new article after duplicate and asset checks pass."""
    payload = make_payload()
    report = ingest_news_payloads(db_session, [payload], mode="WRITE")
    article = db_session.scalar(select(News).where(News.title == "Delta Corporation market update"))

    assert report.mode == "WRITE"
    assert report.articles_written == 1
    assert report.assets_linked == 1
    assert report.results[0].status == "WRITTEN"
    assert article is not None
    assert [asset.ticker for asset in article.assets] == ["DLTA"]
    assert article.content_hash == generate_content_hash(payload.title, payload.summary, payload.content)


def test_ingestion_service_skips_definite_duplicates(db_session: Session) -> None:
    """Duplicate articles are skipped and not written again."""
    payload = make_payload()
    db_session.add(
        News(
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            source=payload.source,
            published_at=payload.published_at,
            url=payload.url,
        )
    )
    db_session.commit()

    report = ingest_news_payloads(db_session, [payload], mode="WRITE")

    assert report.duplicates_skipped == 1
    assert report.articles_written == 0
    assert report.results[0].status == "DUPLICATE"


def test_ingestion_service_handles_missing_assets_gracefully(db_session: Session) -> None:
    """Missing tickers create warnings instead of failing ingestion."""
    payload = make_payload(asset_tickers=["MISSING"], url="https://example.com/missing-asset")

    report = ingest_news_payloads(db_session, [payload], mode="WRITE")

    assert report.articles_written == 1
    assert report.assets_linked == 0
    assert "Missing asset tickers: MISSING" in report.results[0].warnings


def test_ingestion_service_rejects_malformed_payload_without_write(db_session: Session) -> None:
    """Malformed normalized payloads are rejected and reported."""
    report = ingest_news_payloads(db_session, [{"source": "Financial Gazette"}], mode="WRITE")

    assert report.failed_articles == 1
    assert report.articles_written == 0
    assert report.results[0].status == "FAILED"


def test_ingestion_service_rolls_back_failed_write(monkeypatch, db_session: Session) -> None:
    """A write failure rolls back the article insert."""

    def fail_commit() -> None:
        raise RuntimeError("commit failed")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    payload = make_payload()
    report = ingest_news_payloads(db_session, [payload], mode="WRITE")

    assert report.failed_articles == 1
    assert report.articles_written == 0
    assert report.results[0].status == "FAILED"
    assert db_session.scalar(select(News).where(News.title == "Delta Corporation market update")) is None


def test_ingestion_endpoint_returns_response_envelope_without_live_database(db_session: Session) -> None:
    """Route uses dependency overrides so tests do not need PostgreSQL."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        response = client.post(
            "/api/v1/ingestion/news",
            json={
                "mode": "DRY_RUN",
                "articles": [make_payload().model_dump(mode="json")],
            },
        )
    finally:
        app.dependency_overrides.clear()

    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "News ingestion completed"
    assert body["data"]["mode"] == "DRY_RUN"
    assert body["data"]["articles_written"] == 0
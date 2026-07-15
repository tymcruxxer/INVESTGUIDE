"""Tests for the verified data ingestion pipeline framework."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models.asset import Asset
from app.models.company import Company
from app.models.company_profile import CompanyProfile
from app.models.dividend import CorporateAction
from app.models.dividend import Dividend
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement
from app.models.ingestion import IngestionRun
from app.models.market_snapshot import MarketSnapshot
from app.models.news import News
from app.services.market_snapshot_service import get_latest_company_reference_snapshot
from app.services.ingestion import EntityType, IngestionMode, SourceType
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.registry import build_default_registry
from app.services.ingestion.sources import CsvSourceAdapter, JsonSourceAdapter
from app.services.intelligence.dividend_engine import build_dividend_intelligence
from app.services.intelligence.financial_engine import build_financial_intelligence

FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an in-memory database with all current models."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _pipeline(entity: EntityType, source_file: str, source_type: SourceType = SourceType.DEVELOPMENT_FIXTURE) -> IngestionPipeline:
    registry = build_default_registry()
    registration = registry.get(entity)
    source = JsonSourceAdapter(
        FIXTURES / source_file,
        source_name="Development Fixture",
        source_type=source_type,
        dataset_version="test",
        is_development_data=True,
    )
    return IngestionPipeline(entity, source, registration.normalizer, registration.validator, registration.importer)


def test_json_source_adapter_loads_metadata() -> None:
    """JSON source adapter reports checksum, count, and development status."""
    source = JsonSourceAdapter(
        FIXTURES / "companies.json",
        source_name="Development Fixture",
        source_type=SourceType.DEVELOPMENT_FIXTURE,
        is_development_data=True,
    )

    dataset = source.load()

    assert dataset.metadata.record_count == 2
    assert dataset.metadata.checksum
    assert dataset.metadata.is_development_data is True


def test_csv_source_adapter_loads_records() -> None:
    """CSV source adapter supports local file imports."""
    source = CsvSourceAdapter(
        FIXTURES / "companies.csv",
        source_name="CSV Fixture",
        source_type=SourceType.CSV_IMPORT,
        is_development_data=True,
    )

    dataset = source.load()

    assert dataset.records[0]["ticker"] == "TIGERE"
    assert dataset.metadata.record_count == 1


def test_registry_supports_core_runtime_entities() -> None:
    """Default registry wires core persisted entities to components."""
    supported = set(build_default_registry().supported_entities())

    assert EntityType.COMPANIES in supported
    assert EntityType.INCOME_STATEMENTS in supported
    assert EntityType.DIVIDENDS in supported
    assert EntityType.NEWS in supported


def test_dry_run_does_not_insert_entities_but_records_audit(db_session: Session) -> None:
    """Dry-run validates and plans imports without writing entity rows."""
    result = _pipeline(EntityType.COMPANIES, "companies.json").run(db_session)

    assert result.mode == IngestionMode.DRY_RUN
    assert result.import_result.inserted == 2
    assert db_session.scalars(select(Company)).all() == []
    assert db_session.scalar(select(IngestionRun)) is not None


def test_lenient_company_import_is_idempotent(db_session: Session) -> None:
    """Lenient imports upsert by deterministic company identity."""
    pipeline = _pipeline(EntityType.COMPANIES, "companies.json")

    first = pipeline.run(db_session, IngestionMode.LENIENT)
    second = pipeline.run(db_session, IngestionMode.LENIENT)

    assert first.import_result.inserted == 2
    assert second.import_result.inserted == 0
    assert second.import_result.updated + second.import_result.skipped == 2
    assert len(db_session.scalars(select(Company)).all()) == 2


def test_strict_mode_rejects_invalid_batch_without_entity_writes(db_session: Session) -> None:
    """Strict mode rejects an invalid batch and avoids entity writes."""
    registry = build_default_registry()
    registration = registry.get(EntityType.COMPANIES)
    bad_source = JsonSourceAdapter(
        FIXTURES / "companies.json",
        source_name="Bad Fixture",
        source_type=SourceType.DEVELOPMENT_FIXTURE,
        is_development_data=True,
    )
    loaded = bad_source.load()
    loaded.records[0]["exchange"] = "BAD"

    class InlineSource:
        def load(self):
            return loaded

    pipeline = IngestionPipeline(EntityType.COMPANIES, InlineSource(), registration.normalizer, registration.validator, registration.importer)
    result = pipeline.run(db_session, IngestionMode.STRICT)

    assert result.rejected_records == 1
    assert result.import_result.rejected == 1
    assert db_session.scalars(select(Company)).all() == []


def test_income_dividend_and_news_imports_feed_existing_engines(db_session: Session) -> None:
    """Imported fixture rows are consumable by existing deterministic engines."""
    _pipeline(EntityType.COMPANIES, "companies.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.INCOME_STATEMENTS, "financial_statements.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.DIVIDENDS, "dividends.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.NEWS, "news.json").run(db_session, IngestionMode.LENIENT)

    delta = db_session.scalar(select(Company).where(Company.ticker == "DLTA"))
    assert delta is not None
    assert db_session.scalar(select(IncomeStatement).where(IncomeStatement.company_id == delta.id)) is not None
    assert db_session.scalar(select(Dividend).where(Dividend.company_id == delta.id)) is not None
    assert db_session.scalar(select(News)) is not None

    financial_rows = db_session.scalars(select(IncomeStatement).where(IncomeStatement.company_id == delta.id)).all()
    dividend_rows = db_session.scalars(select(Dividend).where(Dividend.company_id == delta.id)).all()

    financial = build_financial_intelligence(delta, income_statements=financial_rows, balance_sheets=[], cash_flow_statements=[])
    dividend = build_dividend_intelligence(delta, dividends=dividend_rows, income_statements=financial_rows)

    assert financial["ticker"] == "DLTA"
    assert dividend["ticker"] == "DLTA"




def test_registry_includes_all_supported_entities() -> None:
    """Sprint 048 completes the registry for every major ingestion entity."""
    supported = {entity.value for entity in build_default_registry().supported_entities()}

    assert supported == {
        "assets",
        "balance_sheets",
        "cash_flow_statements",
        "companies",
        "company_profiles",
        "corporate_actions",
        "dividends",
        "income_statements",
        "market_snapshots",
        "news",
    }


def test_all_remaining_entities_import_idempotently(db_session: Session) -> None:
    """New Sprint 048 entities import through the same pipeline and rerun safely."""
    _pipeline(EntityType.COMPANIES, "companies.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.ASSETS, "assets.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.COMPANY_PROFILES, "company_profiles.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.BALANCE_SHEETS, "balance_sheets.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.CASH_FLOW_STATEMENTS, "cash_flow_statements.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.CORPORATE_ACTIONS, "corporate_actions.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.MARKET_SNAPSHOTS, "market_snapshots.json").run(db_session, IngestionMode.LENIENT)
    rerun = _pipeline(EntityType.MARKET_SNAPSHOTS, "market_snapshots.json").run(db_session, IngestionMode.LENIENT)

    assert db_session.scalar(select(Asset).where(Asset.ticker == "DLTA")) is not None
    assert db_session.scalar(select(CompanyProfile)) is not None
    assert db_session.scalar(select(BalanceSheet)) is not None
    assert db_session.scalar(select(CashFlowStatement)) is not None
    assert db_session.scalar(select(CorporateAction)) is not None
    assert db_session.scalar(select(MarketSnapshot)) is not None
    assert rerun.import_result.inserted == 0
    assert rerun.import_result.updated >= 1


def test_balance_cash_and_market_validators_report_warnings_and_rejections(db_session: Session) -> None:
    """Validators distinguish warning rows from rejected rows for Sprint 048 entities."""
    _pipeline(EntityType.COMPANIES, "companies.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.ASSETS, "assets.json").run(db_session, IngestionMode.LENIENT)

    balance = _pipeline(EntityType.BALANCE_SHEETS, "balance_sheets.json").run(db_session, IngestionMode.DRY_RUN)
    cash = _pipeline(EntityType.CASH_FLOW_STATEMENTS, "cash_flow_statements.json").run(db_session, IngestionMode.DRY_RUN)
    market = _pipeline(EntityType.MARKET_SNAPSHOTS, "market_snapshots.json").run(db_session, IngestionMode.DRY_RUN)

    assert balance.rejected_records == 1
    assert cash.rejected_records == 1
    assert market.rejected_records == 1

    audit_rows = db_session.scalars(select(IngestionRun)).all()
    assert {row.entity for row in audit_rows} >= {"balance_sheets", "cash_flow_statements", "market_snapshots"}


def test_market_snapshot_feeds_dividend_reference_price(db_session: Session) -> None:
    """Dividend Intelligence can use a pipeline-imported market snapshot reference price."""
    _pipeline(EntityType.COMPANIES, "companies.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.ASSETS, "assets.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.INCOME_STATEMENTS, "financial_statements.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.BALANCE_SHEETS, "balance_sheets.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.CASH_FLOW_STATEMENTS, "cash_flow_statements.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.DIVIDENDS, "dividends.json").run(db_session, IngestionMode.LENIENT)
    _pipeline(EntityType.MARKET_SNAPSHOTS, "market_snapshots.json").run(db_session, IngestionMode.LENIENT)

    company = db_session.scalar(select(Company).where(Company.ticker == "DLTA"))
    assert company is not None
    snapshot = get_latest_company_reference_snapshot(db_session, company.id)
    assert snapshot is not None
    income = db_session.scalars(select(IncomeStatement).where(IncomeStatement.company_id == company.id)).all()
    balance = db_session.scalars(select(BalanceSheet).where(BalanceSheet.company_id == company.id)).all()
    cash = db_session.scalars(select(CashFlowStatement).where(CashFlowStatement.company_id == company.id)).all()
    dividends = db_session.scalars(select(Dividend).where(Dividend.company_id == company.id)).all()

    financial = build_financial_intelligence(company, income_statements=income, balance_sheets=balance, cash_flow_statements=cash)
    dividend = build_dividend_intelligence(
        company,
        dividends=dividends,
        income_statements=income,
        cash_flow_statements=cash,
        reference_price=float(snapshot.price),
        price_date=snapshot.snapshot_date.isoformat(),
    )

    assert financial["transparency"]["evidence_used"]
    assert dividend["dividend_yield"]["status"] == "Available"
    assert dividend["dividend_yield"]["price_date"] == snapshot.snapshot_date.isoformat()


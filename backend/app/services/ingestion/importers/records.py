"""Database importers for verified data pipeline records."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Protocol, cast

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.dividend import CorporateAction, CorporateActionType, Dividend, DividendType
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement, StatementPeriod
from app.models.market_snapshot import MarketSnapshot
from app.models.news import News
from app.services.ingestion.types import (
    BaseNormalizedRecord,
    ImportResult,
    IngestionMode,
    NormalizedAsset,
    NormalizedBalanceSheet,
    NormalizedCashFlowStatement,
    NormalizedCompany,
    NormalizedCompanyProfile,
    NormalizedCorporateAction,
    NormalizedDividend,
    NormalizedIncomeStatement,
    NormalizedMarketSnapshot,
    NormalizedNews,
)
from app.utils.hashing import generate_content_hash


class Importer(Protocol):
    """Protocol implemented by database importers."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        """Import normalized records."""


def _decimal_to_float(value: Decimal | None) -> float | None:
    """Convert a Decimal fixture value for existing Numeric columns."""
    return float(value) if value is not None else None


def _should_preserve_existing(existing_is_development: bool | None, incoming_is_development: bool) -> bool:
    """Return whether an existing verified/non-development row should win."""
    return bool(incoming_is_development and existing_is_development is False)


class CompanyImporter:
    """Upsert company records by ticker."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        companies = [cast(NormalizedCompany, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            existing = {
                ticker.upper()
                for ticker in db.scalars(select(Company.ticker).where(Company.ticker.in_([row.ticker for row in companies]))).all()
            }
            return ImportResult(
                inserted=len([row for row in companies if row.ticker not in existing]),
                updated=len([row for row in companies if row.ticker in existing]),
            )

        inserted = updated = skipped = 0
        try:
            for row in companies:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                values = {
                    "name": row.name,
                    "legal_name": row.legal_name,
                    "ticker": row.ticker,
                    "exchange": Exchange(row.exchange),
                    "sector": row.sector,
                    "industry": row.industry,
                    "country": row.country,
                    "headquarters": row.headquarters,
                    "website": row.website,
                    "description": row.description,
                    "founded_year": row.founded_year,
                    "employee_count": row.employee_count,
                    "market": row.market,
                    "currency": Currency(row.currency) if row.currency else None,
                    "status": AssetStatus(row.status),
                    "logo_url": row.logo_url,
                }
                if company is None:
                    db.add(Company(**values))
                    inserted += 1
                    continue
                changed = False
                for field, value in values.items():
                    current = getattr(company, field)
                    if value not in (None, "", []) and current != value:
                        setattr(company, field, value)
                        changed = True
                if changed:
                    updated += 1
                else:
                    skipped += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped)


class IncomeStatementImporter:
    """Upsert income statements by company/year/period."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        statements = [cast(NormalizedIncomeStatement, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(statements))

        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in statements:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                statement = db.scalar(
                    select(IncomeStatement).where(
                        IncomeStatement.company_id == company.id,
                        IncomeStatement.fiscal_year == row.fiscal_year,
                        IncomeStatement.period == StatementPeriod(row.period),
                    )
                )
                if statement and _should_preserve_existing(statement.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {
                    "company_id": company.id,
                    "fiscal_year": row.fiscal_year,
                    "period": StatementPeriod(row.period),
                    "currency": row.currency,
                    "source_name": row.source.source_name,
                    "source_url": row.source.source_url,
                    "is_development_data": row.source.is_development_data,
                    "revenue": _decimal_to_float(row.revenue),
                    "cost_of_sales": _decimal_to_float(row.cost_of_sales),
                    "gross_profit": _decimal_to_float(row.gross_profit),
                    "operating_profit": _decimal_to_float(row.operating_profit),
                    "profit_before_tax": _decimal_to_float(row.profit_before_tax),
                    "net_profit": _decimal_to_float(row.net_profit),
                    "interest_expense": _decimal_to_float(row.interest_expense),
                }
                if statement is None:
                    db.add(IncomeStatement(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(statement, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class DividendImporter:
    """Upsert dividend records by company/asset/year/type/date."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        dividends = [cast(NormalizedDividend, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(dividends))

        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in dividends:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                asset = db.scalar(select(Asset).where(func.upper(Asset.ticker) == row.ticker))
                dividend = db.scalar(
                    select(Dividend).where(
                        Dividend.company_id == company.id,
                        Dividend.asset_id == (asset.id if asset else None),
                        Dividend.fiscal_year == row.fiscal_year,
                        Dividend.dividend_type == DividendType(row.dividend_type),
                        Dividend.announcement_date == row.announcement_date,
                    )
                )
                if dividend and _should_preserve_existing(dividend.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {
                    "company_id": company.id,
                    "asset_id": asset.id if asset else None,
                    "announcement_date": row.announcement_date,
                    "record_date": row.record_date,
                    "ex_dividend_date": row.ex_dividend_date,
                    "payment_date": row.payment_date,
                    "fiscal_year": row.fiscal_year,
                    "dividend_type": DividendType(row.dividend_type),
                    "dividend_per_share": _decimal_to_float(row.dividend_per_share),
                    "currency": row.currency,
                    "shares_outstanding": _decimal_to_float(row.shares_outstanding),
                    "total_dividend_amount": _decimal_to_float(row.total_dividend_amount),
                    "source_name": row.source.source_name,
                    "source_type": row.source.source_type.value,
                    "source_url": row.source.source_url,
                    "imported_at": row.source.imported_at,
                    "verified_at": row.source.verified_at,
                    "is_development_data": row.source.is_development_data,
                }
                if dividend is None:
                    db.add(Dividend(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(dividend, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class NewsImporter:
    """Upsert news articles by canonical content hash."""

    def import_records(
        self,
        db: Session,
        records: list[BaseNormalizedRecord],
        mode: IngestionMode = IngestionMode.DRY_RUN,
    ) -> ImportResult:
        articles = [cast(NormalizedNews, record) for record in records]
        hashes = [generate_content_hash(row.title, row.summary, row.content) for row in articles]
        if mode == IngestionMode.DRY_RUN:
            existing = set(db.scalars(select(News.content_hash).where(News.content_hash.in_(hashes))).all())
            return ImportResult(
                inserted=len([content_hash for content_hash in hashes if content_hash not in existing]),
                updated=len([content_hash for content_hash in hashes if content_hash in existing]),
            )

        inserted = updated = 0
        try:
            for row, content_hash in zip(articles, hashes, strict=True):
                article = db.scalar(select(News).where(News.content_hash == content_hash))
                values = {
                    "title": row.title,
                    "summary": row.summary,
                    "content": row.content,
                    "content_hash": content_hash,
                    "source": row.source_name,
                    "published_at": row.published_at,
                    "url": row.url,
                    "language": row.language,
                }
                if article is None:
                    article = News(**values)
                    db.add(article)
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(article, field, value)
                    updated += 1
                companies = _companies_for_tickers(db, row.related_tickers)
                article.companies = companies
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated)


def _companies_for_tickers(db: Session, tickers: Iterable[str]) -> list[Company]:
    """Resolve related company records from tickers."""
    normalized = [ticker.upper() for ticker in tickers]
    if not normalized:
        return []
    return list(db.scalars(select(Company).where(Company.ticker.in_(normalized))).all())





class AssetImporter:
    """Upsert assets by ticker while resolving the parent company."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        assets = [cast(NormalizedAsset, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            existing = {ticker.upper() for ticker in db.scalars(select(Asset.ticker).where(Asset.ticker.in_([row.ticker for row in assets]))).all()}
            return ImportResult(inserted=len([row for row in assets if row.ticker not in existing]), updated=len([row for row in assets if row.ticker in existing]))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in assets:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.company_ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.company_ticker}")
                    continue
                asset = db.scalar(select(Asset).where(func.upper(Asset.ticker) == row.ticker))
                values = {
                    "ticker": row.ticker,
                    "company_name": row.company_name or company.name,
                    "exchange": Exchange(row.exchange),
                    "sector": row.sector,
                    "industry": row.industry,
                    "asset_type": AssetType(row.asset_type),
                    "currency": Currency(row.currency),
                    "description": row.description,
                    "market_cap": _decimal_to_float(row.market_cap),
                    "listing_date": row.listing_date,
                    "status": AssetStatus(row.status),
                    "company_id": company.id,
                }
                if asset is None:
                    db.add(Asset(**values))
                    inserted += 1
                else:
                    changed = False
                    for field, value in values.items():
                        if value not in (None, "", []) and getattr(asset, field) != value:
                            setattr(asset, field, value)
                            changed = True
                    updated += 1 if changed else 0
                    skipped += 0 if changed else 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class CompanyProfileImporter:
    """Upsert one company profile per company."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        profiles = [cast(NormalizedCompanyProfile, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(profiles))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in profiles:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                profile = db.scalar(select(CompanyProfile).where(CompanyProfile.company_id == company.id))
                incoming_status = ResearchStatus.VERIFIED if not row.source.is_development_data else ResearchStatus.DEVELOPMENT
                if profile and profile.research_status == ResearchStatus.VERIFIED and incoming_status != ResearchStatus.VERIFIED:
                    skipped += 1
                    continue
                values = {
                    "company_id": company.id,
                    "business_summary": row.business_summary,
                    "primary_business": row.primary_business,
                    "products_services": row.products_services or None,
                    "industry": row.industry,
                    "headquarters": row.headquarters,
                    "founded_year": row.founded_year,
                    "website": row.website,
                    "country": row.country,
                    "employees": row.employees,
                    "research_status": incoming_status,
                    "last_verified": row.source.verified_at,
                    "source_name": row.source.source_name,
                    "source_url": row.source.source_url,
                }
                if profile is None:
                    db.add(CompanyProfile(**values))
                    inserted += 1
                else:
                    changed = False
                    for field, value in values.items():
                        if field == "company_id":
                            continue
                        if value not in (None, "", []) and getattr(profile, field) != value:
                            setattr(profile, field, value)
                            changed = True
                    updated += 1 if changed else 0
                    skipped += 0 if changed else 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class BalanceSheetImporter:
    """Upsert balance sheets by company/year/period."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        rows = [cast(NormalizedBalanceSheet, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(rows))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in rows:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                existing = db.scalar(select(BalanceSheet).where(BalanceSheet.company_id == company.id, BalanceSheet.fiscal_year == row.fiscal_year, BalanceSheet.period == StatementPeriod(row.period)))
                if existing and _should_preserve_existing(existing.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {"company_id": company.id, "fiscal_year": row.fiscal_year, "period": StatementPeriod(row.period), "currency": row.currency, "source_name": row.source.source_name, "source_url": row.source.source_url, "is_development_data": row.source.is_development_data, "total_assets": _decimal_to_float(row.total_assets), "current_assets": _decimal_to_float(row.current_assets), "inventory": _decimal_to_float(row.inventory), "cash_and_equivalents": _decimal_to_float(row.cash_and_equivalents), "total_liabilities": _decimal_to_float(row.total_liabilities), "current_liabilities": _decimal_to_float(row.current_liabilities), "total_debt": _decimal_to_float(row.total_debt), "total_equity": _decimal_to_float(row.total_equity)}
                if existing is None:
                    db.add(BalanceSheet(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class CashFlowStatementImporter:
    """Upsert cash flow statements by company/year/period."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        rows = [cast(NormalizedCashFlowStatement, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(rows))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in rows:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                existing = db.scalar(select(CashFlowStatement).where(CashFlowStatement.company_id == company.id, CashFlowStatement.fiscal_year == row.fiscal_year, CashFlowStatement.period == StatementPeriod(row.period)))
                if existing and _should_preserve_existing(existing.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {"company_id": company.id, "fiscal_year": row.fiscal_year, "period": StatementPeriod(row.period), "currency": row.currency, "source_name": row.source.source_name, "source_url": row.source.source_url, "is_development_data": row.source.is_development_data, "operating_cash_flow": _decimal_to_float(row.operating_cash_flow), "investing_cash_flow": _decimal_to_float(row.investing_cash_flow), "financing_cash_flow": _decimal_to_float(row.financing_cash_flow), "net_cash_flow": _decimal_to_float(row.net_cash_flow), "capital_expenditure": _decimal_to_float(row.capital_expenditure), "free_cash_flow": _decimal_to_float(row.free_cash_flow)}
                if existing is None:
                    db.add(CashFlowStatement(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class CorporateActionImporter:
    """Upsert corporate actions by company/action/date."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        actions = [cast(NormalizedCorporateAction, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(actions))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in actions:
                company = db.scalar(select(Company).where(func.upper(Company.ticker) == row.ticker))
                if company is None:
                    skipped += 1
                    warnings.append(f"Company not found for ticker {row.ticker}")
                    continue
                asset_ticker = row.asset_ticker or row.ticker
                asset = db.scalar(select(Asset).where(func.upper(Asset.ticker) == asset_ticker))
                action_type = CorporateActionType(row.action_type)
                existing = db.scalar(select(CorporateAction).where(CorporateAction.company_id == company.id, CorporateAction.asset_id == (asset.id if asset else None), CorporateAction.action_type == action_type, CorporateAction.announcement_date == row.announcement_date))
                if existing and _should_preserve_existing(existing.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {"company_id": company.id, "asset_id": asset.id if asset else None, "action_type": action_type, "announcement_date": row.announcement_date, "effective_date": row.effective_date, "title": row.title, "description": row.description, "source_name": row.source.source_name, "source_type": row.source.source_type.value, "source_url": row.source.source_url, "imported_at": row.source.imported_at, "verified_at": row.source.verified_at, "is_development_data": row.source.is_development_data}
                if existing is None:
                    db.add(CorporateAction(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)


class MarketSnapshotImporter:
    """Upsert market snapshots by asset/date/source."""

    def import_records(self, db: Session, records: list[BaseNormalizedRecord], mode: IngestionMode = IngestionMode.DRY_RUN) -> ImportResult:
        snapshots = [cast(NormalizedMarketSnapshot, record) for record in records]
        if mode == IngestionMode.DRY_RUN:
            return ImportResult(inserted=len(snapshots))
        inserted = updated = skipped = 0
        warnings: list[str] = []
        try:
            for row in snapshots:
                asset = db.scalar(select(Asset).where(func.upper(Asset.ticker) == row.ticker))
                if asset is None:
                    skipped += 1
                    warnings.append(f"Asset not found for ticker {row.ticker}")
                    continue
                existing = db.scalar(select(MarketSnapshot).where(MarketSnapshot.asset_id == asset.id, MarketSnapshot.snapshot_date == row.snapshot_date, MarketSnapshot.source_type == row.source.source_type.value))
                if existing and _should_preserve_existing(existing.is_development_data, row.source.is_development_data):
                    skipped += 1
                    continue
                values = {"asset_id": asset.id, "exchange": row.exchange, "snapshot_date": row.snapshot_date, "price": _decimal_to_float(row.price), "open_price": _decimal_to_float(row.open_price), "high_price": _decimal_to_float(row.high_price), "low_price": _decimal_to_float(row.low_price), "close_price": _decimal_to_float(row.close_price), "volume": _decimal_to_float(row.volume), "market_cap": _decimal_to_float(row.market_cap), "currency": row.currency, "source_name": row.source.source_name, "source_type": row.source.source_type.value, "source_url": row.source.source_url, "imported_at": row.source.imported_at, "verified_at": row.source.verified_at, "is_development_data": row.source.is_development_data}
                if existing is None:
                    db.add(MarketSnapshot(**values))
                    inserted += 1
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    updated += 1
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return ImportResult(errors=[str(exc)])
        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, warnings=warnings)




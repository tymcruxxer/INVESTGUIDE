"""Record normalizers for development fixture imports."""

from __future__ import annotations

from typing import Any, Protocol

from app.services.ingestion.normalizers.helpers import (
    clean_string,
    normalize_asset_type,
    normalize_corporate_action_type,
    normalize_currency,
    normalize_dividend_type,
    normalize_exchange,
    normalize_name,
    normalize_statement_period,
    normalize_status,
    normalize_ticker,
    normalize_url,
    parse_date,
    parse_datetime,
    parse_decimal,
    parse_int,
    parse_string_list,
)
from app.services.ingestion.types import (
    BaseNormalizedRecord,
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
    SourceMetadata,
    build_external_key,
)


class Normalizer(Protocol):
    """Protocol implemented by ingestion normalizers."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[BaseNormalizedRecord]:
        """Return normalized records."""


class CompanyNormalizer:
    """Normalize company records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedCompany]:
        normalized: list[NormalizedCompany] = []
        for record in records:
            ticker = normalize_ticker(record.get("ticker"))
            exchange = normalize_exchange(record.get("exchange"))
            name = normalize_name(record.get("name") or record.get("company_name"))
            normalized.append(
                NormalizedCompany(
                    external_key=build_external_key("company", ticker, exchange),
                    source=source,
                    ticker=ticker or "",
                    name=name or "",
                    legal_name=normalize_name(record.get("legal_name")),
                    exchange=exchange or "",
                    sector=clean_string(record.get("sector")),
                    industry=clean_string(record.get("industry")),
                    country=clean_string(record.get("country")),
                    headquarters=clean_string(record.get("headquarters")),
                    website=normalize_url(record.get("website")),
                    description=clean_string(record.get("description")),
                    founded_year=parse_int(record.get("founded_year")),
                    employee_count=parse_int(record.get("employee_count")),
                    market=clean_string(record.get("market")),
                    currency=normalize_currency(record.get("currency")),
                    status=(clean_string(record.get("status")) or "active").lower(),
                    logo_url=normalize_url(record.get("logo_url")),
                )
            )
        return normalized


class IncomeStatementNormalizer:
    """Normalize income statement records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedIncomeStatement]:
        normalized: list[NormalizedIncomeStatement] = []
        for record in records:
            ticker = normalize_ticker(record.get("ticker"))
            fiscal_year = parse_int(record.get("fiscal_year")) or 0
            period = normalize_statement_period(record.get("period"))
            normalized.append(
                NormalizedIncomeStatement(
                    external_key=build_external_key("income_statement", ticker, fiscal_year, period),
                    source=source,
                    ticker=ticker or "",
                    fiscal_year=fiscal_year,
                    period=period,
                    currency=normalize_currency(record.get("currency")),
                    revenue=parse_decimal(record.get("revenue")),
                    cost_of_sales=parse_decimal(record.get("cost_of_sales")),
                    gross_profit=parse_decimal(record.get("gross_profit")),
                    operating_profit=parse_decimal(record.get("operating_profit")),
                    profit_before_tax=parse_decimal(record.get("profit_before_tax")),
                    net_profit=parse_decimal(record.get("net_profit")),
                    interest_expense=parse_decimal(record.get("interest_expense")),
                )
            )
        return normalized


class DividendNormalizer:
    """Normalize dividend records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedDividend]:
        normalized: list[NormalizedDividend] = []
        for record in records:
            ticker = normalize_ticker(record.get("ticker"))
            fiscal_year = parse_int(record.get("fiscal_year"))
            dividend_type = normalize_dividend_type(record.get("dividend_type"))
            announcement_date = parse_date(record.get("announcement_date"))
            normalized.append(
                NormalizedDividend(
                    external_key=build_external_key("dividend", ticker, fiscal_year, dividend_type, announcement_date),
                    source=source,
                    ticker=ticker or "",
                    fiscal_year=fiscal_year,
                    dividend_type=dividend_type,
                    announcement_date=announcement_date,
                    record_date=parse_date(record.get("record_date")),
                    ex_dividend_date=parse_date(record.get("ex_dividend_date")),
                    payment_date=parse_date(record.get("payment_date")),
                    dividend_per_share=parse_decimal(record.get("dividend_per_share")),
                    currency=normalize_currency(record.get("currency")),
                    shares_outstanding=parse_decimal(record.get("shares_outstanding")),
                    total_dividend_amount=parse_decimal(record.get("total_dividend_amount")),
                )
            )
        return normalized


class NewsNormalizer:
    """Normalize news article records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedNews]:
        normalized: list[NormalizedNews] = []
        for record in records:
            title = clean_string(record.get("title")) or ""
            published_at = parse_datetime(record.get("published_at")) or source.imported_at
            related = record.get("related_tickers") or record.get("tickers") or []
            related_tickers = [ticker for ticker in (normalize_ticker(item) for item in related) if ticker]
            normalized.append(
                NormalizedNews(
                    external_key=build_external_key("news", record.get("url"), title, published_at.date()),
                    source=source,
                    title=title,
                    source_name=clean_string(record.get("source") or source.source_name) or source.source_name,
                    published_at=published_at,
                    summary=clean_string(record.get("summary")),
                    content=clean_string(record.get("content")),
                    url=normalize_url(record.get("url")),
                    language=clean_string(record.get("language")) or "en",
                    related_tickers=related_tickers,
                )
            )
        return normalized



class AssetNormalizer:
    """Normalize listed asset records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedAsset]:
        normalized: list[NormalizedAsset] = []
        for record in records:
            ticker = normalize_ticker(record.get("ticker"))
            company_ticker = normalize_ticker(record.get("company_ticker") or record.get("ticker"))
            exchange = normalize_exchange(record.get("exchange"))
            normalized.append(
                NormalizedAsset(
                    external_key=build_external_key(source.source_type.value, exchange, ticker),
                    source=source,
                    ticker=ticker or "",
                    company_ticker=company_ticker or "",
                    company_name=clean_string(record.get("company_name")) or clean_string(record.get("name")) or "",
                    exchange=exchange or "",
                    sector=clean_string(record.get("sector")),
                    industry=clean_string(record.get("industry")),
                    asset_type=normalize_asset_type(record.get("asset_type")),
                    currency=normalize_currency(record.get("currency")) or "ZWG",
                    description=clean_string(record.get("description")),
                    listing_date=parse_date(record.get("listing_date")),
                    market_cap=parse_decimal(record.get("market_cap")),
                    status=normalize_status(record.get("status")),
                )
            )
        return normalized


class CompanyProfileNormalizer:
    """Normalize company enrichment profiles."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedCompanyProfile]:
        normalized: list[NormalizedCompanyProfile] = []
        for record in records:
            ticker = normalize_ticker(record.get("company_ticker") or record.get("ticker"))
            normalized.append(
                NormalizedCompanyProfile(
                    external_key=build_external_key(source.source_type.value, ticker, "company_profile"),
                    source=source,
                    ticker=ticker or "",
                    business_summary=clean_string(record.get("business_summary")),
                    primary_business=clean_string(record.get("primary_business")),
                    products_services=parse_string_list(record.get("products_services") or record.get("products_and_services")),
                    industry=clean_string(record.get("industry")),
                    country=clean_string(record.get("country")),
                    headquarters=clean_string(record.get("headquarters")),
                    website=normalize_url(record.get("website")),
                    founded_year=parse_int(record.get("founded_year")),
                    employees=parse_int(record.get("employees") or record.get("employee_count")),
                    research_status=(clean_string(record.get("research_status")) or "development").lower(),
                )
            )
        return normalized


class BalanceSheetNormalizer:
    """Normalize balance sheet records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedBalanceSheet]:
        normalized: list[NormalizedBalanceSheet] = []
        for record in records:
            ticker = normalize_ticker(record.get("company_ticker") or record.get("ticker"))
            fiscal_year = parse_int(record.get("fiscal_year")) or 0
            period = normalize_statement_period(record.get("period"))
            normalized.append(
                NormalizedBalanceSheet(
                    external_key=build_external_key(source.source_type.value, ticker, fiscal_year, period, "balance_sheet"),
                    source=source,
                    ticker=ticker or "",
                    fiscal_year=fiscal_year,
                    period=period,
                    currency=normalize_currency(record.get("currency")),
                    total_assets=parse_decimal(record.get("total_assets")),
                    current_assets=parse_decimal(record.get("current_assets")),
                    inventory=parse_decimal(record.get("inventory")),
                    cash_and_equivalents=parse_decimal(record.get("cash_and_equivalents")),
                    total_liabilities=parse_decimal(record.get("total_liabilities")),
                    current_liabilities=parse_decimal(record.get("current_liabilities")),
                    total_debt=parse_decimal(record.get("total_debt")),
                    total_equity=parse_decimal(record.get("total_equity")),
                )
            )
        return normalized


class CashFlowStatementNormalizer:
    """Normalize cash flow statement records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedCashFlowStatement]:
        normalized: list[NormalizedCashFlowStatement] = []
        for record in records:
            ticker = normalize_ticker(record.get("company_ticker") or record.get("ticker"))
            fiscal_year = parse_int(record.get("fiscal_year")) or 0
            period = normalize_statement_period(record.get("period"))
            capital_expenditure = parse_decimal(record.get("capital_expenditure"))
            free_cash_flow = parse_decimal(record.get("free_cash_flow"))
            normalized.append(
                NormalizedCashFlowStatement(
                    external_key=build_external_key(source.source_type.value, ticker, fiscal_year, period, "cash_flow"),
                    source=source,
                    ticker=ticker or "",
                    fiscal_year=fiscal_year,
                    period=period,
                    currency=normalize_currency(record.get("currency")),
                    operating_cash_flow=parse_decimal(record.get("operating_cash_flow")),
                    investing_cash_flow=parse_decimal(record.get("investing_cash_flow")),
                    financing_cash_flow=parse_decimal(record.get("financing_cash_flow")),
                    net_cash_flow=parse_decimal(record.get("net_cash_flow")),
                    capital_expenditure=capital_expenditure,
                    free_cash_flow=free_cash_flow,
                )
            )
        return normalized


class CorporateActionNormalizer:
    """Normalize corporate action records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedCorporateAction]:
        normalized: list[NormalizedCorporateAction] = []
        for record in records:
            ticker = normalize_ticker(record.get("company_ticker") or record.get("ticker"))
            action_type = normalize_corporate_action_type(record.get("action_type"))
            announcement_date = parse_date(record.get("announcement_date"))
            normalized.append(
                NormalizedCorporateAction(
                    external_key=build_external_key(source.source_type.value, ticker, action_type, announcement_date),
                    source=source,
                    ticker=ticker or "",
                    asset_ticker=normalize_ticker(record.get("asset_ticker")),
                    action_type=action_type,
                    title=clean_string(record.get("title")),
                    announcement_date=announcement_date,
                    effective_date=parse_date(record.get("effective_date")),
                    record_date=parse_date(record.get("record_date")),
                    currency=normalize_currency(record.get("currency")),
                    amount=parse_decimal(record.get("amount")),
                    ratio=clean_string(record.get("ratio")),
                    description=clean_string(record.get("description")),
                )
            )
        return normalized


class MarketSnapshotNormalizer:
    """Normalize market snapshot records."""

    def normalize(self, records: list[dict[str, Any]], source: SourceMetadata) -> list[NormalizedMarketSnapshot]:
        normalized: list[NormalizedMarketSnapshot] = []
        for record in records:
            ticker = normalize_ticker(record.get("asset_ticker") or record.get("ticker"))
            exchange = normalize_exchange(record.get("exchange"))
            snapshot_date = parse_date(record.get("snapshot_date"))
            normalized.append(
                NormalizedMarketSnapshot(
                    external_key=build_external_key(source.source_type.value, exchange, ticker, snapshot_date),
                    source=source,
                    ticker=ticker or "",
                    exchange=exchange or "",
                    snapshot_date=snapshot_date or source.imported_at.date(),
                    price=parse_decimal(record.get("price")),
                    open_price=parse_decimal(record.get("open_price")),
                    high_price=parse_decimal(record.get("high_price")),
                    low_price=parse_decimal(record.get("low_price")),
                    close_price=parse_decimal(record.get("close_price")),
                    volume=parse_decimal(record.get("volume")),
                    market_cap=parse_decimal(record.get("market_cap")),
                    currency=normalize_currency(record.get("currency")),
                )
            )
        return normalized


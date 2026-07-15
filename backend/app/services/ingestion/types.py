"""Shared contracts for verified data ingestion."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any


class SourceType(StrEnum):
    """Supported source families for future verified data."""

    ZSE = "ZSE"
    VFEX = "VFEX"
    COMPANY_FILING = "COMPANY_FILING"
    ANNUAL_REPORT = "ANNUAL_REPORT"
    CORPORATE_ANNOUNCEMENT = "CORPORATE_ANNOUNCEMENT"
    CSV_IMPORT = "CSV_IMPORT"
    JSON_IMPORT = "JSON_IMPORT"
    MANUAL_CURATED_IMPORT = "MANUAL_CURATED_IMPORT"
    DEVELOPMENT_FIXTURE = "DEVELOPMENT_FIXTURE"


class VerificationStatus(StrEnum):
    """Lifecycle states for imported records."""

    UNVERIFIED = "Unverified"
    VALIDATED = "Validated"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
    DEVELOPMENT = "Development"


class IngestionMode(StrEnum):
    """Supported import execution modes."""

    DRY_RUN = "dry_run"
    LENIENT = "lenient"
    STRICT = "strict"



class IssueSeverity(StrEnum):
    """Stable ingestion issue severities."""

    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    REJECTED = "Rejected"


class IssueCode(StrEnum):
    """Stable deterministic ingestion issue codes for grouping and exports."""

    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_TICKER = "INVALID_TICKER"
    INVALID_EXCHANGE = "INVALID_EXCHANGE"
    INVALID_CURRENCY = "INVALID_CURRENCY"
    INVALID_DATE = "INVALID_DATE"
    INVALID_DECIMAL = "INVALID_DECIMAL"
    UNKNOWN_COMPANY = "UNKNOWN_COMPANY"
    UNKNOWN_ASSET = "UNKNOWN_ASSET"
    DUPLICATE_EXTERNAL_KEY = "DUPLICATE_EXTERNAL_KEY"
    LOWER_PRECEDENCE_SKIPPED = "LOWER_PRECEDENCE_SKIPPED"
    DEVELOPMENT_DATA_BLOCKED = "DEVELOPMENT_DATA_BLOCKED"
    BALANCE_SHEET_IMBALANCE = "BALANCE_SHEET_IMBALANCE"
    CASH_FLOW_MISMATCH = "CASH_FLOW_MISMATCH"
    DIVIDEND_DATE_WARNING = "DIVIDEND_DATE_WARNING"
    INVALID_PRICE_RANGE = "INVALID_PRICE_RANGE"
    MISSING_SOURCE_METADATA = "MISSING_SOURCE_METADATA"
    VERIFICATION_METADATA_MISSING = "VERIFICATION_METADATA_MISSING"
    STRICT_BATCH_ABORTED = "STRICT_BATCH_ABORTED"
    DATABASE_WRITE_FAILED = "DATABASE_WRITE_FAILED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    IMPORT_WARNING = "IMPORT_WARNING"
    IMPORT_ERROR = "IMPORT_ERROR"

class EntityType(StrEnum):
    """Normalized entity names accepted by the pipeline registry."""

    COMPANIES = "companies"
    ASSETS = "assets"
    COMPANY_PROFILES = "company_profiles"
    INCOME_STATEMENTS = "income_statements"
    BALANCE_SHEETS = "balance_sheets"
    CASH_FLOW_STATEMENTS = "cash_flow_statements"
    DIVIDENDS = "dividends"
    CORPORATE_ACTIONS = "corporate_actions"
    NEWS = "news"
    MARKET_SNAPSHOTS = "market_snapshots"


@dataclass(frozen=True)
class SourceMetadata:
    """Source metadata attached to every ingestion run and normalized record."""

    source_name: str
    source_type: SourceType
    source_url: str | None = None
    source_document_date: date | None = None
    imported_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    dataset_version: str | None = None
    checksum: str | None = None
    record_count: int = 0
    is_development_data: bool = False


@dataclass(frozen=True)
class LoadedDataset:
    """Raw source records plus their resolved metadata."""

    records: list[dict[str, Any]]
    metadata: SourceMetadata


@dataclass(frozen=True)
class ValidationIssue:
    """Field-level validation issue."""

    record_index: int
    field: str
    message: str
    severity: str = "error"
    code: IssueCode = IssueCode.VALIDATION_ERROR
    raw_value_summary: str | None = None


@dataclass(frozen=True)
class RejectedRecord:
    """Rejected normalized record with validation issues."""

    record: "BaseNormalizedRecord"
    issues: list[ValidationIssue]


@dataclass(frozen=True)
class ValidationResult:
    """Validator output with valid, warning, and rejected records."""

    valid_records: list["BaseNormalizedRecord"]
    warnings: list[ValidationIssue] = field(default_factory=list)
    rejected_records: list[RejectedRecord] = field(default_factory=list)

    @property
    def rejected_count(self) -> int:
        """Return the number of rejected records."""
        return len(self.rejected_records)


@dataclass(frozen=True)
class ImportResult:
    """Importer summary."""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    rejected: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineResult:
    """End-to-end ingestion pipeline summary."""

    entity: EntityType
    mode: IngestionMode
    source: SourceMetadata
    total_records: int
    valid_records: int
    rejected_records: int
    import_result: ImportResult
    run_id: int | None = None


@dataclass(frozen=True)
class BaseNormalizedRecord:
    """Base normalized record shared by all entity contracts."""

    external_key: str
    source: SourceMetadata


@dataclass(frozen=True)
class NormalizedCompany(BaseNormalizedRecord):
    """Normalized company record."""

    ticker: str
    name: str
    exchange: str
    legal_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    headquarters: str | None = None
    website: str | None = None
    description: str | None = None
    founded_year: int | None = None
    employee_count: int | None = None
    market: str | None = None
    currency: str | None = None
    status: str = "active"
    logo_url: str | None = None


@dataclass(frozen=True)
class NormalizedAsset(BaseNormalizedRecord):
    """Normalized listed asset record."""

    ticker: str
    company_ticker: str
    company_name: str
    exchange: str
    asset_type: str
    currency: str
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    listing_date: date | None = None
    market_cap: Decimal | None = None
    status: str = "active"


@dataclass(frozen=True)
class NormalizedCompanyProfile(BaseNormalizedRecord):
    """Normalized company profile record."""

    ticker: str
    business_summary: str | None = None
    primary_business: str | None = None
    products_services: list[str] = field(default_factory=list)
    industry: str | None = None
    country: str | None = None
    headquarters: str | None = None
    website: str | None = None
    founded_year: int | None = None
    employees: int | None = None
    research_status: str = "development"


@dataclass(frozen=True)
class NormalizedIncomeStatement(BaseNormalizedRecord):
    """Normalized income statement period."""

    ticker: str
    fiscal_year: int
    period: str
    currency: str | None = None
    revenue: Decimal | None = None
    cost_of_sales: Decimal | None = None
    gross_profit: Decimal | None = None
    operating_profit: Decimal | None = None
    profit_before_tax: Decimal | None = None
    net_profit: Decimal | None = None
    interest_expense: Decimal | None = None


@dataclass(frozen=True)
class NormalizedBalanceSheet(BaseNormalizedRecord):
    """Normalized balance sheet period."""

    ticker: str
    fiscal_year: int
    period: str
    currency: str | None = None
    total_assets: Decimal | None = None
    current_assets: Decimal | None = None
    inventory: Decimal | None = None
    cash_and_equivalents: Decimal | None = None
    total_liabilities: Decimal | None = None
    current_liabilities: Decimal | None = None
    total_debt: Decimal | None = None
    total_equity: Decimal | None = None


@dataclass(frozen=True)
class NormalizedCashFlowStatement(BaseNormalizedRecord):
    """Normalized cash flow statement period."""

    ticker: str
    fiscal_year: int
    period: str
    currency: str | None = None
    operating_cash_flow: Decimal | None = None
    investing_cash_flow: Decimal | None = None
    financing_cash_flow: Decimal | None = None
    net_cash_flow: Decimal | None = None
    capital_expenditure: Decimal | None = None
    free_cash_flow: Decimal | None = None


@dataclass(frozen=True)
class NormalizedDividend(BaseNormalizedRecord):
    """Normalized dividend record."""

    ticker: str
    fiscal_year: int | None
    dividend_type: str
    announcement_date: date | None = None
    record_date: date | None = None
    ex_dividend_date: date | None = None
    payment_date: date | None = None
    dividend_per_share: Decimal | None = None
    currency: str | None = None
    shares_outstanding: Decimal | None = None
    total_dividend_amount: Decimal | None = None


@dataclass(frozen=True)
class NormalizedCorporateAction(BaseNormalizedRecord):
    """Normalized corporate action record."""

    ticker: str
    asset_ticker: str | None
    action_type: str
    title: str | None = None
    announcement_date: date | None = None
    effective_date: date | None = None
    record_date: date | None = None
    currency: str | None = None
    amount: Decimal | None = None
    ratio: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class NormalizedNews(BaseNormalizedRecord):
    """Normalized news article record."""

    title: str
    source_name: str
    published_at: datetime
    summary: str | None = None
    content: str | None = None
    url: str | None = None
    language: str = "en"
    related_tickers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizedMarketSnapshot(BaseNormalizedRecord):
    """Normalized market snapshot record for future imports."""

    ticker: str
    exchange: str
    snapshot_date: date
    price: Decimal | None = None
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    close_price: Decimal | None = None
    volume: Decimal | None = None
    market_cap: Decimal | None = None
    currency: str | None = None


def build_external_key(*parts: object) -> str:
    """Build a deterministic external key from normalized parts."""
    normalized = "|".join(str(part).strip().upper() for part in parts if part not in (None, ""))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()




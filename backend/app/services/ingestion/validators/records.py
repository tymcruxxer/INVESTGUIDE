"""Validation rules for normalized ingestion records."""

from __future__ import annotations

from collections import Counter
from typing import Protocol

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
    RejectedRecord,
    ValidationIssue,
    ValidationResult,
    VerificationStatus,
)

SUPPORTED_EXCHANGES = {"ZSE", "VFEX"}
SUPPORTED_CURRENCIES = {"ZWG", "USD", None}
SUPPORTED_COMPANY_STATUSES = {"active", "suspended", "delisted"}
SUPPORTED_PERIODS = {"annual", "interim"}


class Validator(Protocol):
    """Protocol implemented by ingestion validators."""

    def validate(self, records: list[BaseNormalizedRecord]) -> ValidationResult:
        """Validate normalized records."""


class BaseValidator:
    """Shared validation helpers."""

    def validate(self, records: list[BaseNormalizedRecord]) -> ValidationResult:
        """Validate records using subclass rules."""
        key_counts = Counter(record.external_key for record in records)
        valid: list[BaseNormalizedRecord] = []
        warnings: list[ValidationIssue] = []
        rejected: list[RejectedRecord] = []

        for index, record in enumerate(records):
            issues = self.validate_record(record, index)
            if key_counts[record.external_key] > 1:
                issues.append(ValidationIssue(index, "external_key", "Duplicate external key in source batch."))
            if record.source.is_development_data and record.source.verification_status != VerificationStatus.DEVELOPMENT:
                issues.append(
                    ValidationIssue(index, "verification_status", "Development data must use Development status.")
                )
            if record.source.verification_status == VerificationStatus.VERIFIED and record.source.verified_at is None:
                issues.append(ValidationIssue(index, "verified_at", "Verified records require verified_at."))
            errors = [issue for issue in issues if issue.severity == "error"]
            warnings.extend(issue for issue in issues if issue.severity != "error")
            if errors:
                rejected.append(RejectedRecord(record=record, issues=issues))
            else:
                valid.append(record)
        return ValidationResult(valid_records=valid, warnings=warnings, rejected_records=rejected)

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        """Validate one record."""
        return []


class CompanyValidator(BaseValidator):
    """Validate company records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        company = record
        assert isinstance(company, NormalizedCompany)
        issues: list[ValidationIssue] = []
        if not company.ticker:
            issues.append(ValidationIssue(index, "ticker", "Ticker is required."))
        if not company.name:
            issues.append(ValidationIssue(index, "name", "Company name is required."))
        if company.exchange not in SUPPORTED_EXCHANGES:
            issues.append(ValidationIssue(index, "exchange", "Exchange must be ZSE or VFEX."))
        if company.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        if company.status not in SUPPORTED_COMPANY_STATUSES:
            issues.append(ValidationIssue(index, "status", "Status must be active, suspended, or delisted."))
        return issues


class IncomeStatementValidator(BaseValidator):
    """Validate income statement records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        statement = record
        assert isinstance(statement, NormalizedIncomeStatement)
        issues: list[ValidationIssue] = []
        if not statement.ticker:
            issues.append(ValidationIssue(index, "ticker", "Ticker is required."))
        if statement.fiscal_year < 1900:
            issues.append(ValidationIssue(index, "fiscal_year", "Fiscal year is required."))
        if statement.period not in SUPPORTED_PERIODS:
            issues.append(ValidationIssue(index, "period", "Period must be annual or interim."))
        if statement.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        if statement.revenue is None and statement.net_profit is None:
            issues.append(
                ValidationIssue(index, "values", "At least revenue or net_profit should be supplied.", "warning")
            )
        return issues


class DividendValidator(BaseValidator):
    """Validate dividend records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        dividend = record
        assert isinstance(dividend, NormalizedDividend)
        issues: list[ValidationIssue] = []
        if not dividend.ticker:
            issues.append(ValidationIssue(index, "ticker", "Ticker is required."))
        if dividend.fiscal_year is None and dividend.announcement_date is None:
            issues.append(ValidationIssue(index, "date", "Fiscal year or announcement date is required."))
        if dividend.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        if dividend.dividend_per_share is None and dividend.total_dividend_amount is None:
            issues.append(
                ValidationIssue(index, "amount", "Dividend per share or total amount should be supplied.", "warning")
            )
        return issues


class NewsValidator(BaseValidator):
    """Validate news records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        news = record
        assert isinstance(news, NormalizedNews)
        issues: list[ValidationIssue] = []
        if not news.title:
            issues.append(ValidationIssue(index, "title", "Title is required."))
        if not news.source_name:
            issues.append(ValidationIssue(index, "source", "Source is required."))
        if news.url is None:
            issues.append(ValidationIssue(index, "url", "URL is missing; duplicate detection will rely on content.", "warning"))
        return issues



def _negative_issue(value: object, index: int, field: str) -> ValidationIssue | None:
    if value is not None and value < 0:
        return ValidationIssue(index, field, "Value cannot be negative.")
    return None


class AssetValidator(BaseValidator):
    """Validate asset records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        asset = record
        assert isinstance(asset, NormalizedAsset)
        issues: list[ValidationIssue] = []
        if not asset.ticker:
            issues.append(ValidationIssue(index, "ticker", "Ticker is required."))
        if not asset.company_ticker:
            issues.append(ValidationIssue(index, "company_ticker", "Company ticker is required."))
        if asset.exchange not in SUPPORTED_EXCHANGES:
            issues.append(ValidationIssue(index, "exchange", "Exchange must be ZSE or VFEX."))
        if asset.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        if asset.status not in SUPPORTED_COMPANY_STATUSES:
            issues.append(ValidationIssue(index, "status", "Status must be active, suspended, or delisted."))
        if asset.market_cap is not None and asset.market_cap < 0:
            issues.append(ValidationIssue(index, "market_cap", "Market cap cannot be negative."))
        return issues


class CompanyProfileValidator(BaseValidator):
    """Validate company profile records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        profile = record
        assert isinstance(profile, NormalizedCompanyProfile)
        issues: list[ValidationIssue] = []
        if not profile.ticker:
            issues.append(ValidationIssue(index, "company_ticker", "Company ticker is required."))
        if not any([profile.business_summary, profile.primary_business, profile.products_services]):
            issues.append(ValidationIssue(index, "profile", "At least one profile field should be supplied.", "warning"))
        if profile.research_status not in {"development", "verified", "needs_review", "unavailable"}:
            issues.append(ValidationIssue(index, "research_status", "Unsupported research status."))
        return issues


class BalanceSheetValidator(BaseValidator):
    """Validate balance sheet records."""

    tolerance = 1

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        sheet = record
        assert isinstance(sheet, NormalizedBalanceSheet)
        issues: list[ValidationIssue] = []
        if not sheet.ticker:
            issues.append(ValidationIssue(index, "company_ticker", "Company ticker is required."))
        if sheet.fiscal_year < 1900:
            issues.append(ValidationIssue(index, "fiscal_year", "Fiscal year is required."))
        if sheet.period not in SUPPORTED_PERIODS:
            issues.append(ValidationIssue(index, "period", "Period must be annual or interim."))
        if sheet.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        for field in ("total_assets", "current_assets", "inventory", "cash_and_equivalents", "total_liabilities", "current_liabilities", "total_debt", "total_equity"):
            issue = _negative_issue(getattr(sheet, field), index, field)
            if issue:
                issues.append(issue)
        if sheet.total_assets is not None and sheet.total_liabilities is not None and sheet.total_equity is not None:
            difference = abs(sheet.total_assets - (sheet.total_liabilities + sheet.total_equity))
            if difference > self.tolerance:
                issues.append(ValidationIssue(index, "balance", "Assets do not approximately equal liabilities plus equity.", "warning"))
        return issues


class CashFlowStatementValidator(BaseValidator):
    """Validate cash flow statement records."""

    tolerance = 1

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        cash_flow = record
        assert isinstance(cash_flow, NormalizedCashFlowStatement)
        issues: list[ValidationIssue] = []
        if not cash_flow.ticker:
            issues.append(ValidationIssue(index, "company_ticker", "Company ticker is required."))
        if cash_flow.fiscal_year < 1900:
            issues.append(ValidationIssue(index, "fiscal_year", "Fiscal year is required."))
        if cash_flow.period not in SUPPORTED_PERIODS:
            issues.append(ValidationIssue(index, "period", "Period must be annual or interim."))
        if cash_flow.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        if all(value is not None for value in (cash_flow.operating_cash_flow, cash_flow.investing_cash_flow, cash_flow.financing_cash_flow, cash_flow.net_cash_flow)):
            difference = abs(cash_flow.operating_cash_flow + cash_flow.investing_cash_flow + cash_flow.financing_cash_flow - cash_flow.net_cash_flow)
            if difference > self.tolerance:
                issues.append(ValidationIssue(index, "net_cash_flow", "Cash flow components do not approximately equal net cash flow.", "warning"))
        return issues


class CorporateActionValidator(BaseValidator):
    """Validate corporate action records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        action = record
        assert isinstance(action, NormalizedCorporateAction)
        issues: list[ValidationIssue] = []
        if not action.ticker:
            issues.append(ValidationIssue(index, "company_ticker", "Company ticker is required."))
        if not action.action_type:
            issues.append(ValidationIssue(index, "action_type", "Action type is required."))
        if action.announcement_date is None:
            issues.append(ValidationIssue(index, "announcement_date", "Announcement date is required."))
        if action.effective_date and action.announcement_date and action.effective_date < action.announcement_date:
            issues.append(ValidationIssue(index, "effective_date", "Effective date cannot precede announcement date."))
        return issues


class MarketSnapshotValidator(BaseValidator):
    """Validate market snapshot records."""

    def validate_record(self, record: BaseNormalizedRecord, index: int) -> list[ValidationIssue]:
        snapshot = record
        assert isinstance(snapshot, NormalizedMarketSnapshot)
        issues: list[ValidationIssue] = []
        if not snapshot.ticker:
            issues.append(ValidationIssue(index, "asset_ticker", "Asset ticker is required."))
        if snapshot.exchange not in SUPPORTED_EXCHANGES:
            issues.append(ValidationIssue(index, "exchange", "Exchange must be ZSE or VFEX."))
        if snapshot.currency not in SUPPORTED_CURRENCIES:
            issues.append(ValidationIssue(index, "currency", "Currency must be ZWG or USD."))
        for field in ("price", "open_price", "high_price", "low_price", "close_price", "volume", "market_cap"):
            issue = _negative_issue(getattr(snapshot, field), index, field)
            if issue:
                issues.append(issue)
        if snapshot.high_price is not None and snapshot.low_price is not None and snapshot.high_price < snapshot.low_price:
            issues.append(ValidationIssue(index, "high_price", "High price cannot be below low price."))
        if snapshot.high_price is not None and snapshot.low_price is not None:
            for field in ("open_price", "close_price", "price"):
                value = getattr(snapshot, field)
                if value is not None and not (snapshot.low_price <= value <= snapshot.high_price):
                    issues.append(ValidationIssue(index, field, "Price is outside the high/low range.", "warning"))
        return issues

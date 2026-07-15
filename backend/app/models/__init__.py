"""SQLAlchemy model registry.

Import model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.associations import asset_news, company_news
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.dividend import CorporateAction, CorporateActionType, Dividend, DividendType
from app.models.financial_statement import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    StatementPeriod,
)
from app.models.ingestion import IngestionRecordIssue, IngestionRun
from app.models.market_snapshot import MarketSnapshot
from app.models.investor_profile import (
    ExperienceLevel,
    InvestorProfile,
    PreferredLanguageLevel,
    RiskAppetite,
)
from app.models.mixins import TimestampMixin
from app.models.news import News
from app.models.user import User

__all__ = [
    "Asset",
    "AssetStatus",
    "AssetType",
    "Currency",
    "Exchange",
    "Company",
    "CompanyProfile",
    "ResearchStatus",
    "BalanceSheet",
    "CashFlowStatement",
    "IncomeStatement",
    "StatementPeriod",
    "ExperienceLevel",
    "InvestorProfile",
    "IngestionRun",
    "IngestionRecordIssue",
    "MarketSnapshot",
    "PreferredLanguageLevel",
    "RiskAppetite",
    "News",
    "TimestampMixin",
    "User",
    "asset_news",
    "company_news",
]







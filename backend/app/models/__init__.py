"""SQLAlchemy model registry.

Import model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.asset import Asset, AssetStatus, AssetType, Currency, Exchange
from app.models.associations import asset_news, company_news
from app.models.audit import AuditLog
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.connector_registry import (
    Connector,
    ConnectorAuthStrategy,
    ConnectorCapability,
    ConnectorCapabilityName,
    ConnectorConfigurationSchema,
    ConnectorKind,
    ConnectorLifecycle,
    ConnectorValidation,
    ConnectorValidationStatus,
    ConnectorVersion,
)
from app.models.dividend import CorporateAction, CorporateActionType, Dividend, DividendType
from app.models.financial_statement import (
    BalanceSheet,
    CashFlowStatement,
    IncomeStatement,
    StatementPeriod,
)
from app.models.ingestion import IngestionRecordIssue, IngestionRun
from app.models.ingestion_operations import (
    ExecutionFailure,
    ExecutionMetric,
    FreshnessStatus,
    IngestionExecution,
    IngestionExecutionMode,
    IngestionExecutionStatus,
    IngestionFailureCategory,
    IngestionJob,
    IngestionJobStatus,
    IngestionJobType,
    IngestionPriority,
    IngestionTriggerType,
)
from app.models.investor_profile import (
    ExperienceLevel,
    InvestorProfile,
    PreferredLanguageLevel,
    RiskAppetite,
)
from app.models.macro import MacroIndicator, MacroIndicatorType
from app.models.market_snapshot import MarketSnapshot
from app.models.mixins import TimestampMixin
from app.models.news import News
from app.models.runtime_registry import (
    RuntimeCapability,
    RuntimeCapabilityName,
    RuntimeCompatibility,
    RuntimeCompatibilityStatus,
    RuntimeDefinition,
    RuntimeExecutionState,
    RuntimeResultStatus,
    RuntimeStatus,
    RuntimeValidation,
    RuntimeValidationStatus,
    RuntimeVersion,
)
from app.models.rbac import Permission, PrivilegeChangeHistory, Role, RolePermission, UserRole, UserRoleHistory
from app.models.sector import Industry, Sector
from app.models.sensitive_action import SensitiveActionRequest, SensitiveActionStatus
from app.models.source_registry import (
    AuthenticationType,
    ConnectorType,
    RefreshPolicy,
    Source,
    SourceCapability,
    SourceCategory,
    SourceConfiguration,
    SourceCredential,
    SourceStatus,
    SourceTier,
    SourceVersion,
)
from app.models.user import User

__all__ = [
    "Asset",
    "AssetStatus",
    "AssetType",
    "AuditLog",
    "BalanceSheet",
    "CashFlowStatement",
    "Company",
    "CompanyProfile",
    "Connector",
    "ConnectorAuthStrategy",
    "ConnectorCapability",
    "ConnectorCapabilityName",
    "ConnectorConfigurationSchema",
    "ConnectorKind",
    "ConnectorLifecycle",
    "ConnectorValidation",
    "ConnectorValidationStatus",
    "ConnectorVersion",
    "CorporateAction",
    "CorporateActionType",
    "Currency",
    "Dividend",
    "DividendType",
    "Exchange",
    "ExecutionFailure",
    "ExecutionMetric",
    "ExperienceLevel",
    "IncomeStatement",
    "Industry",
    "IngestionRecordIssue",
    "IngestionRun",
    "FreshnessStatus",
    "IngestionExecution",
    "IngestionExecutionMode",
    "IngestionExecutionStatus",
    "IngestionFailureCategory",
    "IngestionJob",
    "IngestionJobStatus",
    "IngestionJobType",
    "IngestionPriority",
    "IngestionTriggerType",
    "InvestorProfile",
    "MacroIndicator",
    "MacroIndicatorType",
    "MarketSnapshot",
    "News",
    "Permission",
    "PrivilegeChangeHistory",
    "PreferredLanguageLevel",
    "ResearchStatus",
    "RiskAppetite",
    "Role",
    "RuntimeCapability",`r`n    "RuntimeCapabilityName",`r`n    "RuntimeCompatibility",`r`n    "RuntimeCompatibilityStatus",`r`n    "RuntimeDefinition",`r`n    "RuntimeExecutionState",`r`n    "RuntimeResultStatus",`r`n    "RuntimeStatus",`r`n    "RuntimeValidation",`r`n    "RuntimeValidationStatus",`r`n    "RuntimeVersion",`r`n    "RolePermission",
    "Sector",
    "SensitiveActionRequest",
    "SensitiveActionStatus",
    "AuthenticationType",
    "ConnectorType",
    "RefreshPolicy",
    "Source",
    "SourceCapability",
    "SourceCategory",
    "SourceConfiguration",
    "SourceCredential",
    "SourceStatus",
    "SourceTier",
    "SourceVersion",
    "StatementPeriod",
    "TimestampMixin",
    "User",
    "UserRole",
    "UserRoleHistory",
    "asset_news",
    "company_news",
]









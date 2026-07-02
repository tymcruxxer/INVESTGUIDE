"""InvestGuide analytics engine foundation."""

from app.analytics.base import AnalyticsMetadata, BaseAnalytics
from app.analytics.confidence import ConfidenceScoreAnalytics
from app.analytics.context import AnalyticsContext
from app.analytics.dividend import DividendScoreAnalytics
from app.analytics.engine import AnalyticsEngine
from app.analytics.exceptions import (
    AnalyticsError,
    CalculationError,
    MissingDataError,
    UnknownMetricError,
    ValidationError,
)
from app.analytics.explanation import AnalyticsExplanation
from app.analytics.growth import GrowthScoreAnalytics
from app.analytics.liquidity import LiquidityScoreAnalytics
from app.analytics.macro import MacroScoreAnalytics
from app.analytics.quality import QualityScoreAnalytics
from app.analytics.registry import AnalyticsRegistry
from app.analytics.result import AnalyticsResult
from app.analytics.risk import RiskScoreAnalytics
from app.analytics.scores import DEFAULT_ANALYTICS
from app.analytics.valuation import ValueScoreAnalytics
from app.analytics.version import ENGINE_VERSION, METHODOLOGY_VERSION

__all__ = [
    "AnalyticsContext",
    "AnalyticsEngine",
    "AnalyticsError",
    "AnalyticsExplanation",
    "AnalyticsMetadata",
    "AnalyticsRegistry",
    "AnalyticsResult",
    "BaseAnalytics",
    "CalculationError",
    "ConfidenceScoreAnalytics",
    "DEFAULT_ANALYTICS",
    "DividendScoreAnalytics",
    "ENGINE_VERSION",
    "GrowthScoreAnalytics",
    "LiquidityScoreAnalytics",
    "METHODOLOGY_VERSION",
    "MacroScoreAnalytics",
    "MissingDataError",
    "QualityScoreAnalytics",
    "RiskScoreAnalytics",
    "UnknownMetricError",
    "ValidationError",
    "ValueScoreAnalytics",
]
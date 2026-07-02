"""Score module exports and default registry list."""

from __future__ import annotations

from app.analytics.confidence import ConfidenceScoreAnalytics
from app.analytics.dividend import DividendScoreAnalytics
from app.analytics.growth import GrowthScoreAnalytics
from app.analytics.liquidity import LiquidityScoreAnalytics
from app.analytics.macro import MacroScoreAnalytics
from app.analytics.quality import QualityScoreAnalytics
from app.analytics.risk import RiskScoreAnalytics
from app.analytics.valuation import ValueScoreAnalytics

DEFAULT_ANALYTICS = (
    QualityScoreAnalytics,
    GrowthScoreAnalytics,
    DividendScoreAnalytics,
    ValueScoreAnalytics,
    LiquidityScoreAnalytics,
    RiskScoreAnalytics,
    MacroScoreAnalytics,
    ConfidenceScoreAnalytics,
)

__all__ = [
    "ConfidenceScoreAnalytics",
    "DEFAULT_ANALYTICS",
    "DividendScoreAnalytics",
    "GrowthScoreAnalytics",
    "LiquidityScoreAnalytics",
    "MacroScoreAnalytics",
    "QualityScoreAnalytics",
    "RiskScoreAnalytics",
    "ValueScoreAnalytics",
]
"""Analytics foundation tests."""

from __future__ import annotations

import pytest

from app.analytics import (
    ENGINE_VERSION,
    METHODOLOGY_VERSION,
    AnalyticsContext,
    AnalyticsEngine,
    AnalyticsExplanation,
    AnalyticsRegistry,
    AnalyticsResult,
    ConfidenceScoreAnalytics,
    DividendScoreAnalytics,
    GrowthScoreAnalytics,
    LiquidityScoreAnalytics,
    MacroScoreAnalytics,
    QualityScoreAnalytics,
    RiskScoreAnalytics,
    ValidationError,
    ValueScoreAnalytics,
)
from app.analytics.exceptions import CalculationError, MissingDataError, UnknownMetricError


def test_registry_registers_and_calculates_metrics() -> None:
    registry = AnalyticsRegistry()
    registry.register("quality_score", QualityScoreAnalytics)

    result = registry.calculate("quality_score", AnalyticsContext(asset={"ticker": "Delta"}))

    assert result.metric_name == "quality_score"
    assert result.value is None
    assert result.version == ENGINE_VERSION
    assert "asset" in result.inputs_used


def test_registry_unregisters_metrics() -> None:
    registry = AnalyticsRegistry()
    registry.register("quality_score", QualityScoreAnalytics)
    registry.unregister("quality_score")

    with pytest.raises(UnknownMetricError):
        registry.calculate("quality_score", AnalyticsContext(asset={"ticker": "Delta"}))


def test_context_tracks_optional_inputs() -> None:
    context = AnalyticsContext(asset={"ticker": "Delta"}, historical_prices=[{"date": "2024-01-01"}])

    assert context.asset_identifier() == "Delta"
    assert context.available_inputs() == ["asset", "historical_prices"]
    assert context.has_required_data(["asset"]) is True
    assert context.has_required_data(["news"]) is False
    assert context.missing_inputs(["asset", "news"]) == ["news"]


def test_engine_executes_registered_modules_and_collects_warnings() -> None:
    engine = AnalyticsEngine(auto_register=False)
    engine.registry.register("quality_score", QualityScoreAnalytics)
    engine.registry.register("risk_score", RiskScoreAnalytics)

    payload = engine.analyze(AnalyticsContext(asset={"ticker": "Delta"}))

    assert payload["engine_version"] == ENGINE_VERSION
    assert payload["methodology_version"] == METHODOLOGY_VERSION
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["completed"] == 2
    assert payload["results"][0]["metric_name"] in {"quality_score", "risk_score"}
    assert payload["warnings"]


def test_engine_auto_registers_default_metrics() -> None:
    engine = AnalyticsEngine()
    metadata = engine.metadata()

    assert "quality_score" in metadata["registered_metrics"]
    assert "confidence_score" in metadata["registered_metrics"]
    assert len(metadata["metrics"]) >= 8


def test_result_object_exposes_standard_fields() -> None:
    result = AnalyticsResult(
        metric_name="growth_score",
        value=None,
        confidence=0.0,
        methodology="Planned methodology",
        inputs_used=("asset", "historical_prices"),
        warnings=("Pending implementation",),
        version="0.1.0",
    )

    data = result.to_dict()

    expected = {"metric_name", "value", "confidence", "methodology", "inputs_used", "warnings", "timestamp", "version"}
    assert expected.issubset(data.keys())


def test_result_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        AnalyticsResult(metric_name="risk_score", confidence=1.5)


def test_explanation_layer_formats_plain_text() -> None:
    explanation = AnalyticsExplanation(
        metric_name="dividend_score",
        summary="Architecture placeholder",
        details=("Dividend history is stable.", "Payout ratio is healthy."),
        confidence_label="Medium",
        missing_inputs=("last_annual_report",),
    )

    text = explanation.to_text()

    assert "dividend_score" in text
    assert "Dividend history is stable." in text
    assert "last_annual_report" in text


def test_exceptions_are_specific() -> None:
    with pytest.raises(ValidationError):
        raise ValidationError("context is invalid")

    with pytest.raises(MissingDataError):
        raise MissingDataError("asset is required")

    with pytest.raises(CalculationError):
        raise CalculationError("calculation not implemented")

    with pytest.raises(UnknownMetricError):
        raise UnknownMetricError("unknown metric")


def test_versioning_is_exposed_on_engine_and_modules() -> None:
    assert AnalyticsEngine.ENGINE_VERSION == ENGINE_VERSION
    assert AnalyticsEngine.METHODOLOGY_VERSION == METHODOLOGY_VERSION

    metric_classes = [
        QualityScoreAnalytics,
        GrowthScoreAnalytics,
        DividendScoreAnalytics,
        ValueScoreAnalytics,
        LiquidityScoreAnalytics,
        RiskScoreAnalytics,
        MacroScoreAnalytics,
        ConfidenceScoreAnalytics,
    ]

    for metric_class in metric_classes:
        instance = metric_class()
        assert instance.version == ENGINE_VERSION
        assert instance.methodology_version == METHODOLOGY_VERSION
        assert instance.metadata().purpose
        assert instance.planned_inputs()
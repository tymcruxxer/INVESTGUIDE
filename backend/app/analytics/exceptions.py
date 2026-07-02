"""Analytics package exceptions."""


class AnalyticsError(Exception):
    """Base class for analytics package errors."""


class ValidationError(AnalyticsError):
    """Raised when an analytics context or input is invalid."""


class MissingDataError(AnalyticsError):
    """Raised when required data is missing for a metric."""


class CalculationError(AnalyticsError):
    """Raised when a metric calculation cannot be completed."""


class UnknownMetricError(AnalyticsError):
    """Raised when a metric is not registered."""
"""Retry policy primitives for scraper infrastructure."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError

RetrySleep = Callable[[float], None]


@dataclass(frozen=True)
class RetryDecision:
    """Result of evaluating whether an operation should retry."""

    should_retry: bool
    delay: float
    reason: str | None = None


@dataclass(frozen=True)
class RetryPolicy:
    """Exponential-backoff retry policy."""

    max_retries: int = 3
    backoff_factor: float = 0.5
    retryable_status_codes: set[int] = field(default_factory=lambda: {408, 429, 500, 502, 503, 504})
    retryable_exceptions: tuple[type[BaseException], ...] = (TimeoutError, URLError, ConnectionError)

    def delay_for_attempt(self, attempt: int) -> float:
        """Return exponential delay for a one-based retry attempt."""
        if attempt <= 0:
            return 0.0
        return self.backoff_factor * (2 ** (attempt - 1))

    def evaluate_status(self, status_code: int, attempt: int) -> RetryDecision:
        """Return whether a response status should be retried."""
        should_retry = status_code in self.retryable_status_codes and attempt < self.max_retries
        return RetryDecision(
            should_retry=should_retry,
            delay=self.delay_for_attempt(attempt + 1) if should_retry else 0.0,
            reason=f"status:{status_code}" if should_retry else None,
        )

    def evaluate_exception(self, exc: BaseException, attempt: int) -> RetryDecision:
        """Return whether an exception should be retried."""
        status_code = exc.code if isinstance(exc, HTTPError) else None
        if status_code is not None:
            return self.evaluate_status(status_code, attempt)
        should_retry = isinstance(exc, self.retryable_exceptions) and attempt < self.max_retries
        return RetryDecision(
            should_retry=should_retry,
            delay=self.delay_for_attempt(attempt + 1) if should_retry else 0.0,
            reason=exc.__class__.__name__ if should_retry else None,
        )

    def run(self, operation: Callable[[], object], sleep: RetrySleep | None = None) -> object:
        """Run an operation with retry behavior."""
        sleeper = sleep or (lambda _delay: None)
        attempt = 0
        while True:
            try:
                result = operation()
            except BaseException as exc:
                decision = self.evaluate_exception(exc, attempt)
                if not decision.should_retry:
                    raise
                sleeper(decision.delay)
                attempt += 1
                continue
            status_code = getattr(result, "status_code", None)
            if isinstance(status_code, int):
                decision = self.evaluate_status(status_code, attempt)
                if decision.should_retry:
                    sleeper(decision.delay)
                    attempt += 1
                    continue
            return result
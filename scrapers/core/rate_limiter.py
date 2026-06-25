"""Rate limiting primitives for scraper requests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import time

Clock = Callable[[], float]
Sleeper = Callable[[float], None]


@dataclass
class RateLimiter:
    """Synchronous rate limiter with interval, RPM, cooldown, and burst protection."""

    minimum_interval: float = 2.0
    requests_per_minute: int = 30
    burst_limit: int = 1
    clock: Clock = time.monotonic
    sleep: Sleeper = time.sleep
    _last_request_at: float | None = None
    _window_started_at: float | None = None
    _request_count: int = 0
    _cooldown_until: float | None = None

    def __post_init__(self) -> None:
        if self.burst_limit <= 0:
            raise ValueError("burst_limit must be positive")
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        if self._window_started_at is None:
            self._window_started_at = self.clock()

    def _wait(self, seconds: float) -> None:
        if seconds > 0:
            self.sleep(seconds)

    def acquire(self) -> None:
        """Block until a request may be made."""
        now = self.clock()
        if self._cooldown_until is not None and now < self._cooldown_until:
            self._wait(self._cooldown_until - now)
            now = self.clock()

        window_started_at = self._window_started_at if self._window_started_at is not None else now
        if now - window_started_at >= 60:
            self._window_started_at = now
            self._request_count = 0
            window_started_at = now

        if self._request_count >= self.requests_per_minute:
            wait_for = 60 - (now - window_started_at)
            self._wait(wait_for)
            now = self.clock()
            self._window_started_at = now
            self._request_count = 0

        if self._last_request_at is not None:
            elapsed = now - self._last_request_at
            self._wait(self.minimum_interval - elapsed)
            now = self.clock()

        self._last_request_at = now
        self._request_count += 1

    def cooldown(self, seconds: float) -> None:
        """Set a cooldown before the next request."""
        self._cooldown_until = self.clock() + max(seconds, 0.0)
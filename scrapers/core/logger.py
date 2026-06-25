"""Structured logging helpers for scraper infrastructure."""

from __future__ import annotations

import logging


class ScraperLogger:
    """Small wrapper around Python logging for scraper lifecycle events."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("investguide.scrapers")

    def scraper_started(self, source_name: str) -> None:
        """Log scraper startup."""
        self.logger.info("scraper started", extra={"source_name": source_name})

    def scraper_completed(self, source_name: str, execution_time: float, article_count: int = 0) -> None:
        """Log scraper completion."""
        self.logger.info(
            "scraper completed",
            extra={"source_name": source_name, "execution_time": execution_time, "article_count": article_count},
        )

    def scraper_failed(self, source_name: str, execution_time: float, error: str) -> None:
        """Log scraper failure without secrets."""
        self.logger.error(
            "scraper failed",
            extra={"source_name": source_name, "execution_time": execution_time, "error": self._sanitize(error)},
        )

    def retry_attempt(self, source_name: str, attempt: int, delay: float) -> None:
        """Log retry attempts."""
        self.logger.warning(
            "scraper retry",
            extra={"source_name": source_name, "attempt": attempt, "delay": delay},
        )

    @staticmethod
    def _sanitize(value: str) -> str:
        """Avoid accidental secret disclosure from common key-value fragments."""
        redacted = value
        for marker in ("password=", "token=", "api_key=", "secret="):
            lower = redacted.lower()
            index = lower.find(marker)
            if index >= 0:
                end = redacted.find(" ", index)
                if end < 0:
                    end = len(redacted)
                redacted = redacted[: index + len(marker)] + "[REDACTED]" + redacted[end:]
        return redacted
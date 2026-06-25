"""Source-specific scraper configuration."""

from __future__ import annotations

from dataclasses import dataclass, replace
from os import environ
from typing import Mapping

from scrapers.core.user_agent import DEFAULT_USER_AGENT


@dataclass(frozen=True)
class SourceConfig:
    """Runtime configuration for a scraper source."""

    timeout: float = 10.0
    retry_count: int = 3
    retry_backoff: float = 0.5
    rate_limit: int = 30
    request_interval: float = 2.0
    user_agent: str = DEFAULT_USER_AGENT
    enabled: bool = True

    @classmethod
    def from_env(cls, source_id: str, env: Mapping[str, str] | None = None) -> "SourceConfig":
        """Load config from defaults and source-specific environment variables."""
        values = env or environ
        prefix = f"SCRAPER_{source_id.upper().replace('-', '_').replace(' ', '_')}_"
        default_prefix = "SCRAPER_DEFAULT_"
        config = cls()

        def get_value(name: str) -> str | None:
            return values.get(f"{prefix}{name}") or values.get(f"{default_prefix}{name}")

        updates: dict[str, object] = {}
        parsers = {
            "TIMEOUT": ("timeout", float),
            "RETRY_COUNT": ("retry_count", int),
            "RETRY_BACKOFF": ("retry_backoff", float),
            "RATE_LIMIT": ("rate_limit", int),
            "REQUEST_INTERVAL": ("request_interval", float),
            "USER_AGENT": ("user_agent", str),
        }
        for env_name, (field_name, parser) in parsers.items():
            raw = get_value(env_name)
            if raw is not None:
                updates[field_name] = parser(raw)

        enabled = get_value("ENABLED")
        if enabled is not None:
            updates["enabled"] = enabled.strip().lower() in {"1", "true", "yes", "on"}

        return replace(config, **updates)
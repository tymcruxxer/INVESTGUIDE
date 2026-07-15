"""Environment guard for development fixture data."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings


DEVELOPMENT_DATA_DISABLED_MESSAGE = (
    "Development seed aborted: fixture data is disabled in this environment."
)


@dataclass(frozen=True)
class DevelopmentDataPolicy:
    """Resolved policy for development fixture usage."""

    environment: str
    allow_development_data: bool

    @property
    def permits_fixtures(self) -> bool:
        """Return whether fixture inserts/reads are allowed."""
        return self.environment.lower() == "development" and self.allow_development_data


def get_development_data_policy(settings: Settings | None = None) -> DevelopmentDataPolicy:
    """Return the current development-data policy."""
    resolved = settings or get_settings()
    return DevelopmentDataPolicy(
        environment=resolved.environment,
        allow_development_data=resolved.allow_development_data,
    )


def ensure_development_data_allowed(settings: Settings | None = None) -> DevelopmentDataPolicy:
    """Raise when development fixtures are disabled for the current environment."""
    policy = get_development_data_policy(settings)
    if not policy.permits_fixtures:
        raise RuntimeError(DEVELOPMENT_DATA_DISABLED_MESSAGE)
    return policy

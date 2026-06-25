"""User agent profiles for future scraper requests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

DEFAULT_USER_AGENT = "InvestGuideBot/0.1 (+https://investguide.app)"


class UserAgentProfile(StrEnum):
    """Supported user-agent profiles."""

    BOT = "bot"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    API = "api"


@dataclass(frozen=True)
class UserAgentManager:
    """Resolve user-agent strings by named profile."""

    default_user_agent: str = DEFAULT_USER_AGENT

    def get(self, profile: UserAgentProfile | str = UserAgentProfile.BOT) -> str:
        """Return the configured user-agent string for a profile."""
        profile_value = UserAgentProfile(profile)
        profiles = {
            UserAgentProfile.BOT: self.default_user_agent,
            UserAgentProfile.DESKTOP: (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
            UserAgentProfile.MOBILE: (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            ),
            UserAgentProfile.API: "InvestGuideAPIClient/0.1",
        }
        return profiles[profile_value]

    def with_custom_default(self, user_agent: str) -> "UserAgentManager":
        """Return a manager with a custom bot user-agent."""
        return UserAgentManager(default_user_agent=user_agent)
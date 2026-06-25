"""Robots policy metadata for scraper sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin


@dataclass(frozen=True)
class RobotsRule:
    """Stored robots.txt metadata for a source."""

    source_id: str
    robots_url: str
    homepage: str


@dataclass
class RobotsPolicy:
    """Robots policy placeholder for future permission checks."""

    rules: dict[str, RobotsRule] = field(default_factory=dict)

    @staticmethod
    def robots_url_for_homepage(homepage: str) -> str:
        """Return the conventional robots.txt URL for a homepage."""
        return urljoin(homepage.rstrip("/") + "/", "robots.txt")

    def register(self, source_id: str, homepage: str, robots_url: str | None = None) -> RobotsRule:
        """Store robots metadata without downloading robots.txt."""
        rule = RobotsRule(
            source_id=source_id,
            homepage=homepage,
            robots_url=robots_url or self.robots_url_for_homepage(homepage),
        )
        self.rules[source_id] = rule
        return rule

    def get(self, source_id: str) -> RobotsRule | None:
        """Return stored robots metadata for a source."""
        return self.rules.get(source_id)

    def can_fetch(self, source_id: str, _url: str, _user_agent: str) -> bool | None:
        """Placeholder permission hook; parsing is intentionally deferred."""
        if source_id not in self.rules:
            return None
        return None
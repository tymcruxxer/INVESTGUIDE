"""Hashing utilities for deterministic backend content identifiers."""

from __future__ import annotations

import hashlib
import re

_TITLE_PATTERN = re.compile(r"[^a-z0-9]+")


def normalize_title(title: str) -> str:
    """Normalize article titles for duplicate comparisons."""
    return _TITLE_PATTERN.sub(" ", title.lower()).strip()


def generate_content_hash(title: str, summary: str | None = None, content: str | None = None) -> str:
    """Generate the canonical SHA-256 hash for article content identity."""
    parts = [normalize_title(title), (summary or "").strip().lower(), (content or "").strip().lower()]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
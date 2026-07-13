"""Shared constants and labels for deterministic research intelligence."""

from __future__ import annotations

ENGINE_VERSION = "1.0.0"
RESEARCH_ASSESSMENT_VERSION = "1"

PROHIBITED_SIGNAL_WORDS = {"buy", "sell", "strong buy", "hold recommendation"}

EVIDENCE_LABELS = {
    "Low": "Limited",
    "Medium": "Moderate",
    "High": "Strong",
    "Very High": "Strong",
}

RESEARCH_STATUS_READY = "Deterministic research generated from structured data"
RESEARCH_STATUS_LIMITED = "Limited structured data available"

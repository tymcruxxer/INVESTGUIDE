"""Pydantic schemas for deterministic asset intelligence assessments."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssetAssessmentRead(BaseModel):
    """Structured deterministic investment assessment returned by the API."""

    ticker: str
    overall_assessment: str
    evidence_strength: str
    investment_horizon: str
    key_strengths: list[str] = Field(default_factory=list)
    things_to_watch: list[str] = Field(default_factory=list)
    educational_summary: str
    explain_like_im_18: str
    generated_at: datetime
    assessment_version: str = "1"
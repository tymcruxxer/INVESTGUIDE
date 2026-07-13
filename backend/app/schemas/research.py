"""Schemas for deterministic investment research payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ResearchScore(BaseModel):
    """Reusable scored research section."""

    label: str
    score: int = Field(ge=0, le=100)
    summary: str
    reasons: list[str]
    supporting_evidence: list[str]


class RiskResearch(BaseModel):
    """Risk-focused research section."""

    overall_risk: str
    risk_level: Literal["Low", "Moderate", "Elevated", "High"]
    risk_score: int = Field(ge=0, le=100)
    summary: str
    reasons: list[str]
    things_to_watch: list[str]
    supporting_evidence: list[str]


class EvidenceResearch(BaseModel):
    """Evidence-strength section for transparency."""

    strength: Literal["Strong", "Moderate", "Limited", "Experimental"]
    score: int = Field(ge=0, le=100)
    summary: str
    reasons: list[str]
    data_used: list[str]
    missing_data: list[str]


class EducationResearch(BaseModel):
    """Educational context for the assessment."""

    summary: str
    key_concepts: list[str]
    why_it_matters: str


class Eli18Research(BaseModel):
    """Beginner-friendly explanation."""

    summary: str
    example: str


class OverallResearch(BaseModel):
    """Overall non-prescriptive research summary."""

    label: str
    summary: str
    reasons: list[str]


class ResearchTransparency(BaseModel):
    """Metadata showing how the research was produced."""

    data_used: list[str]
    assessment_generated: datetime
    evidence_strength: str
    last_updated: datetime | None = None
    research_status: str


class ResearchAssessmentRead(BaseModel):
    """Full deterministic AI Research response."""

    ticker: str
    subject_type: Literal["asset", "company"]
    overall_assessment: OverallResearch
    opportunity: ResearchScore
    risk: RiskResearch
    evidence: EvidenceResearch
    education: EducationResearch
    eli18: Eli18Research
    suggested_questions: list[str]
    transparency: ResearchTransparency
    generated_at: datetime
    assessment_version: str
    engine_version: str

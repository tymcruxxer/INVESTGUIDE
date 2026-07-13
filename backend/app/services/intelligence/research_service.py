"""Deterministic AI Research composition service.

This service does not call LLMs or external AI providers. It converts existing
structured backend facts into an explainable research card that future AI layers
can enhance without replacing the deterministic foundation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.schemas.research import ResearchAssessmentRead
from app.services.intelligence.education_engine import EducationEngine
from app.services.intelligence.evidence_engine import EvidenceEngine
from app.services.intelligence.models import (
    ENGINE_VERSION,
    RESEARCH_ASSESSMENT_VERSION,
    RESEARCH_STATUS_LIMITED,
    RESEARCH_STATUS_READY,
)
from app.services.intelligence.opportunity_engine import OpportunityEngine
from app.services.intelligence.question_engine import QuestionEngine
from app.services.intelligence.risk_engine import RiskEngine
from app.services.intelligence.summary_engine import SummaryEngine
from app.services.intelligence.utils import asset_value, unique_ordered

_RESEARCH_CACHE: dict[str, dict[str, Any]] = {}


def clear_research_cache() -> None:
    """Clear the process-local research cache for tests or operational refreshes."""
    _RESEARCH_CACHE.clear()


def build_asset_research(asset: Any) -> dict[str, Any]:
    """Build deterministic AI Research for an asset."""
    return _build_research(subject=_asset_subject(asset), subject_type="asset")


def build_company_research(company: Any, primary_asset: Any | None = None, profile: Any | None = None) -> dict[str, Any]:
    """Build deterministic AI Research for a company using the best available facts."""
    subject = _company_subject(company, primary_asset, profile)
    return _build_research(subject=subject, subject_type="company")


def _build_research(subject: dict[str, Any], subject_type: str) -> dict[str, Any]:
    cache_key = _cache_key(subject, subject_type)
    if cache_key in _RESEARCH_CACHE:
        return _RESEARCH_CACHE[cache_key]

    generated_at = datetime.now(UTC)
    opportunity = OpportunityEngine().assess(subject)
    risk = RiskEngine().assess(subject)
    evidence = EvidenceEngine().assess(subject)
    education_engine = EducationEngine()
    education = education_engine.explain(subject, opportunity["label"], risk["risk_level"])
    eli18 = education_engine.explain_like_im_18(subject, risk["risk_level"])
    overall = SummaryEngine().summarize(opportunity, risk, evidence)
    suggested_questions = QuestionEngine().suggest(subject)

    research_status = RESEARCH_STATUS_READY if evidence["score"] >= 45 else RESEARCH_STATUS_LIMITED
    payload = {
        "ticker": str(subject.get("ticker") or "").upper(),
        "subject_type": subject_type,
        "overall_assessment": overall,
        "opportunity": opportunity,
        "risk": risk,
        "evidence": evidence,
        "education": education,
        "eli18": eli18,
        "suggested_questions": suggested_questions,
        "transparency": {
            "data_used": evidence["data_used"],
            "assessment_generated": generated_at,
            "evidence_strength": evidence["strength"],
            "last_updated": subject.get("updated_at"),
            "research_status": research_status,
        },
        "generated_at": generated_at,
        "assessment_version": RESEARCH_ASSESSMENT_VERSION,
        "engine_version": ENGINE_VERSION,
    }
    result = ResearchAssessmentRead.model_validate(payload).model_dump(mode="json")
    _RESEARCH_CACHE[cache_key] = result
    return result


def _asset_subject(asset: Any) -> dict[str, Any]:
    return {
        "id": asset_value(asset, "id"),
        "ticker": asset_value(asset, "ticker"),
        "company_name": asset_value(asset, "company_name") or asset_value(asset, "name"),
        "name": asset_value(asset, "company_name") or asset_value(asset, "name"),
        "exchange": asset_value(asset, "exchange"),
        "sector": asset_value(asset, "sector"),
        "industry": asset_value(asset, "industry"),
        "asset_type": asset_value(asset, "asset_type"),
        "currency": asset_value(asset, "currency"),
        "description": asset_value(asset, "description"),
        "market_cap": asset_value(asset, "market_cap"),
        "listing_date": asset_value(asset, "listing_date"),
        "updated_at": asset_value(asset, "updated_at"),
    }


def _company_subject(company: Any, primary_asset: Any | None, profile: Any | None) -> dict[str, Any]:
    asset_subject = _asset_subject(primary_asset) if primary_asset is not None else {}
    description_parts = [
        asset_value(company, "description"),
        asset_value(profile, "business_summary") if profile is not None else None,
        asset_value(profile, "primary_business") if profile is not None else None,
    ]
    description = " ".join(str(part) for part in description_parts if part)
    products = asset_value(profile, "products_services", []) if profile is not None else []
    if products:
        description = f"{description} Products and services: {', '.join(products)}".strip()

    return {
        "id": asset_value(company, "id"),
        "ticker": asset_value(company, "ticker") or asset_subject.get("ticker"),
        "company_name": asset_value(company, "name") or asset_subject.get("company_name"),
        "name": asset_value(company, "name") or asset_subject.get("name"),
        "exchange": asset_value(company, "exchange") or asset_subject.get("exchange"),
        "sector": asset_value(company, "sector") or asset_subject.get("sector"),
        "industry": asset_value(company, "industry") or asset_subject.get("industry"),
        "asset_type": asset_subject.get("asset_type") or "company",
        "currency": asset_value(company, "currency") or asset_subject.get("currency"),
        "description": description or asset_subject.get("description"),
        "market_cap": asset_subject.get("market_cap"),
        "listing_date": asset_subject.get("listing_date"),
        "updated_at": asset_value(profile, "updated_at") if profile is not None else asset_value(company, "updated_at"),
    }


def _cache_key(subject: dict[str, Any], subject_type: str) -> str:
    fields = [
        subject_type,
        str(subject.get("ticker") or "").upper(),
        str(subject.get("updated_at") or ""),
        str(subject.get("description") or ""),
        str(subject.get("market_cap") or ""),
        str(subject.get("listing_date") or ""),
    ]
    return "|".join(unique_ordered(fields))
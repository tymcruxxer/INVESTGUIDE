"""Deterministic investment assessment service pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.schemas.assessment import AssetAssessmentRead
from app.services.intelligence.assessment_engine import InvestmentAssessmentEngine
from app.services.intelligence.risk_engine import RiskEngine
from app.services.intelligence.strength_engine import StrengthEngine
from app.services.intelligence.utils import normalized_value

ASSESSMENT_VERSION = "1"


def _build_educational_summary(
    asset: Any,
    evidence_strength: str,
    overall_assessment: str,
    investment_horizon: str,
    key_strengths: list[str],
    things_to_watch: list[str],
) -> str:
    asset_type = normalized_value(asset, "asset_type").replace("_", " ") or "listed asset"
    exchange = normalized_value(asset, "exchange") or "its exchange"
    sector = normalized_value(asset, "sector") or normalized_value(asset, "industry") or "its sector"

    strengths_text = ", ".join(key_strengths[:3]) if key_strengths else "available structured profile data"
    watches_text = ", ".join(things_to_watch[:3]) if things_to_watch else "key market signals"

    return (
        f"{normalized_value(asset, 'ticker').upper()} is a {asset_type} listed on {exchange} in the {sector} sector. "
        f"The assessment is {overall_assessment} with {evidence_strength.lower()} evidence strength. "
        f"Key strengths include {strengths_text}. Monitor {watches_text} as new information becomes available. "
        f"This summary is based on structured asset profile data, not investment advice."
    )


def _build_explain_like_im_18(
    asset: Any,
    evidence_strength: str,
    overall_assessment: str,
    investment_horizon: str,
    key_strengths: list[str],
    things_to_watch: list[str],
) -> str:
    ticker = normalized_value(asset, "ticker").upper()
    company = normalized_value(asset, "company_name") or ticker
    asset_type = normalized_value(asset, "asset_type").replace("_", " ") or "asset"

    return (
        f"Think of {company} ({ticker}) as a {asset_type} that we are studying using structured data. "
        f"There is {evidence_strength.lower()} evidence available, so the assessment is {overall_assessment}. "
        f"It looks best for {investment_horizon.lower()} planning and shows strengths like {', '.join(key_strengths[:2])}. "
        f"Watch {', '.join(things_to_watch[:2])} because those factors can change how much confidence we have."
    )


def build_asset_assessment(asset: Any) -> dict[str, Any]:
    """Build a deterministic assessment payload for an asset."""
    strength_engine = StrengthEngine()
    risk_engine = RiskEngine()
    assessment_engine = InvestmentAssessmentEngine()

    evidence_strength = strength_engine.calculate_evidence_strength(asset)
    things_to_watch = risk_engine.things_to_watch(asset)
    key_strengths = assessment_engine.key_strengths(asset)
    overall_assessment = assessment_engine.overall_assessment(
        asset,
        evidence_strength=evidence_strength,
        watch_count=len(things_to_watch),
    )
    investment_horizon = assessment_engine.investment_horizon(asset)

    payload = {
        "ticker": normalized_value(asset, "ticker").upper(),
        "overall_assessment": overall_assessment,
        "evidence_strength": evidence_strength,
        "investment_horizon": investment_horizon,
        "key_strengths": key_strengths,
        "things_to_watch": things_to_watch,
        "educational_summary": _build_educational_summary(
            asset,
            evidence_strength,
            overall_assessment,
            investment_horizon,
            key_strengths,
            things_to_watch,
        ),
        "explain_like_im_18": _build_explain_like_im_18(
            asset,
            evidence_strength,
            overall_assessment,
            investment_horizon,
            key_strengths,
            things_to_watch,
        ),
        "generated_at": datetime.now(UTC),
        "assessment_version": ASSESSMENT_VERSION,
    }

    return AssetAssessmentRead.model_validate(payload).model_dump(mode="json")

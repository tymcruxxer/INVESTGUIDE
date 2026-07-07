"""Deterministic intelligence engine tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

from app.services.intelligence.assessment_service import build_asset_assessment


def make_asset(**overrides: object) -> SimpleNamespace:
    """Create an ORM-shaped asset object for intelligence tests."""
    now = datetime(2026, 6, 25, tzinfo=UTC)
    data = {
        "ticker": "DLTA",
        "company_name": "Delta Corporation Limited",
        "exchange": "ZSE",
        "sector": "Consumer Staples",
        "industry": "Beverages",
        "asset_type": "EQUITY",
        "currency": "ZWG",
        "description": "Zimbabwe-listed beverages company.",
        "market_cap": None,
        "listing_date": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_build_asset_assessment_returns_valid_payload() -> None:
    asset = make_asset(
        market_cap=120_000_000,
        listing_date=datetime(2020, 1, 1, tzinfo=UTC).date(),
    )

    result = build_asset_assessment(asset)

    assert result["ticker"] == "DLTA"
    assert result["assessment_version"] == "1"
    assert result["evidence_strength"] in {"Low", "Medium", "High", "Very High"}
    assert result["overall_assessment"] in {
        "Neutral",
        "Moderately Attractive",
        "Attractive",
    }
    assert isinstance(result["key_strengths"], list)
    assert isinstance(result["things_to_watch"], list)
    assert "educational_summary" in result
    assert "explain_like_im_18" in result
    assert result["generated_at"] is not None


def test_build_asset_assessment_reasonable_strength_and_watch_list() -> None:
    asset = make_asset(
        sector="Mining",
        industry="Gold Mining",
        exchange="VFEX",
        currency="USD",
        market_cap=250_000_000,
        listing_date=datetime(2018, 5, 10, tzinfo=UTC).date(),
    )

    result = build_asset_assessment(asset)

    assert result["evidence_strength"] in {"High", "Very High"}
    assert "Commodity" in " ".join(result["key_strengths"]) or "foreign" in " ".join(result["key_strengths"]).lower()
    assert any("Interest rates" in watch for watch in result["things_to_watch"]) or any(
        hint in watch for watch in result["things_to_watch"] for hint in ["Foreign-currency rules", "Commodity prices"]
    )

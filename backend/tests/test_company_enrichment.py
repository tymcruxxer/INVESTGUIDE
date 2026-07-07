"""Company enrichment service tests."""

from datetime import UTC, datetime

from app.models.asset import AssetStatus, Currency, Exchange
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.services.company_enrichment import apply_enrichment, build_company_profile_from_fixture, build_verification_payload


def make_company() -> Company:
    """Create a company object for enrichment tests."""
    return Company(
        id=1,
        name="Delta Corporation Limited",
        ticker="DLTA",
        exchange=Exchange.ZSE,
        sector="Consumer Staples",
        industry="Beverages",
        country="Zimbabwe",
        status=AssetStatus.ACTIVE,
        currency=Currency.ZWG,
    )


def test_build_company_profile_from_fixture_is_development_labeled() -> None:
    """Fixture-backed profiles carry source metadata and development status."""
    profile = build_company_profile_from_fixture(make_company())

    assert profile.primary_business is not None
    assert profile.products_services
    assert profile.research_status == ResearchStatus.DEVELOPMENT
    assert profile.source_name == "InvestGuide development fixture data"
    assert profile.source_url is not None


def test_apply_enrichment_preserves_verified_fields() -> None:
    """Verified fields are not overwritten by development fixture data."""
    existing = CompanyProfile(
        company_id=1,
        business_summary="Verified summary",
        research_status=ResearchStatus.VERIFIED,
        last_verified=datetime(2026, 1, 1, tzinfo=UTC),
        source_name="Verified source",
    )
    incoming = build_company_profile_from_fixture(make_company())

    enriched = apply_enrichment(existing, incoming)

    assert enriched.business_summary == "Verified summary"
    assert enriched.research_status == ResearchStatus.VERIFIED
    assert enriched.source_name == "Verified source"


def test_build_verification_payload_exposes_source_transparency() -> None:
    """Verification payload keeps source and research status explicit."""
    profile = build_company_profile_from_fixture(make_company())
    payload = build_verification_payload(profile)

    assert payload["research_status"] == ResearchStatus.DEVELOPMENT
    assert payload["last_verified"] == profile.last_verified
    assert payload["source_name"] == profile.source_name
"""Company enrichment service.

The enrichment layer stores structured, source-transparent facts. It does not
scrape websites, call external APIs, generate AI summaries, or fabricate
financial metrics.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.database.company_profile_seed import get_company_profile_fixture
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.services.company_profile_service import get_company_profile

PRESERVE_FIELDS = {
    "business_summary",
    "primary_business",
    "products_services",
    "industry",
    "sub_industry",
    "headquarters",
    "founded_year",
    "website",
    "email",
    "phone",
    "country",
    "exchange",
    "currency",
    "employees",
    "status",
    "research_status",
    "last_verified",
    "source_name",
    "source_url",
}


def build_company_profile_from_fixture(company: Company) -> CompanyProfile:
    """Build a non-persisted profile from development fixtures and company facts."""
    fixture = get_company_profile_fixture(company.ticker) or {}
    return CompanyProfile(
        company_id=company.id or 0,
        business_summary=fixture.get("business_summary") or company.description,
        primary_business=fixture.get("primary_business") or company.industry,
        products_services=fixture.get("products_services") or [],
        industry=fixture.get("industry") or company.sector,
        sub_industry=fixture.get("sub_industry") or company.industry,
        headquarters=fixture.get("headquarters") or company.headquarters,
        founded_year=fixture.get("founded_year") or company.founded_year,
        website=fixture.get("website") or company.website,
        email=fixture.get("email"),
        phone=fixture.get("phone"),
        country=fixture.get("country") or company.country,
        exchange=fixture.get("exchange") or company.exchange,
        currency=fixture.get("currency") or company.currency,
        employees=fixture.get("employees") or company.employee_count,
        status=fixture.get("status") or company.status,
        research_status=fixture.get("research_status") or ResearchStatus.DEVELOPMENT,
        last_verified=fixture.get("last_verified"),
        source_name=fixture.get("source_name"),
        source_url=fixture.get("source_url"),
    )


def apply_enrichment(existing: CompanyProfile, incoming: CompanyProfile) -> CompanyProfile:
    """Fill missing fields while preserving already verified profile values."""
    for field in PRESERVE_FIELDS:
        current_value = getattr(existing, field)
        incoming_value = getattr(incoming, field)
        should_fill = current_value is None or current_value == [] or current_value == ""
        if should_fill and incoming_value not in (None, [], ""):
            setattr(existing, field, incoming_value)

    if existing.research_status != ResearchStatus.VERIFIED:
        existing.last_verified = incoming.last_verified
        existing.source_name = incoming.source_name
        existing.source_url = incoming.source_url
        existing.research_status = incoming.research_status
    return existing


def upsert_company_profile_from_fixture(db: Session, company: Company) -> CompanyProfile:
    """Create or update a company profile using development fixture data only."""
    incoming = build_company_profile_from_fixture(company)
    existing = get_company_profile(db, company)
    if existing is None:
        db.add(incoming)
        db.flush()
        return incoming
    return apply_enrichment(existing, incoming)


def get_or_build_company_profile(db: Session, company: Company) -> CompanyProfile:
    """Return persisted profile, otherwise a non-persisted fixture-backed profile."""
    existing = get_company_profile(db, company)
    if existing is not None:
        return existing
    return build_company_profile_from_fixture(company)


def build_verification_payload(profile: CompanyProfile) -> dict[str, Any]:
    """Build source transparency metadata for API responses."""
    return {
        "last_verified": profile.last_verified,
        "source_name": profile.source_name,
        "source_url": profile.source_url,
        "research_status": profile.research_status,
    }
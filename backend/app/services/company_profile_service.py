"""Company profile service functions."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus


def get_company_profile(db: Session, company: Company) -> CompanyProfile | None:
    """Return the persisted profile for a company, if one exists."""
    if company.id is None:
        return None
    return db.scalar(select(CompanyProfile).where(CompanyProfile.company_id == company.id))


def build_unavailable_profile(company: Company) -> CompanyProfile:
    """Build a non-persisted transparency profile when enrichment is unavailable."""
    return CompanyProfile(
        company_id=company.id or 0,
        business_summary="Company profile enrichment is not available yet.",
        primary_business=company.industry,
        products_services=[],
        industry=company.sector,
        sub_industry=company.industry,
        headquarters=company.headquarters,
        founded_year=company.founded_year,
        website=company.website,
        country=company.country,
        exchange=company.exchange,
        currency=company.currency,
        employees=company.employee_count,
        status=company.status,
        research_status=ResearchStatus.UNAVAILABLE,
        last_verified=None,
        source_name=None,
        source_url=None,
    )
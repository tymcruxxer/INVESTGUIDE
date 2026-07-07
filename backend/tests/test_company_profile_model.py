"""Company profile model metadata tests."""

from sqlalchemy import Index, UniqueConstraint, inspect

from app.models.company_profile import CompanyProfile, ResearchStatus


def test_company_profile_model_columns_match_domain_contract() -> None:
    """CompanyProfile stores structured enrichment facts and source metadata."""
    columns = inspect(CompanyProfile).columns

    expected_columns = {
        "id",
        "company_id",
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
        "created_at",
        "updated_at",
    }

    assert set(columns.keys()) == expected_columns
    assert columns.company_id.nullable is False
    assert columns.research_status.nullable is False


def test_company_profile_constraints_and_indexes_are_registered() -> None:
    """CompanyProfile metadata supports one profile per company and research filtering."""
    table = CompanyProfile.__table__
    unique_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    index_names = {index.name for index in table.indexes if isinstance(index, Index)}

    assert "uq_company_profiles_company_id" in unique_names
    assert {
        "ix_company_profiles_company_id",
        "ix_company_profiles_research_status",
        "ix_company_profiles_last_verified",
    }.issubset(index_names)


def test_research_status_values_are_explicit() -> None:
    """Research statuses prepare future human verification workflows."""
    assert {item.value for item in ResearchStatus} == {
        "development",
        "verified",
        "needs_review",
        "unavailable",
    }
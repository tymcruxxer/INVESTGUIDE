"""Company profile schema tests."""

from app.models.company_profile import ResearchStatus
from app.schemas.company_profile import CompanyProfileRead


def test_company_profile_schema_normalizes_nullable_products_services() -> None:
    """Nullable database JSON values are serialized as stable lists."""
    profile = CompanyProfileRead.model_validate(
        {
            "business_summary": "Development fixture.",
            "products_services": None,
            "research_status": ResearchStatus.DEVELOPMENT,
        }
    )

    assert profile.products_services == []
    assert profile.research_status == ResearchStatus.DEVELOPMENT
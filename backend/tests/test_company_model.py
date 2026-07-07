"""Company model metadata tests."""

from sqlalchemy import Index, UniqueConstraint, inspect

from app.models.company import Company


def test_company_model_columns_match_domain_contract() -> None:
    """Company model exposes the issuer-level intelligence fields."""
    columns = inspect(Company).columns

    expected_columns = {
        "id",
        "name",
        "legal_name",
        "ticker",
        "exchange",
        "sector",
        "industry",
        "country",
        "headquarters",
        "website",
        "description",
        "founded_year",
        "employee_count",
        "market",
        "currency",
        "status",
        "logo_url",
        "created_at",
        "updated_at",
    }

    assert set(columns.keys()) == expected_columns
    assert columns.name.nullable is False
    assert columns.ticker.nullable is False
    assert columns.status.nullable is False


def test_company_model_constraints_and_indexes_are_registered() -> None:
    """Company metadata is migration-ready and searchable."""
    table = Company.__table__
    unique_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    index_names = {index.name for index in table.indexes if isinstance(index, Index)}

    assert "uq_companies_ticker" in unique_names
    assert {
        "ix_companies_ticker",
        "ix_companies_exchange",
        "ix_companies_sector",
        "ix_companies_industry",
        "ix_companies_market",
    }.issubset(index_names)


def test_company_relationships_are_declared() -> None:
    """Company connects to assets and news without implementing future domains yet."""
    relationships = inspect(Company).relationships

    assert "assets" in relationships
    assert "news_articles" in relationships
    assert relationships.assets.mapper.class_.__name__ == "Asset"
    assert relationships.news_articles.mapper.class_.__name__ == "News"
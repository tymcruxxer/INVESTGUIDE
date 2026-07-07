"""create companies table and company intelligence relationships

Revision ID: 20260702_0002
Revises: 20260626_0005
Create Date: 2026-07-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260702_0002"
down_revision: str | None = "20260626_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("exchange", sa.String(length=20), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("market", sa.String(length=100), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("exchange IN ('ZSE', 'VFEX')", name="ck_companies_company_exchange"),
        sa.CheckConstraint("currency IN ('ZWG', 'USD')", name="ck_companies_company_currency"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'delisted')", name="ck_companies_company_status"),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
        sa.UniqueConstraint("ticker", name="uq_companies_ticker"),
    )
    op.create_index("ix_companies_ticker", "companies", ["ticker"], unique=False)
    op.create_index("ix_companies_exchange", "companies", ["exchange"], unique=False)
    op.create_index("ix_companies_sector", "companies", ["sector"], unique=False)
    op.create_index("ix_companies_industry", "companies", ["industry"], unique=False)
    op.create_index("ix_companies_market", "companies", ["market"], unique=False)

    op.create_table(
        "company_news",
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("news_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_company_news_company_id_companies", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["news_id"], ["news_articles.id"], name="fk_company_news_news_id_news_articles", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("company_id", "news_id", name="pk_company_news"),
        sa.UniqueConstraint("company_id", "news_id", name="uq_company_news_company_id_news_id"),
    )

    op.add_column("assets", sa.Column("company_id", sa.Integer(), nullable=True))
    op.create_index("ix_assets_company_id", "assets", ["company_id"], unique=False)
    op.create_foreign_key(
        "fk_assets_company_id_companies",
        "assets",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        INSERT INTO companies (
            name,
            legal_name,
            ticker,
            exchange,
            sector,
            industry,
            country,
            website,
            description,
            market,
            currency,
            status,
            logo_url,
            created_at,
            updated_at
        )
        SELECT
            company_name,
            company_name,
            ticker,
            exchange,
            sector,
            industry,
            'Zimbabwe',
            official_website,
            description,
            exchange,
            currency,
            status,
            logo_url,
            created_at,
            updated_at
        FROM assets
        """
    )
    op.execute(
        """
        UPDATE assets
        SET company_id = companies.id
        FROM companies
        WHERE assets.ticker = companies.ticker
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_assets_company_id_companies", "assets", type_="foreignkey")
    op.drop_index("ix_assets_company_id", table_name="assets")
    op.drop_column("assets", "company_id")
    op.drop_table("company_news")
    op.drop_index("ix_companies_market", table_name="companies")
    op.drop_index("ix_companies_industry", table_name="companies")
    op.drop_index("ix_companies_sector", table_name="companies")
    op.drop_index("ix_companies_exchange", table_name="companies")
    op.drop_index("ix_companies_ticker", table_name="companies")
    op.drop_table("companies")
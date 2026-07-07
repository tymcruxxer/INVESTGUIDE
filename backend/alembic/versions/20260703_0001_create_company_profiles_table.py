"""create company profiles table

Revision ID: 20260703_0001
Revises: 20260702_0002
Create Date: 2026-07-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260703_0001"
down_revision: str | None = "20260702_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("business_summary", sa.Text(), nullable=True),
        sa.Column("primary_business", sa.String(length=255), nullable=True),
        sa.Column("products_services", sa.JSON(), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("sub_industry", sa.String(length=100), nullable=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("exchange", sa.String(length=20), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("employees", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("research_status", sa.String(length=20), server_default="development", nullable=False),
        sa.Column("last_verified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("exchange IN ('ZSE', 'VFEX')", name="ck_company_profiles_company_profile_exchange"),
        sa.CheckConstraint("currency IN ('ZWG', 'USD')", name="ck_company_profiles_company_profile_currency"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'delisted')", name="ck_company_profiles_company_profile_status"),
        sa.CheckConstraint(
            "research_status IN ('development', 'verified', 'needs_review', 'unavailable')",
            name="ck_company_profiles_company_profile_research_status",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_company_profiles_company_id_companies", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_company_profiles"),
        sa.UniqueConstraint("company_id", name="uq_company_profiles_company_id"),
    )
    op.create_index("ix_company_profiles_company_id", "company_profiles", ["company_id"], unique=False)
    op.create_index("ix_company_profiles_research_status", "company_profiles", ["research_status"], unique=False)
    op.create_index("ix_company_profiles_last_verified", "company_profiles", ["last_verified"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_profiles_last_verified", table_name="company_profiles")
    op.drop_index("ix_company_profiles_research_status", table_name="company_profiles")
    op.drop_index("ix_company_profiles_company_id", table_name="company_profiles")
    op.drop_table("company_profiles")
"""create sectors and industries

Revision ID: 20260715_0005
Revises: 20260715_0004
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa

revision = "20260715_0005"
down_revision = "20260715_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sectors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("exchange_coverage", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=100), server_default="Zimbabwe", nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_status", sa.String(length=50), server_default="Development", nullable=False),
        sa.Column("dataset_version", sa.String(length=100), nullable=True),
        sa.Column("external_key", sa.String(length=128), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sectors")),    )
    op.create_index("ix_sectors_slug", "sectors", ["slug"], unique=False)
    op.create_index("ix_sectors_name", "sectors", ["name"], unique=False)
    op.create_index("ix_sectors_country", "sectors", ["country"], unique=False)
    op.create_index("ix_sectors_is_development_data", "sectors", ["is_development_data"], unique=False)

    op.create_table(
        "industries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_status", sa.String(length=50), server_default="Development", nullable=False),
        sa.Column("dataset_version", sa.String(length=100), nullable=True),
        sa.Column("external_key", sa.String(length=128), nullable=True),
        sa.Column("is_development_data", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sector_id"], ["sectors.id"], name=op.f("fk_industries_sector_id_sectors"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_industries")),    )
    op.create_index("ix_industries_slug", "industries", ["slug"], unique=False)
    op.create_index("ix_industries_name", "industries", ["name"], unique=False)
    op.create_index("ix_industries_sector_id", "industries", ["sector_id"], unique=False)
    op.create_index("ix_industries_is_development_data", "industries", ["is_development_data"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_industries_is_development_data", table_name="industries")
    op.drop_index("ix_industries_sector_id", table_name="industries")
    op.drop_index("ix_industries_name", table_name="industries")
    op.drop_index("ix_industries_slug", table_name="industries")
    op.drop_table("industries")
    op.drop_index("ix_sectors_is_development_data", table_name="sectors")
    op.drop_index("ix_sectors_country", table_name="sectors")
    op.drop_index("ix_sectors_name", table_name="sectors")
    op.drop_index("ix_sectors_slug", table_name="sectors")
    op.drop_table("sectors")


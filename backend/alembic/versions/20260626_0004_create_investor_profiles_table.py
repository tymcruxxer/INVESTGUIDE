"""create investor profiles table

Revision ID: 20260626_0004
Revises: 20260625_0003
Create Date: 2026-06-26
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260626_0004"
down_revision: str | None = "20260625_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create investor personalization profile table."""
    op.create_table(
        "investor_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "experience_level",
            sa.Enum(
                "beginner",
                "intermediate",
                "advanced",
                name="investor_experience_level",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            server_default="beginner",
            nullable=False,
        ),
        sa.Column(
            "risk_appetite",
            sa.Enum(
                "conservative",
                "moderate",
                "aggressive",
                name="investor_risk_appetite",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            server_default="moderate",
            nullable=False,
        ),
        sa.Column("investment_horizon", sa.String(length=100), nullable=True),
        sa.Column("planned_investment_range", sa.String(length=100), nullable=True),
        sa.Column("preferred_asset_types", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("investment_goals", sa.JSON(), server_default="[]", nullable=False),
        sa.Column(
            "preferred_language_level",
            sa.Enum(
                "simple",
                "balanced",
                "technical",
                name="investor_preferred_language_level",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            server_default="simple",
            nullable=False,
        ),
        sa.Column("education_focus", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_investor_profiles"),
    )
    op.create_index("ix_investor_profiles_user_id", "investor_profiles", ["user_id"], unique=False)
    op.create_index(
        "ix_investor_profiles_experience_level",
        "investor_profiles",
        ["experience_level"],
        unique=False,
    )
    op.create_index(
        "ix_investor_profiles_risk_appetite",
        "investor_profiles",
        ["risk_appetite"],
        unique=False,
    )


def downgrade() -> None:
    """Drop investor personalization profile table."""
    op.drop_index("ix_investor_profiles_risk_appetite", table_name="investor_profiles")
    op.drop_index("ix_investor_profiles_experience_level", table_name="investor_profiles")
    op.drop_index("ix_investor_profiles_user_id", table_name="investor_profiles")
    op.drop_table("investor_profiles")
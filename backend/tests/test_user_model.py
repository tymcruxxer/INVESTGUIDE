"""User model tests."""

from sqlalchemy import Boolean, String

from app.models.user import User


def test_user_model_has_authentication_columns() -> None:
    """User contains the identity fields required for JWT authentication."""
    columns = User.__table__.columns

    for column_name in (
        "id",
        "email",
        "username",
        "hashed_password",
        "is_active",
        "is_verified",
        "created_at",
        "updated_at",
    ):
        assert column_name in columns

    assert isinstance(columns.email.type, String)
    assert isinstance(columns.hashed_password.type, String)
    assert isinstance(columns.is_active.type, Boolean)
    assert isinstance(columns.is_verified.type, Boolean)


def test_user_model_indexes_and_unique_email() -> None:
    """Email is unique and indexed for authentication lookup."""
    indexes = {index.name for index in User.__table__.indexes}
    constraints = {constraint.name for constraint in User.__table__.constraints}

    assert "ix_users_email" in indexes
    assert "ix_users_username" in indexes
    assert "uq_users_email" in constraints

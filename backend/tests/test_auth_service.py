"""Authentication service tests."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models import User
from app.schemas.auth import UserCreate
from app.services.auth_service import (
    AuthServiceError,
    create_access_token,
    decode_access_token,
    get_user_by_email,
    hash_password,
    register_user,
    verify_credentials,
    verify_password,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_hash_password_does_not_store_plaintext() -> None:
    """Password hashing stores bcrypt output rather than plaintext."""
    hashed = hash_password("secure-password")

    assert hashed != "secure-password"
    assert verify_password("secure-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_register_user_normalizes_email_and_hashes_password(db_session: Session) -> None:
    """Registering a user stores normalized email and hashed password."""
    user = register_user(db_session, UserCreate(email="USER@Example.com", password="password123"))

    assert user.id == 1
    assert user.email == "user@example.com"
    assert user.hashed_password != "password123"
    assert user.is_active is True
    assert user.is_verified is False


def test_register_user_rejects_duplicate_email(db_session: Session) -> None:
    """Duplicate email registrations are rejected before persistence."""
    register_user(db_session, UserCreate(email="user@example.com", password="password123"))

    with pytest.raises(AuthServiceError) as exc_info:
        register_user(db_session, UserCreate(email="USER@example.com", password="password456"))

    assert exc_info.value.error_code == "EMAIL_ALREADY_REGISTERED"


def test_verify_credentials_returns_user_for_valid_credentials(db_session: Session) -> None:
    """Valid email/password credentials return the active user."""
    register_user(db_session, UserCreate(email="user@example.com", password="password123"))

    user = verify_credentials(db_session, "USER@example.com", "password123")

    assert user is not None
    assert user.email == "user@example.com"


def test_verify_credentials_returns_none_for_invalid_password(db_session: Session) -> None:
    """Invalid passwords are rejected."""
    register_user(db_session, UserCreate(email="user@example.com", password="password123"))

    assert verify_credentials(db_session, "user@example.com", "wrong") is None


def test_verify_credentials_returns_none_for_inactive_user(db_session: Session) -> None:
    """Inactive users cannot authenticate."""
    user = register_user(db_session, UserCreate(email="user@example.com", password="password123"))
    user.is_active = False
    db_session.commit()

    assert verify_credentials(db_session, "user@example.com", "password123") is None


def test_jwt_generation_and_validation(db_session: Session) -> None:
    """JWTs include the user id and email claims."""
    user = register_user(db_session, UserCreate(email="user@example.com", password="password123"))

    token = create_access_token(user, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)

    assert payload.sub == user.id
    assert payload.email == "user@example.com"


def test_decode_access_token_rejects_invalid_token() -> None:
    """Malformed JWTs are rejected."""
    with pytest.raises(AuthServiceError) as exc_info:
        decode_access_token("not-a-token")

    assert exc_info.value.error_code == "INVALID_TOKEN"


def test_get_user_by_email_uses_normalized_lookup(db_session: Session) -> None:
    """Email lookups are case-insensitive via normalization."""
    register_user(db_session, UserCreate(email="user@example.com", password="password123"))

    user = get_user_by_email(db_session, "USER@example.com")

    assert isinstance(user, User)
    assert user.email == "user@example.com"

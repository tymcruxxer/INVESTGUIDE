"""Authentication route tests."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.services.auth_service import create_access_token, get_user_by_email


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Provide a TestClient with database dependency overridden."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _signup(client: TestClient, email: str = "user@example.com", password: str = "password123") -> str:
    response = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_auth_routes_are_registered() -> None:
    """Auth routes are mounted under the versioned API."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/auth/signup" in routes
    assert "/api/v1/auth/login" in routes
    assert "/api/v1/auth/me" in routes


def test_signup_returns_user_and_access_token(client: TestClient) -> None:
    """Signup creates a user and returns a bearer token."""
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "USER@example.com", "password": "password123", "username": " investor "},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["user"]["email"] == "user@example.com"
    assert body["data"]["user"]["username"] == "investor"
    assert body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"


def test_signup_rejects_duplicate_email(client: TestClient) -> None:
    """Duplicate signup returns a consistent conflict envelope."""
    _signup(client)

    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "USER@example.com", "password": "password456"},
    )
    body = response.json()

    assert response.status_code == 409
    assert body["success"] is False
    assert body["error_code"] == "EMAIL_ALREADY_REGISTERED"


def test_login_success_returns_token_and_user(client: TestClient) -> None:
    """Login returns a token for valid credentials."""
    _signup(client, password="password123")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "USER@example.com", "password": "password123"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["email"] == "user@example.com"


def test_login_failure_returns_unauthorized_envelope(client: TestClient) -> None:
    """Invalid credentials return 401 without leaking account details."""
    _signup(client, password="password123")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrong"},
    )
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error_code"] == "INVALID_CREDENTIALS"


def test_me_returns_current_user(client: TestClient) -> None:
    """The current user endpoint returns the bearer token owner."""
    token = _signup(client)

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["email"] == "user@example.com"


def test_me_requires_authentication(client: TestClient) -> None:
    """Missing bearer token returns the global auth error envelope."""
    response = client.get("/api/v1/auth/me")
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error_code"] == "HTTP_ERROR"


def test_me_rejects_invalid_token(client: TestClient) -> None:
    """Invalid bearer tokens are rejected."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad-token"})
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error_code"] == "HTTP_ERROR"



def test_me_rejects_expired_token(client: TestClient, db_session: Session) -> None:
    """Expired bearer tokens are rejected with a 401 envelope."""
    _signup(client)
    user = get_user_by_email(db_session, "user@example.com")
    assert user is not None
    expired_token = create_access_token(user, expires_delta=timedelta(minutes=-1))

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error_code"] == "HTTP_ERROR"


def test_inactive_user_cannot_access_me(client: TestClient, db_session: Session) -> None:
    """Inactive users with otherwise valid tokens cannot access the current-user endpoint."""
    token = _signup(client)
    user = get_user_by_email(db_session, "user@example.com")
    assert user is not None
    user.is_active = False
    db_session.commit()

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error_code"] == "HTTP_ERROR"



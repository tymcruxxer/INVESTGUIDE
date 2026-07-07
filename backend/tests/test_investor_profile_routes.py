"""Investor profile API route tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app


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


def test_investor_profile_route_is_registered() -> None:
    """Investor profile routes are mounted under the versioned API."""
    routes = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/investor-profile" in routes


def test_get_profile_missing_returns_error_envelope(client: TestClient) -> None:
    """GET returns 404 envelope when no development profile exists."""
    response = client.get("/api/v1/investor-profile")
    body = response.json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "message": "Investor profile was not found",
        "error_code": "INVESTOR_PROFILE_NOT_FOUND",
        "details": {},
    }


def test_post_profile_creates_default_profile(client: TestClient) -> None:
    """POST creates a beginner-friendly default profile."""
    response = client.post("/api/v1/investor-profile", json={})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Investor profile created successfully"
    assert body["data"]["id"] == 1
    assert body["data"]["experience_level"] == "beginner"
    assert body["data"]["risk_appetite"] == "moderate"
    assert body["data"]["preferred_language_level"] == "simple"


def test_get_profile_returns_first_profile(client: TestClient) -> None:
    """GET returns the first profile until authentication exists."""
    client.post(
        "/api/v1/investor-profile",
        json={
            "experience_level": "beginner",
            "risk_appetite": "moderate",
            "investment_horizon": "long_term",
            "preferred_asset_types": ["zse", "reits"],
            "investment_goals": ["long_term_wealth", "learning"],
        },
    )

    response = client.get("/api/v1/investor-profile")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Investor profile retrieved successfully"
    assert body["data"]["investment_horizon"] == "long_term"
    assert body["meta"] == {"profile_resolution": "development_fallback_first_profile"}


def test_put_profile_updates_existing_profile(client: TestClient) -> None:
    """PUT partially updates the existing development profile."""
    client.post("/api/v1/investor-profile", json={"investment_goals": ["learning"]})

    response = client.put(
        "/api/v1/investor-profile",
        json={
            "experience_level": "intermediate",
            "risk_appetite": "conservative",
            "investment_goals": ["capital_preservation", "learning"],
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["message"] == "Investor profile updated successfully"
    assert body["data"]["experience_level"] == "intermediate"
    assert body["data"]["risk_appetite"] == "conservative"
    assert body["data"]["investment_goals"] == ["capital_preservation", "learning"]


def test_put_profile_missing_returns_error_envelope(client: TestClient) -> None:
    """PUT returns 404 when no development profile exists."""
    response = client.put("/api/v1/investor-profile", json={"risk_appetite": "moderate"})

    assert response.status_code == 404
    assert response.json()["error_code"] == "INVESTOR_PROFILE_NOT_FOUND"


def test_profile_endpoint_rejects_malformed_list_payload(client: TestClient) -> None:
    """Malformed JSON list fields return the global validation envelope."""
    response = client.post(
        "/api/v1/investor-profile",
        json={"investment_goals": "learning"},
    )
    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert body["error_code"] == "VALIDATION_ERROR"


def test_profile_endpoint_rejects_unsupported_asset_type(client: TestClient) -> None:
    """Unsupported asset preferences return a profile validation envelope."""
    response = client.post(
        "/api/v1/investor-profile",
        json={"preferred_asset_types": ["crypto"]},
    )
    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert body["error_code"] == "INVESTOR_PROFILE_VALIDATION_ERROR"
    assert "preferred_asset_types" in body["details"]


def _signup(client: TestClient, email: str = "profile@example.com") -> str:
    """Create a user and return an access token."""
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_authenticated_profile_is_attached_to_current_user(client: TestClient) -> None:
    """Authenticated POST/GET uses the current user's profile instead of first row fallback."""
    client.post("/api/v1/investor-profile", json={"investment_goals": ["learning"]})
    token = _signup(client)

    create_response = client.post(
        "/api/v1/investor-profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "investment_horizon": "long_term",
            "preferred_asset_types": ["zse"],
            "investment_goals": ["long_term_wealth"],
        },
    )
    created = create_response.json()

    assert create_response.status_code == 200
    assert created["data"]["user_id"] == 1
    assert created["meta"] == {"profile_resolution": "authenticated_user"}

    get_response = client.get(
        "/api/v1/investor-profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["data"]["investment_goals"] == ["long_term_wealth"]
    assert body["meta"] == {"profile_resolution": "authenticated_user"}


def test_authenticated_profile_update_ignores_payload_user_id(client: TestClient) -> None:
    """Authenticated updates cannot move a profile to another user id from JSON."""
    token = _signup(client)
    client.post(
        "/api/v1/investor-profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"investment_goals": ["learning"]},
    )

    response = client.put(
        "/api/v1/investor-profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": 999, "investment_goals": ["diversification"]},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["data"]["user_id"] == 1
    assert body["data"]["investment_goals"] == ["diversification"]


def test_authenticated_duplicate_profile_returns_conflict(client: TestClient) -> None:
    """POST rejects creating a second profile for the same user."""
    token = _signup(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/investor-profile", headers=headers, json={})

    response = client.post("/api/v1/investor-profile", headers=headers, json={})
    body = response.json()

    assert response.status_code == 409
    assert body["error_code"] == "INVESTOR_PROFILE_ALREADY_EXISTS"


def test_profile_requires_authentication_outside_development(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unauthenticated profile access is rejected when development fallback is disabled."""
    monkeypatch.setattr("app.api.v1.investor_profile._is_development_environment", lambda: False)

    response = client.get("/api/v1/investor-profile")
    body = response.json()

    assert response.status_code == 401
    assert body["error_code"] == "AUTHENTICATION_REQUIRED"


"""CORS configuration regression tests."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_cors_origins_are_loaded_as_list() -> None:
    """Comma-separated CORS origins from .env are parsed into separate origins."""
    settings = get_settings()

    assert isinstance(settings.cors_origins, list)
    assert "http://localhost:3000" in settings.cors_origins
    assert "http://127.0.0.1:3000" in settings.cors_origins
    assert "http://localhost:3001" in settings.cors_origins
    assert "http://127.0.0.1:3001" in settings.cors_origins


def test_auth_signup_preflight_allows_frontend_fallback_port() -> None:
    """Auth signup accepts preflight requests from the Next.js fallback dev port."""
    client = TestClient(app)

    response = client.options(
        "/api/v1/auth/signup",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3001"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_auth_login_preflight_allows_frontend_fallback_port() -> None:
    """Auth login accepts preflight requests from the Next.js fallback dev port."""
    client = TestClient(app)

    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3001"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()
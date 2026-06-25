"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_success_envelope() -> None:
    """Health endpoint returns 200 and the standard success payload."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Backend is healthy",
        "data": {
            "status": "ok",
            "version": "0.1.0-alpha",
        },
    }

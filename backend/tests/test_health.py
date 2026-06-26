"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.api.v1 import health as health_module
from app.database.diagnostics import DatabaseDiagnostics
from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_success_envelope(monkeypatch) -> None:
    """Health endpoint returns 200 and the standard success payload."""
    monkeypatch.setattr(
        health_module,
        "run_database_diagnostics",
        lambda: DatabaseDiagnostics(database="connected", migrations="current"),
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Backend is healthy",
        "data": {
            "status": "ok",
            "database": "connected",
            "migrations": "current",
            "environment": "development",
            "version": "0.1.0-alpha",
        },
    }

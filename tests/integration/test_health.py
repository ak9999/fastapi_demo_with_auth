"""Integration tests for health check endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_returns_healthy() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Application is alive"}


def test_readiness_returns_ready() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "message": "Application is ready to serve requests",
    }

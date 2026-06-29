from app.main import app
from fastapi.testclient import TestClient


def test_health_check_returns_ok() -> None:
    # Exercise the public API contract through FastAPI rather than calling the route function.
    with TestClient(app) as client:
        response = client.get("/api/health")

    # Verify both the HTTP status and the stable liveness payload expected by callers.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

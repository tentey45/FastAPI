from fastapi.testclient import TestClient

from app.main import app


def test_health_and_ready_endpoints() -> None:
    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    ready_response = client.get("/health/ready")
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ok"
    assert ready_response.json()["database"] == "ok"

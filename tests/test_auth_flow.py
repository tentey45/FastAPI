from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_me() -> None:
    client = TestClient(app)
    email = f"user-{uuid4().hex}@example.com"

    response = client.post(
        "/register",
        json={"email": email, "password": "secret123"},
    )

    assert response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": email, "password": "secret123"},
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    token = login_response.json()["access_token"]
    me_response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

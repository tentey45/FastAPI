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


def test_user_can_change_password_and_login_with_new_password() -> None:
    client = TestClient(app)
    email = f"password-user-{uuid4().hex}@example.com"

    register_response = client.post(
        "/register",
        json={"email": email, "password": "old-password"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": email, "password": "old-password"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    change_password_response = client.post(
        "/change-password",
        json={
            "current_password": "old-password",
            "new_password": "new-password",
        },
        headers=headers,
    )
    assert change_password_response.status_code == 200
    assert change_password_response.json()["message"] == "Password updated successfully"

    old_password_login = client.post(
        "/login",
        json={"email": email, "password": "old-password"},
    )
    assert old_password_login.status_code == 401

    new_password_login = client.post(
        "/login",
        json={"email": email, "password": "new-password"},
    )
    assert new_password_login.status_code == 200


def test_change_password_fails_with_incorrect_current_password() -> None:
    client = TestClient(app)
    email = f"password-user-{uuid4().hex}@example.com"

    register_response = client.post(
        "/register",
        json={"email": email, "password": "secret123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": email, "password": "secret123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    change_password_response = client.post(
        "/change-password",
        json={
            "current_password": "wrong-password",
            "new_password": "new-password",
        },
        headers=headers,
    )

    assert change_password_response.status_code == 401
    assert change_password_response.json()["detail"] == "Current password is incorrect"


def test_login_returns_refresh_token_and_refresh_endpoint_issues_new_access_token() -> None:
    client = TestClient(app)
    email = f"refresh-user-{uuid4().hex}@example.com"

    register_response = client.post(
        "/register",
        json={"email": email, "password": "secret123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={"email": email, "password": "secret123"},
    )
    assert login_response.status_code == 200

    payload = login_response.json()
    assert "refresh_token" in payload

    refresh_response = client.post(
        "/refresh-token",
        json={"refresh_token": payload["refresh_token"]},
    )

    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()
    assert refresh_response.json()["token_type"] == "bearer"

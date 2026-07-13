from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_user_can_create_and_list_only_their_todos() -> None:
    client = TestClient(app)
    email = f"todo-user-{uuid4().hex}@example.com"

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

    create_response = client.post(
        "/todos",
        json={"title": "Protected todo", "description": "Should belong to this user"},
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = client.get("/todos", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == "Protected todo"

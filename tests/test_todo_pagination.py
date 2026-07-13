from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_todo_list_supports_filtering_and_pagination() -> None:
    client = TestClient(app)
    email = f"todo-pagination-{uuid4().hex}@example.com"

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

    for index in range(3):
        create_response = client.post(
            "/todos",
            json={"title": f"Todo {index}", "completed": index % 2 == 0},
            headers=headers,
        )
        assert create_response.status_code == 201

    filtered_response = client.get("/todos?completed=true&limit=1&offset=0", headers=headers)
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 1
    assert filtered_response.json()[0]["completed"] is True

    paginated_response = client.get("/todos?limit=2&offset=1", headers=headers)
    assert paginated_response.status_code == 200
    assert len(paginated_response.json()) == 2

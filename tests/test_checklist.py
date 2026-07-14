from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_checklist_items_crud() -> None:
    client = TestClient(app)
    email = f"checklist-user-{uuid4().hex}@example.com"

    # Register & Login
    client.post("/register", json={"email": email, "password": "secret123"})
    login_response = client.post("/login", json={"email": email, "password": "secret123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Todo
    create_todo_resp = client.post(
        "/todos",
        json={"title": "Master Task", "description": "Needs checklist"},
        headers=headers,
    )
    assert create_todo_resp.status_code == 201
    todo_id = create_todo_resp.json()["id"]

    # 2. Add Checklist Item
    add_item_resp = client.post(
        f"/todos/{todo_id}/checklist",
        json={"title": "Subtask 1", "completed": False},
        headers=headers,
    )
    assert add_item_resp.status_code == 201
    item_id = add_item_resp.json()["id"]
    assert add_item_resp.json()["title"] == "Subtask 1"
    assert add_item_resp.json()["completed"] is False

    # 3. Retrieve Todo with nested checklist items
    get_todo_resp = client.get(f"/todos/{todo_id}", headers=headers)
    assert get_todo_resp.status_code == 200
    assert len(get_todo_resp.json()["checklist_items"]) == 1
    assert get_todo_resp.json()["checklist_items"][0]["title"] == "Subtask 1"

    # 4. Update Checklist Item
    update_item_resp = client.put(
        f"/todos/{todo_id}/checklist/{item_id}",
        json={"title": "Subtask 1 Renamed", "completed": True},
        headers=headers,
    )
    assert update_item_resp.status_code == 200
    assert update_item_resp.json()["title"] == "Subtask 1 Renamed"
    assert update_item_resp.json()["completed"] is True

    # 5. Delete Checklist Item
    delete_item_resp = client.delete(f"/todos/{todo_id}/checklist/{item_id}", headers=headers)
    assert delete_item_resp.status_code == 204

    # Verify checklist item is gone
    get_todo_resp2 = client.get(f"/todos/{todo_id}", headers=headers)
    assert len(get_todo_resp2.json()["checklist_items"]) == 0

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_folders_crud_and_todos_association() -> None:
    client = TestClient(app)
    email = f"folder-user-{uuid4().hex}@example.com"

    # Register & Login
    client.post("/register", json={"email": email, "password": "secret123"})
    login_response = client.post("/login", json={"email": email, "password": "secret123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Folder
    create_folder_resp = client.post("/folders", json={"name": "Work Projects"}, headers=headers)
    assert create_folder_resp.status_code == 201
    folder_id = create_folder_resp.json()["id"]
    assert create_folder_resp.json()["name"] == "Work Projects"

    # 2. List Folders
    list_folders_resp = client.get("/folders", headers=headers)
    assert list_folders_resp.status_code == 200
    assert len(list_folders_resp.json()) == 1
    assert list_folders_resp.json()[0]["id"] == folder_id

    # 3. Rename Folder
    rename_resp = client.put(f"/folders/{folder_id}", json={"name": "Important Work"}, headers=headers)
    assert rename_resp.status_code == 200
    assert rename_resp.json()["name"] == "Important Work"

    # 4. Create a Todo inside the folder
    create_todo_resp = client.post(
        "/todos",
        json={"title": "Folder task", "description": "Inside folder", "folder_id": folder_id},
        headers=headers,
    )
    assert create_todo_resp.status_code == 201
    todo_id = create_todo_resp.json()["id"]
    assert create_todo_resp.json()["folder_id"] == folder_id

    # 5. List todos in this folder
    list_todos_resp = client.get(f"/todos?folder_id={folder_id}", headers=headers)
    assert list_todos_resp.status_code == 200
    assert len(list_todos_resp.json()) == 1
    assert list_todos_resp.json()[0]["id"] == todo_id

    # 6. Delete Folder (Cascade delete todo)
    delete_folder_resp = client.delete(f"/folders/{folder_id}", headers=headers)
    assert delete_folder_resp.status_code == 204

    # Verify folder is gone
    get_folders_resp = client.get("/folders", headers=headers)
    assert len(get_folders_resp.json()) == 0

    # Verify todo is gone
    get_todo_resp = client.get(f"/todos/{todo_id}", headers=headers)
    assert get_todo_resp.status_code == 404

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data


def test_list_courses():
    response = client.get("/courses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_documents_empty_query():
    response = client.post("/search/documents", json={"query": "Python"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_conversations_crud():
    # Create
    resp = client.post("/conversations", json={"title": "Test"})
    assert resp.status_code == 200
    conv_id = resp.json()["id"]

    # List
    resp = client.get("/conversations")
    assert resp.status_code == 200

    # Get
    resp = client.get(f"/conversations/{conv_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test"

    # Delete
    resp = client.delete(f"/conversations/{conv_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

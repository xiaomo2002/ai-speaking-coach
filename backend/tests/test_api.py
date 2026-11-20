"""API smoke tests and persistence/validation regression tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(database_path=tmp_path / "test.sqlite3")
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_home(client):
    assert client.get("/health").json()["status"] == "ok"
    page = client.get("/")
    assert page.status_code == 200
    assert "SpeakQuest" in page.text


def test_catalog_and_question_lookup(client):
    catalog = client.get("/api/v1/lessons")
    assert catalog.status_code == 200
    lessons = catalog.json()
    assert len(lessons) == 3
    assert sum(len(item["questions"]) for item in lessons) == 15
    assert client.get("/api/v1/lessons/daily").json()["questions"][0]["id"] == "daily-1"
    assert client.get("/api/v1/lessons/unknown").status_code == 404


def test_evaluation_is_text_based(client):
    endpoint = "/api/v1/practice/evaluate"
    payload = {"lesson_id": "daily", "question_id": "daily-1", "transcript": "HELLO, nice to meet you!"}
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200
    assert response.json()["score"] == 100
    assert response.json()["passed"] is True
    assert response.json()["xp_gained"] == 0  # no session supplied

    bad = client.post(endpoint, json={**payload, "transcript": "good morning"})
    assert bad.status_code == 200
    assert bad.json()["passed"] is False
    assert bad.json()["missing_words"]
    assert client.post(endpoint, json={**payload, "question_id": "coffee-1"}).status_code == 404


def test_validation_and_authentication(client):
    endpoint = "/api/v1/practice/evaluate"
    payload = {"lesson_id": "daily", "question_id": "daily-1", "transcript": "  "}
    assert client.post(endpoint, json=payload).status_code == 422
    assert client.get("/api/v1/progress").status_code == 401
    assert client.get("/api/v1/progress", headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert client.post(
        endpoint,
        json={**payload, "transcript": "Hello nice to meet you"},
        headers={"Authorization": "Bearer invalid"},
    ).status_code == 401


def test_sessions_progress_and_single_award(client):
    session = client.post("/api/v1/sessions")
    assert session.status_code == 201
    token = session.json()["session_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"lesson_id": "daily", "question_id": "daily-1", "transcript": "Hello nice to meet you"}

    first = client.post("/api/v1/practice/evaluate", headers=headers, json=payload).json()
    assert first["passed"] is True
    assert first["xp_gained"] == 20
    assert first["progress"]["xp"] == 20
    assert first["progress"]["streak"] == 1
    assert first["progress"]["completed_question_ids"] == ["daily-1"]

    second = client.post("/api/v1/practice/evaluate", headers=headers, json=payload).json()
    assert second["xp_gained"] == 0
    assert second["progress"]["xp"] == 20

    client.post("/api/v1/practice/evaluate", headers=headers, json={**payload, "transcript": "oops"})
    progress = client.get("/api/v1/progress", headers=headers).json()
    assert progress["xp"] == 20
    assert progress["streak"] == 0
    assert progress["completed_question_ids"] == ["daily-1"]

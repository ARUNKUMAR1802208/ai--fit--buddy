import os

os.environ["MOCK_AI"] = "true"
os.environ["ADMIN_PASSWORD"] = "test-admin"
os.environ["SESSION_SECRET"] = "test-secret"

from fastapi.testclient import TestClient

from app.main import app


def test_homepage():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "FitBuddy" in response.text


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_generate_api_with_mock_ai():
    payload = {
        "name": "Test User",
        "user_id": "test001",
        "age": 21,
        "weight": 65,
        "goal": "general wellness",
        "intensity": "medium",
        "experience_level": "beginner",
    }
    with TestClient(app) as client:
        response = client.post("/api/generate-workout", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert len(body["plan"]["days"]) == 7
        assert "nutrition_tip" in body


def test_admin_login():
    with TestClient(app) as client:
        response = client.post("/admin/login", data={"password": "test-admin"}, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/view-all-users"

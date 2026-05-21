from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_movies_endpoint_returns_seed_data():
    response = client.get("/api/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert {"id", "title", "genre", "description"}.issubset(data[0].keys())


def test_query_recommendations():
    response = client.post("/api/recommendations/query", json={"query": "AI cybersecurity systems"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "recommendation_score" in data[0]

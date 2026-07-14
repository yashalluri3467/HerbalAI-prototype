"""Smoke tests for the health/root endpoints (no DB or model needed)."""

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_root_returns_available_datasets():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "online"
    assert "available_datasets" in body


def test_health_endpoint_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

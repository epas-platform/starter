"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test basic health check returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "profile" in data


def test_health_returns_version(client: TestClient):
    """Test health check returns application version."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Version should match app version
    assert data["version"] == "0.1.0"


def test_health_returns_profile(client: TestClient):
    """Test health check returns current profile."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Should return the configured profile
    assert data["profile"] in ["dev", "prod", "test"]

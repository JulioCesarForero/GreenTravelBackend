"""
Tests for provedor routes.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_get_provedores(client: TestClient):
    """Test getting provedores list."""
    response = client.get("/api/v1/provedores")
    assert response.status_code == 200
    data = response.json()
    assert "provedores" in data
    assert "total" in data


@pytest.mark.integration
def test_create_provedor(client: TestClient):
    """Test creating a provedor."""
    provedor_data = {
        "provedor_nombre": "Test Proveedor",
        "provedor_razonsocial": "Test Proveedor S.A.",
        "provedor_estado": 1
    }
    
    response = client.post("/api/v1/provedores", json=provedor_data)
    assert response.status_code == 201
    data = response.json()
    assert data["provedor_nombre"] == "Test Proveedor"


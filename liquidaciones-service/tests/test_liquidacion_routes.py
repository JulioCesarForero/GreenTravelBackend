"""
Tests for liquidacion routes.
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
def test_get_liquidaciones(client: TestClient):
    """Test getting liquidaciones list."""
    response = client.get("/api/v1/liquidaciones")
    assert response.status_code == 200
    data = response.json()
    assert "liquidaciones" in data
    assert "total" in data


@pytest.mark.integration
def test_create_liquidacion(client: TestClient):
    """Test creating a liquidacion."""
    liquidacion_data = {
        "observaciones": "Test observaciones",
        "nombre_empresa": "Test Empresa",
        "estado": 1
    }
    
    response = client.post("/api/v1/liquidaciones", json=liquidacion_data)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre_empresa"] == "Test Empresa"


"""
Tests for invoice API endpoints.

Tests:
- HTTP endpoints
- Request validation
- Response formats
- Error handling
"""

import pytest
from datetime import datetime
from decimal import Decimal


@pytest.mark.integration
def test_get_invoices(client):
    """Test GET /api/v1/invoices endpoint."""
    response = client.get("/api/v1/invoices")
    
    assert response.status_code == 200
    data = response.json()
    assert "invoices" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data


@pytest.mark.integration
def test_create_invoice(client, sample_invoice_data):
    """Test POST /api/v1/invoices endpoint."""
    # Convert datetime to ISO format string
    invoice_data = sample_invoice_data.copy()
    invoice_data["issue_date"] = invoice_data["issue_date"].isoformat()
    
    response = client.post("/api/v1/invoices", json=invoice_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["invoice_number"] == invoice_data["invoice_number"]
    assert "id" in data


@pytest.mark.integration
def test_get_invoice_by_id(client, sample_invoice):
    """Test GET /api/v1/invoices/{id} endpoint."""
    response = client.get(f"/api/v1/invoices/{sample_invoice.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_invoice.id
    assert data["invoice_number"] == sample_invoice.invoice_number


@pytest.mark.integration
def test_update_invoice(client, sample_invoice):
    """Test PUT /api/v1/invoices/{id} endpoint."""
    update_data = {"paid": True}
    
    response = client.put(f"/api/v1/invoices/{sample_invoice.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["paid"] is True


@pytest.mark.integration
def test_delete_invoice(client, sample_invoice):
    """Test DELETE /api/v1/invoices/{id} endpoint."""
    response = client.delete(f"/api/v1/invoices/{sample_invoice.id}")
    
    assert response.status_code == 204


@pytest.mark.integration
def test_create_invoice_with_items(client, sample_invoice_data):
    """Test POST /api/v1/invoices/with-items endpoint."""
    invoice_data = sample_invoice_data.copy()
    invoice_data["issue_date"] = invoice_data["issue_date"].isoformat()
    invoice_data["items"] = [
        {
            "description": "Habitación estándar",
            "quantity": 2,
            "unit_price": 150000.00,
            "tax_rate": 19,
            "total_amount": 357000.00
        }
    ]
    
    response = client.post("/api/v1/invoices/with-items", json=invoice_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "items" in data
    assert len(data["items"]) == 1


@pytest.mark.integration
def test_get_invoice_stats(client):
    """Test GET /api/v1/invoices/stats endpoint."""
    response = client.get("/api/v1/invoices/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "paid" in data
    assert "unpaid" in data
    assert "total_amount" in data


@pytest.mark.integration
def test_get_invoice_not_found(client):
    """Test GET /api/v1/invoices/{id} with non-existent ID."""
    response = client.get("/api/v1/invoices/99999")
    
    assert response.status_code == 404


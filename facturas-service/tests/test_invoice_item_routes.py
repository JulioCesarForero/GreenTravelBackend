"""
Tests for invoice item API endpoints.

Tests:
- HTTP endpoints
- Request validation
- Response formats
- Error handling
"""

import pytest
from decimal import Decimal


@pytest.mark.integration
def test_get_invoice_items(client, sample_invoice):
    """Test GET /api/v1/invoices/{id}/items endpoint."""
    response = client.get(f"/api/v1/invoices/{sample_invoice.id}/items")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "invoice_id" in data


@pytest.mark.integration
def test_create_invoice_item(client, sample_invoice, sample_invoice_item_data):
    """Test POST /api/v1/invoices/{id}/items endpoint."""
    item_data = sample_invoice_item_data.copy()
    # Convert Decimal to float for JSON
    item_data["quantity"] = float(item_data["quantity"])
    item_data["unit_price"] = float(item_data["unit_price"])
    item_data["tax_rate"] = float(item_data["tax_rate"])
    item_data["total_amount"] = float(item_data["total_amount"])
    
    response = client.post(f"/api/v1/invoices/{sample_invoice.id}/items", json=item_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == item_data["description"]
    assert data["invoice_id"] == sample_invoice.id


@pytest.mark.integration
def test_get_invoice_item_by_id(client, sample_invoice_item):
    """Test GET /api/v1/invoice-items/{id} endpoint."""
    response = client.get(f"/api/v1/invoice-items/{sample_invoice_item.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_invoice_item.id
    assert data["invoice_id"] == sample_invoice_item.invoice_id


@pytest.mark.integration
def test_update_invoice_item(client, sample_invoice_item):
    """Test PUT /api/v1/invoice-items/{id} endpoint."""
    update_data = {"quantity": 3}
    
    response = client.put(f"/api/v1/invoice-items/{sample_invoice_item.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 3


@pytest.mark.integration
def test_delete_invoice_item(client, sample_invoice_item):
    """Test DELETE /api/v1/invoice-items/{id} endpoint."""
    response = client.delete(f"/api/v1/invoice-items/{sample_invoice_item.id}")
    
    assert response.status_code == 204


@pytest.mark.integration
def test_get_invoice_item_not_found(client):
    """Test GET /api/v1/invoice-items/{id} with non-existent ID."""
    response = client.get("/api/v1/invoice-items/99999")
    
    assert response.status_code == 404


@pytest.mark.integration
def test_create_item_for_nonexistent_invoice(client, sample_invoice_item_data):
    """Test creating item for non-existent invoice."""
    item_data = sample_invoice_item_data.copy()
    item_data["quantity"] = float(item_data["quantity"])
    item_data["unit_price"] = float(item_data["unit_price"])
    item_data["tax_rate"] = float(item_data["tax_rate"])
    item_data["total_amount"] = float(item_data["total_amount"])
    
    response = client.post("/api/v1/invoices/99999/items", json=item_data)
    
    assert response.status_code == 404


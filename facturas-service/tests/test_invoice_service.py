"""
Tests for InvoiceService business logic.

Tests:
- CRUD operations
- Business validations
- Calculations
- Statistics
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.invoice_service import InvoiceService
from app.models.invoice import InvoiceCreateRequest, InvoiceUpdateRequest, InvoiceCreateWithItemsRequest


@pytest.mark.unit
def test_create_invoice(db_session: Session, sample_invoice_data):
    """Test creating an invoice."""
    service = InvoiceService(db_session)
    
    request = InvoiceCreateRequest(**sample_invoice_data)
    result = service.create(request)
    
    assert result.id is not None
    assert result.invoice_number == sample_invoice_data["invoice_number"]
    assert result.total_amount == sample_invoice_data["total_amount"]


@pytest.mark.unit
def test_create_invoice_with_items(db_session: Session, sample_invoice_data):
    """Test creating an invoice with nested items."""
    service = InvoiceService(db_session)
    
    # Create request with items
    items_data = [
        {
            "description": "Habitación estándar",
            "quantity": Decimal("2"),
            "unit_price": Decimal("150000.00"),
            "tax_rate": Decimal("19"),
            "total_amount": Decimal("357000.00")
        }
    ]
    
    request_data = sample_invoice_data.copy()
    request_data["items"] = items_data
    request = InvoiceCreateWithItemsRequest(**request_data)
    
    result = service.create_with_items(request)
    
    assert result.id is not None
    assert len(result.items) == 1
    assert result.items[0].description == "Habitación estándar"


@pytest.mark.unit
def test_get_invoice_by_id(db_session: Session, sample_invoice):
    """Test getting invoice by ID."""
    service = InvoiceService(db_session)
    
    result = service.get_by_id(sample_invoice.id)
    
    assert result is not None
    assert result.id == sample_invoice.id
    assert result.invoice_number == sample_invoice.invoice_number


@pytest.mark.unit
def test_get_all_invoices(db_session: Session, sample_invoice):
    """Test getting all invoices with pagination."""
    service = InvoiceService(db_session)
    
    result = service.get_all(page=1, limit=10)
    
    assert result.total >= 1
    assert len(result.invoices) >= 1
    assert result.page == 1
    assert result.limit == 10


@pytest.mark.unit
def test_update_invoice(db_session: Session, sample_invoice):
    """Test updating an invoice."""
    service = InvoiceService(db_session)
    
    update_request = InvoiceUpdateRequest(paid=True)
    result = service.update(sample_invoice.id, update_request)
    
    assert result is not None
    assert result.paid is True


@pytest.mark.unit
def test_delete_invoice(db_session: Session, sample_invoice):
    """Test deleting an invoice."""
    service = InvoiceService(db_session)
    
    deleted = service.delete(sample_invoice.id)
    
    assert deleted is True
    
    # Verify it's deleted
    result = service.get_by_id(sample_invoice.id)
    assert result is None


@pytest.mark.unit
def test_get_stats(db_session: Session, sample_invoice):
    """Test getting invoice statistics."""
    service = InvoiceService(db_session)
    
    stats = service.get_stats()
    
    assert stats.total >= 1
    assert stats.paid >= 0
    assert stats.unpaid >= 1
    assert stats.total_amount >= Decimal("0")


@pytest.mark.unit
def test_validate_departure_date_after_arrival_date(db_session: Session, sample_invoice_data):
    """Test validation: departure_date must be >= arrival_date."""
    service = InvoiceService(db_session)
    
    from datetime import date
    
    request_data = sample_invoice_data.copy()
    request_data["arrival_date"] = date(2025, 1, 20)
    request_data["departure_date"] = date(2025, 1, 15)  # Before arrival
    
    request = InvoiceCreateRequest(**request_data)
    
    with pytest.raises(ValueError, match="departure_date must be >= arrival_date"):
        service.create(request)


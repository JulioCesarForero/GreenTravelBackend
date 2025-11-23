"""
Tests for InvoiceItemService business logic.

Tests:
- CRUD operations
- Automatic total recalculation
- Relationship validation
"""

import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.invoice_item_service import InvoiceItemService
from app.models.invoice_item import InvoiceItemCreateRequest, InvoiceItemUpdateRequest


@pytest.mark.unit
def test_create_invoice_item(db_session: Session, sample_invoice, sample_invoice_item_data):
    """Test creating an invoice item."""
    service = InvoiceItemService(db_session)
    
    request = InvoiceItemCreateRequest(**sample_invoice_item_data)
    result = service.create(sample_invoice.id, request)
    
    assert result.id is not None
    assert result.invoice_id == sample_invoice.id
    assert result.description == sample_invoice_item_data["description"]


@pytest.mark.unit
def test_create_item_recalculates_invoice_total(db_session: Session, sample_invoice, sample_invoice_item_data):
    """Test that creating an item recalculates invoice total."""
    service = InvoiceItemService(db_session)
    from app.services.invoice_service import InvoiceService
    
    # Get initial total
    invoice_service = InvoiceService(db_session)
    initial_invoice = invoice_service.get_by_id(sample_invoice.id)
    initial_total = initial_invoice.total_amount
    
    # Create item
    request = InvoiceItemCreateRequest(**sample_invoice_item_data)
    service.create(sample_invoice.id, request)
    
    # Verify invoice total was updated
    updated_invoice = invoice_service.get_by_id(sample_invoice.id)
    assert updated_invoice.total_amount == initial_total + sample_invoice_item_data["total_amount"]


@pytest.mark.unit
def test_get_items_by_invoice_id(db_session: Session, sample_invoice, sample_invoice_item):
    """Test getting items by invoice ID."""
    service = InvoiceItemService(db_session)
    
    result = service.get_by_invoice_id(sample_invoice.id)
    
    assert result.total >= 1
    assert len(result.items) >= 1
    assert result.invoice_id == sample_invoice.id


@pytest.mark.unit
def test_update_invoice_item(db_session: Session, sample_invoice_item):
    """Test updating an invoice item."""
    service = InvoiceItemService(db_session)
    
    update_request = InvoiceItemUpdateRequest(quantity=Decimal("3"))
    result = service.update(sample_invoice_item.id, update_request)
    
    assert result is not None
    assert result.quantity == Decimal("3")


@pytest.mark.unit
def test_delete_invoice_item(db_session: Session, sample_invoice_item):
    """Test deleting an invoice item."""
    service = InvoiceItemService(db_session)
    
    deleted = service.delete(sample_invoice_item.id)
    
    assert deleted is True
    
    # Verify it's deleted
    result = service.get_by_id(sample_invoice_item.id)
    assert result is None


@pytest.mark.unit
def test_delete_item_recalculates_invoice_total(db_session: Session, sample_invoice, sample_invoice_item):
    """Test that deleting an item recalculates invoice total."""
    service = InvoiceItemService(db_session)
    from app.services.invoice_service import InvoiceService
    
    # Get initial total
    invoice_service = InvoiceService(db_session)
    initial_invoice = invoice_service.get_by_id(sample_invoice.id)
    initial_total = initial_invoice.total_amount
    
    # Delete item
    service.delete(sample_invoice_item.id)
    
    # Verify invoice total was updated
    updated_invoice = invoice_service.get_by_id(sample_invoice.id)
    assert updated_invoice.total_amount == initial_total - sample_invoice_item.total_amount


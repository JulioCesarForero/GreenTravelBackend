"""
Tests for database connection and initialization.

Tests:
- Database connection
- Table creation
- Model relationships
"""

import pytest
from sqlalchemy.orm import Session
from app.database.connection import Base, engine, test_db_connection
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem


@pytest.mark.database
def test_database_connection(db_session: Session):
    """Test database connection."""
    # Simple query to test connection
    result = db_session.execute("SELECT 1").scalar()
    assert result == 1


@pytest.mark.database
def test_invoice_table_exists(db_session: Session):
    """Test that Invoice table exists."""
    # Try to query the table
    count = db_session.query(Invoice).count()
    assert isinstance(count, int)


@pytest.mark.database
def test_invoice_item_table_exists(db_session: Session):
    """Test that InvoiceItem table exists."""
    # Try to query the table
    count = db_session.query(InvoiceItem).count()
    assert isinstance(count, int)


@pytest.mark.database
def test_invoice_item_relationship(db_session: Session, sample_invoice, sample_invoice_item):
    """Test relationship between Invoice and InvoiceItem."""
    # Test relationship from invoice to items
    assert len(sample_invoice.items) == 1
    assert sample_invoice.items[0].id == sample_invoice_item.id
    
    # Test relationship from item to invoice
    assert sample_invoice_item.invoice.id == sample_invoice.id
    assert sample_invoice_item.invoice.invoice_number == sample_invoice.invoice_number


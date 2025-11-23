"""
Pytest configuration and shared fixtures for facturas-service tests.

This module provides:
- Database fixtures (in-memory SQLite for fast tests)
- FastAPI test client
- Mock fixtures
- Test data factories
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock

# Import application components
from main import app
from app.database.connection import Base, get_db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem


# ============================================
# DATABASE FIXTURES
# ============================================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create in-memory SQLite database for testing.
    
    Uses SQLite for fast, isolated tests without requiring MySQL.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create database session for testing.
    
    Yields:
        Session: SQLAlchemy session
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create FastAPI test client with mocked database.
    
    Returns:
        TestClient: FastAPI test client
    """
    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Mock database initialization functions
    with patch('main.ensure_database_exists', return_value=True), \
         patch('main.test_db_connection', return_value=True), \
         patch('main.init_db'), \
         patch('main.run_migrations'), \
         patch('main.run_seeds'):
        
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()


# ============================================
# TEST DATA FIXTURES
# ============================================

@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    from datetime import datetime
    from decimal import Decimal
    
    return {
        "invoice_number": "FAC-TEST-001",
        "cufe": "CUFE123456789",
        "provider_name": "Hotel Test",
        "provider_nit": "900123456-7",
        "client_name": "Cliente Test",
        "client_nit": "800123456-7",
        "client_address": "Calle Test 123",
        "client_email": "cliente@test.com",
        "issue_date": datetime(2025, 1, 15, 10, 0, 0),
        "total_amount": Decimal("500000.00"),
        "paid": False,
        "loaded_in_liquidation": False
    }


@pytest.fixture
def sample_invoice_item_data():
    """Sample invoice item data for testing."""
    from decimal import Decimal
    
    return {
        "description": "Habitación estándar",
        "unit": "noche",
        "quantity": Decimal("2"),
        "unit_price": Decimal("150000.00"),
        "tax_rate": Decimal("19"),
        "total_amount": Decimal("357000.00")
    }


@pytest.fixture
def sample_invoice(db_session, sample_invoice_data):
    """Create a sample invoice in the database."""
    invoice = Invoice(**sample_invoice_data)
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def sample_invoice_item(db_session, sample_invoice, sample_invoice_item_data):
    """Create a sample invoice item in the database."""
    item_data = sample_invoice_item_data.copy()
    item_data["invoice_id"] = sample_invoice.id
    item = InvoiceItem(**item_data)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


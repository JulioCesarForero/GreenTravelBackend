"""
Pytest configuration and shared fixtures.

This module provides:
- Test database setup
- FastAPI test client
- Common fixtures
- Test utilities
"""

import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"

from app.database.connection import get_db
from app.models.provedor import Base
from main import app

# ============================================
# TEST DATABASE
# ============================================

# Use SQLite in-memory database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """
    Create test database engine.
    
    Yields:
        Engine: SQLAlchemy engine
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create test database session.
    
    Args:
        db_engine: Test database engine
        
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


# ============================================
# FASTAPI TEST CLIENT
# ============================================

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI test client with database override.
    
    Args:
        db_session: Test database session
        
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        """Override database dependency."""
        try:
            yield db_session
        finally:
            pass
    
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Mock startup functions to avoid real database operations
    with patch('main.ensure_database_exists', return_value=True), \
         patch('main.test_db_connection', return_value=True), \
         patch('main.init_db'), \
         patch('main.run_migrations'), \
         patch('main.run_seeds'):
        
        # Create test client
        with TestClient(app) as test_client:
            yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


# ============================================
# COMMON FIXTURES
# ============================================

@pytest.fixture
def sample_provedor_data():
    """Sample data for creating provedores."""
    return {
        "provedor_nombre": "Test Proveedor",
        "provedor_razonsocial": "Test Proveedor S.A.",
        "provedor_estado": 1
    }


@pytest.fixture
def create_provedor(db_session: Session, sample_provedor_data):
    """
    Factory fixture for creating provedores in the database.
    
    Args:
        db_session: Database session
        sample_provedor_data: Sample data
        
    Returns:
        Callable: Function to create provedores
    """
    from app.models.provedor import Provedor
    
    def _create_provedor(**kwargs):
        """Create provedor with custom data."""
        data = {**sample_provedor_data, **kwargs}
        provedor = Provedor(**data)
        db_session.add(provedor)
        db_session.commit()
        db_session.refresh(provedor)
        return provedor
    
    return _create_provedor


# ============================================
# PYTEST CONFIGURATION
# ============================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "database: Tests requiring database")


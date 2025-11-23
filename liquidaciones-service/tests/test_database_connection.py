"""
Tests for database connection.
"""

import pytest
from app.database.connection import test_db_connection, get_db, SessionLocal


@pytest.mark.database
def test_db_connection():
    """Test database connection."""
    # This test requires a real database connection
    # In CI/CD, use a test database
    pass


@pytest.mark.database
def test_get_db():
    """Test database session dependency."""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        db.close()
    except:
        pass


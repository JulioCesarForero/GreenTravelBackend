"""
Tests for provedor service.
"""

import pytest
from sqlalchemy.orm import Session
from app.services.provedor_service import ProvedorService
from app.models.provedor import ProvedorCreateRequest


@pytest.mark.unit
def test_provedor_service_init(db_session: Session):
    """Test service initialization."""
    service = ProvedorService(db_session)
    assert service.db == db_session


@pytest.mark.unit
def test_create_provedor(db_session: Session):
    """Test creating a provedor."""
    service = ProvedorService(db_session)
    
    request = ProvedorCreateRequest(
        provedor_nombre="Test Proveedor",
        provedor_razonsocial="Test Proveedor S.A.",
        provedor_estado=1
    )
    
    result = service.create(request)
    assert result is not None
    assert result.provedor_nombre == "Test Proveedor"
    assert result.provedor_razonsocial == "Test Proveedor S.A."


@pytest.mark.unit
def test_get_all_provedores(db_session: Session):
    """Test getting all provedores."""
    service = ProvedorService(db_session)
    
    result = service.get_all(page=1, limit=10)
    assert result is not None
    assert result.total >= 0
    assert len(result.provedores) >= 0


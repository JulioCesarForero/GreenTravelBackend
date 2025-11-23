"""
Tests for liquidacion service.
"""

import pytest
from sqlalchemy.orm import Session
from app.services.liquidacion_service import LiquidacionService
from app.models.liquidacion import LiquidacionCreateRequest


@pytest.mark.unit
def test_liquidacion_service_init(db_session: Session):
    """Test service initialization."""
    service = LiquidacionService(db_session)
    assert service.db == db_session


@pytest.mark.unit
def test_create_liquidacion(db_session: Session):
    """Test creating a liquidacion."""
    service = LiquidacionService(db_session)
    
    request = LiquidacionCreateRequest(
        observaciones="Test observaciones",
        nombre_empresa="Test Empresa",
        estado=1
    )
    
    result = service.create(request)
    assert result is not None
    assert result.nombre_empresa == "Test Empresa"
    assert result.observaciones == "Test observaciones"


@pytest.mark.unit
def test_get_all_liquidaciones(db_session: Session):
    """Test getting all liquidaciones."""
    service = LiquidacionService(db_session)
    
    result = service.get_all(page=1, limit=10)
    assert result is not None
    assert result.total >= 0
    assert len(result.liquidaciones) >= 0


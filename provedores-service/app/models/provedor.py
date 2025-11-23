"""
Provedor model demonstrating best practices for SQLAlchemy + Pydantic models.

This module shows:
- SQLAlchemy ORM models with proper types and indexes
- Pydantic models for request/response validation
- Enum definitions
- Model configuration
"""

from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# Import base from database connection
from app.database.connection import Base


# ============================================
# SQLAlchemy ORM MODEL
# ============================================

class Provedor(Base):
    """
    Provedor entity model.
    
    Maps to the colombia_green_travel.provedores table.
    """
    __tablename__ = "provedores"
    
    # Primary key
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    
    # Provider information
    provedor_hotel_code = Column(Integer, nullable=True, comment="Código del hotel del proveedor")
    provedor_razonsocial = Column(String(250), nullable=True, comment="Razón social del proveedor")
    provedor_nombre = Column(String(150), nullable=True, comment="Nombre del proveedor")
    provedor_identificacion = Column(String(25), nullable=True, comment="Identificación del proveedor")
    provedor_direccion = Column(String(250), nullable=True, comment="Dirección del proveedor")
    provedor_telefono = Column(String(25), nullable=True, comment="Teléfono del proveedor")
    
    # Provider classification
    provedor_tipo = Column(Integer, nullable=True, comment="Tipo de proveedor")
    provedor_estado = Column(Integer, nullable=True, default=1, comment="Estado (1=activo, 0=inactivo)")
    provedor_ciudad = Column(Integer, nullable=True, comment="ID de la ciudad")
    
    # Additional information
    provedor_link_dropbox = Column(String(500), nullable=True, comment="Link de Dropbox del proveedor")
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_provedor_hotel_code', 'provedor_hotel_code'),
        Index('idx_provedor_estado', 'provedor_estado'),
        Index('idx_provedor_tipo', 'provedor_tipo'),
        Index('idx_provedor_ciudad', 'provedor_ciudad'),
        {'comment': 'Tabla de proveedores'}
    )

    def __repr__(self):
        return f"<Provedor(id={self.id}, provedor_nombre='{self.provedor_nombre}', provedor_estado={self.provedor_estado})>"


# ============================================
# PYDANTIC REQUEST MODELS
# ============================================

class ProvedorCreateRequest(BaseModel):
    """Request model for creating a provedor."""
    
    provedor_hotel_code: Optional[int] = Field(None, description="Código del hotel del proveedor")
    provedor_razonsocial: Optional[str] = Field(None, max_length=250, description="Razón social del proveedor")
    provedor_nombre: Optional[str] = Field(None, max_length=150, description="Nombre del proveedor")
    provedor_identificacion: Optional[str] = Field(None, max_length=25, description="Identificación del proveedor")
    provedor_direccion: Optional[str] = Field(None, max_length=250, description="Dirección del proveedor")
    provedor_telefono: Optional[str] = Field(None, max_length=25, description="Teléfono del proveedor")
    provedor_tipo: Optional[int] = Field(None, description="Tipo de proveedor")
    provedor_estado: Optional[int] = Field(1, ge=0, le=1, description="Estado (1=activo, 0=inactivo)")
    provedor_ciudad: Optional[int] = Field(None, description="ID de la ciudad")
    provedor_link_dropbox: Optional[str] = Field(None, max_length=500, description="Link de Dropbox del proveedor")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provedor_hotel_code": 12345,
                "provedor_razonsocial": "Hotel Ejemplo S.A.",
                "provedor_nombre": "Hotel Ejemplo",
                "provedor_identificacion": "900123456-7",
                "provedor_direccion": "Calle 123 #45-67, Bogotá",
                "provedor_telefono": "6012345678",
                "provedor_tipo": 1,
                "provedor_estado": 1,
                "provedor_ciudad": 1,
                "provedor_link_dropbox": "https://dropbox.com/proveedor123"
            }
        }
    )


class ProvedorUpdateRequest(BaseModel):
    """Request model for updating a provedor."""
    
    provedor_hotel_code: Optional[int] = Field(None, description="Código del hotel del proveedor")
    provedor_razonsocial: Optional[str] = Field(None, max_length=250, description="Razón social del proveedor")
    provedor_nombre: Optional[str] = Field(None, max_length=150, description="Nombre del proveedor")
    provedor_identificacion: Optional[str] = Field(None, max_length=25, description="Identificación del proveedor")
    provedor_direccion: Optional[str] = Field(None, max_length=250, description="Dirección del proveedor")
    provedor_telefono: Optional[str] = Field(None, max_length=25, description="Teléfono del proveedor")
    provedor_tipo: Optional[int] = Field(None, description="Tipo de proveedor")
    provedor_estado: Optional[int] = Field(None, ge=0, le=1, description="Estado (1=activo, 0=inactivo)")
    provedor_ciudad: Optional[int] = Field(None, description="ID de la ciudad")
    provedor_link_dropbox: Optional[str] = Field(None, max_length=500, description="Link de Dropbox del proveedor")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provedor_estado": 0,
                "provedor_telefono": "6012345679"
            }
        }
    )


# ============================================
# PYDANTIC RESPONSE MODELS
# ============================================

class ProvedorResponse(BaseModel):
    """Response model for a single provedor."""
    
    id: Optional[int] = Field(None, description="ID único")
    provedor_hotel_code: Optional[int] = Field(None, description="Código del hotel del proveedor")
    provedor_razonsocial: Optional[str] = Field(None, description="Razón social del proveedor")
    provedor_nombre: Optional[str] = Field(None, description="Nombre del proveedor")
    provedor_identificacion: Optional[str] = Field(None, description="Identificación del proveedor")
    provedor_direccion: Optional[str] = Field(None, description="Dirección del proveedor")
    provedor_telefono: Optional[str] = Field(None, description="Teléfono del proveedor")
    provedor_tipo: Optional[int] = Field(None, description="Tipo de proveedor")
    provedor_estado: Optional[int] = Field(None, description="Estado (1=activo, 0=inactivo)")
    provedor_ciudad: Optional[int] = Field(None, description="ID de la ciudad")
    provedor_link_dropbox: Optional[str] = Field(None, description="Link de Dropbox del proveedor")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        json_schema_extra={
            "example": {
                "id": 1,
                "provedor_hotel_code": 12345,
                "provedor_nombre": "Hotel Ejemplo",
                "provedor_razonsocial": "Hotel Ejemplo S.A.",
                "provedor_estado": 1
            }
        }
    )


class ProvedorListResponse(BaseModel):
    """Response model for paginated list of provedores."""
    
    provedores: List[ProvedorResponse] = Field(..., description="Lista de proveedores")
    total: int = Field(..., description="Total de proveedores")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Elementos por página")
    pages: int = Field(..., description="Total de páginas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provedores": [
                    {
                        "id": 1,
                        "provedor_nombre": "Hotel Ejemplo",
                        "provedor_estado": 1
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 50,
                "pages": 2
            }
        }
    )


class ProvedorStatsResponse(BaseModel):
    """Response model for provedor statistics."""
    
    total: int = Field(..., description="Total de proveedores")
    activos: int = Field(..., description="Proveedores activos")
    inactivos: int = Field(..., description="Proveedores inactivos")
    por_estado: dict = Field(..., description="Conteo por estado")
    por_tipo: dict = Field(..., description="Conteo por tipo")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150,
                "activos": 120,
                "inactivos": 30,
                "por_estado": {
                    "1": 120,
                    "0": 30
                },
                "por_tipo": {
                    "1": 80,
                    "2": 40
                }
            }
        }
    )


"""
Liquidacion model demonstrating best practices for SQLAlchemy + Pydantic models.

This module shows:
- SQLAlchemy ORM models with proper types and indexes
- Pydantic models for request/response validation
- Enum definitions
- Model configuration
"""

from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# Import base from database connection
from app.database.connection import Base


# ============================================
# SQLAlchemy ORM MODEL
# ============================================

class Liquidacion(Base):
    """
    Liquidacion entity model.
    
    Maps to the colombia_green_travel.liquidaciones table.
    """
    __tablename__ = "liquidaciones"
    
    # Primary key
    id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    
    # Reservation and company information
    id_reserva = Column(Integer, nullable=True, comment="ID de la reserva")
    nombre_asesor = Column(String(150), nullable=True, comment="Nombre del asesor")
    nombre_empresa = Column(String(150), nullable=True, comment="Nombre de la empresa")
    nit_empresa = Column(String(25), nullable=True, comment="NIT de la empresa")
    direccion_empresa = Column(String(150), nullable=True, comment="Dirección de la empresa")
    telefono_empresa = Column(String(15), nullable=True, comment="Teléfono de la empresa")
    
    # Service information
    servicio = Column(String(100), nullable=True, comment="Tipo de servicio")
    fecha_servicio = Column(String(25), nullable=True, comment="Fecha del servicio")
    incluye_servicio = Column(String(100), nullable=True, comment="Incluye del servicio")
    numero_pasajeros = Column(Integer, nullable=True, comment="Número de pasajeros")
    
    # Financial information
    valor_liquidacion = Column(String(50), nullable=True, comment="Valor de la liquidación")
    iva = Column(Integer, nullable=True, comment="Porcentaje de IVA")
    valor_iva = Column(String(50), nullable=True, comment="Valor del IVA")
    valor_total_iva = Column(String(50), nullable=True, comment="Valor total con IVA")
    
    # Passenger information
    nombre_pasajero = Column(String(150), nullable=True, comment="Nombre del pasajero")
    
    # Additional information
    fecha = Column(String(25), nullable=True, comment="Fecha de la liquidación")
    factura = Column(Integer, nullable=True, comment="Número de factura")
    estado = Column(Integer, nullable=True, default=1, comment="Estado (1=activo, 0=inactivo)")
    origen_venta = Column(String(75), nullable=True, comment="Origen de la venta")
    
    # Observations
    observaciones = Column(Text, nullable=False, comment="Observaciones")
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_liquidacion_id_reserva', 'id_reserva'),
        Index('idx_liquidacion_estado', 'estado'),
        Index('idx_liquidacion_fecha', 'fecha'),
        Index('idx_liquidacion_factura', 'factura'),
        {'comment': 'Tabla de liquidaciones'}
    )

    def __repr__(self):
        return f"<Liquidacion(id={self.id}, id_reserva={self.id_reserva}, nombre_empresa='{self.nombre_empresa}')>"


# ============================================
# PYDANTIC REQUEST MODELS
# ============================================

class LiquidacionCreateRequest(BaseModel):
    """Request model for creating a liquidacion."""
    
    id_reserva: Optional[int] = Field(None, description="ID de la reserva")
    nombre_asesor: Optional[str] = Field(None, max_length=150, description="Nombre del asesor")
    nombre_empresa: Optional[str] = Field(None, max_length=150, description="Nombre de la empresa")
    nit_empresa: Optional[str] = Field(None, max_length=25, description="NIT de la empresa")
    direccion_empresa: Optional[str] = Field(None, max_length=150, description="Dirección de la empresa")
    telefono_empresa: Optional[str] = Field(None, max_length=15, description="Teléfono de la empresa")
    observaciones: str = Field(..., description="Observaciones")
    servicio: Optional[str] = Field(None, max_length=100, description="Tipo de servicio")
    fecha_servicio: Optional[str] = Field(None, max_length=25, description="Fecha del servicio")
    incluye_servicio: Optional[str] = Field(None, max_length=100, description="Incluye del servicio")
    numero_pasajeros: Optional[int] = Field(None, ge=0, description="Número de pasajeros")
    valor_liquidacion: Optional[str] = Field(None, max_length=50, description="Valor de la liquidación")
    iva: Optional[int] = Field(None, ge=0, le=100, description="Porcentaje de IVA")
    valor_iva: Optional[str] = Field(None, max_length=50, description="Valor del IVA")
    valor_total_iva: Optional[str] = Field(None, max_length=50, description="Valor total con IVA")
    nombre_pasajero: Optional[str] = Field(None, max_length=150, description="Nombre del pasajero")
    fecha: Optional[str] = Field(None, max_length=25, description="Fecha de la liquidación")
    factura: Optional[int] = Field(None, description="Número de factura")
    estado: Optional[int] = Field(1, ge=0, le=1, description="Estado (1=activo, 0=inactivo)")
    origen_venta: Optional[str] = Field(None, max_length=75, description="Origen de la venta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_reserva": 123,
                "nombre_asesor": "Juan Pérez",
                "nombre_empresa": "Empresa Ejemplo S.A.",
                "nit_empresa": "900123456-7",
                "direccion_empresa": "Calle 123 #45-67",
                "telefono_empresa": "6012345678",
                "observaciones": "Liquidación de prueba",
                "servicio": "Hotel",
                "fecha_servicio": "2025-01-15",
                "incluye_servicio": "Desayuno, WiFi",
                "numero_pasajeros": 2,
                "valor_liquidacion": "500000",
                "iva": 19,
                "valor_iva": "95000",
                "valor_total_iva": "595000",
                "nombre_pasajero": "María García",
                "fecha": "2025-01-10",
                "factura": 1001,
                "estado": 1,
                "origen_venta": "Web"
            }
        }
    )


class LiquidacionUpdateRequest(BaseModel):
    """Request model for updating a liquidacion."""
    
    id_reserva: Optional[int] = Field(None, description="ID de la reserva")
    nombre_asesor: Optional[str] = Field(None, max_length=150, description="Nombre del asesor")
    nombre_empresa: Optional[str] = Field(None, max_length=150, description="Nombre de la empresa")
    nit_empresa: Optional[str] = Field(None, max_length=25, description="NIT de la empresa")
    direccion_empresa: Optional[str] = Field(None, max_length=150, description="Dirección de la empresa")
    telefono_empresa: Optional[str] = Field(None, max_length=15, description="Teléfono de la empresa")
    observaciones: Optional[str] = Field(None, description="Observaciones")
    servicio: Optional[str] = Field(None, max_length=100, description="Tipo de servicio")
    fecha_servicio: Optional[str] = Field(None, max_length=25, description="Fecha del servicio")
    incluye_servicio: Optional[str] = Field(None, max_length=100, description="Incluye del servicio")
    numero_pasajeros: Optional[int] = Field(None, ge=0, description="Número de pasajeros")
    valor_liquidacion: Optional[str] = Field(None, max_length=50, description="Valor de la liquidación")
    iva: Optional[int] = Field(None, ge=0, le=100, description="Porcentaje de IVA")
    valor_iva: Optional[str] = Field(None, max_length=50, description="Valor del IVA")
    valor_total_iva: Optional[str] = Field(None, max_length=50, description="Valor total con IVA")
    nombre_pasajero: Optional[str] = Field(None, max_length=150, description="Nombre del pasajero")
    fecha: Optional[str] = Field(None, max_length=25, description="Fecha de la liquidación")
    factura: Optional[int] = Field(None, description="Número de factura")
    estado: Optional[int] = Field(None, ge=0, le=1, description="Estado (1=activo, 0=inactivo)")
    origen_venta: Optional[str] = Field(None, max_length=75, description="Origen de la venta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": 0,
                "observaciones": "Liquidación actualizada"
            }
        }
    )


# ============================================
# PYDANTIC RESPONSE MODELS
# ============================================

class LiquidacionResponse(BaseModel):
    """Response model for a single liquidacion."""
    
    id: Optional[int] = Field(None, description="ID único")
    id_reserva: Optional[int] = Field(None, description="ID de la reserva")
    nombre_asesor: Optional[str] = Field(None, description="Nombre del asesor")
    nombre_empresa: Optional[str] = Field(None, description="Nombre de la empresa")
    nit_empresa: Optional[str] = Field(None, description="NIT de la empresa")
    direccion_empresa: Optional[str] = Field(None, description="Dirección de la empresa")
    telefono_empresa: Optional[str] = Field(None, description="Teléfono de la empresa")
    observaciones: str = Field(..., description="Observaciones")
    servicio: Optional[str] = Field(None, description="Tipo de servicio")
    fecha_servicio: Optional[str] = Field(None, description="Fecha del servicio")
    incluye_servicio: Optional[str] = Field(None, description="Incluye del servicio")
    numero_pasajeros: Optional[int] = Field(None, description="Número de pasajeros")
    valor_liquidacion: Optional[str] = Field(None, description="Valor de la liquidación")
    iva: Optional[int] = Field(None, description="Porcentaje de IVA")
    valor_iva: Optional[str] = Field(None, description="Valor del IVA")
    valor_total_iva: Optional[str] = Field(None, description="Valor total con IVA")
    nombre_pasajero: Optional[str] = Field(None, description="Nombre del pasajero")
    fecha: Optional[str] = Field(None, description="Fecha de la liquidación")
    factura: Optional[int] = Field(None, description="Número de factura")
    estado: Optional[int] = Field(None, description="Estado (1=activo, 0=inactivo)")
    origen_venta: Optional[str] = Field(None, description="Origen de la venta")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        json_schema_extra={
            "example": {
                "id": 1,
                "id_reserva": 123,
                "nombre_asesor": "Juan Pérez",
                "nombre_empresa": "Empresa Ejemplo S.A.",
                "nit_empresa": "900123456-7",
                "estado": 1
            }
        }
    )


class LiquidacionListResponse(BaseModel):
    """Response model for paginated list of liquidaciones."""
    
    liquidaciones: List[LiquidacionResponse] = Field(..., description="Lista de liquidaciones")
    total: int = Field(..., description="Total de liquidaciones")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Elementos por página")
    pages: int = Field(..., description="Total de páginas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "liquidaciones": [
                    {
                        "id": 1,
                        "id_reserva": 123,
                        "nombre_empresa": "Empresa Ejemplo",
                        "estado": 1
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 50,
                "pages": 2
            }
        }
    )


class LiquidacionStatsResponse(BaseModel):
    """Response model for liquidacion statistics."""
    
    total: int = Field(..., description="Total de liquidaciones")
    activas: int = Field(..., description="Liquidaciones activas")
    inactivas: int = Field(..., description="Liquidaciones inactivas")
    por_estado: dict = Field(..., description="Conteo por estado")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150,
                "activas": 120,
                "inactivas": 30,
                "por_estado": {
                    "1": 120,
                    "0": 30
                }
            }
        }
    )


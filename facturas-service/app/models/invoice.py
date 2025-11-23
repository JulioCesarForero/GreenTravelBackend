"""
Invoice model demonstrating best practices for SQLAlchemy + Pydantic models.

This module shows:
- SQLAlchemy ORM models with proper types and indexes
- Pydantic models for request/response validation
- Model configuration
- Relationship with InvoiceItem
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, Date, Numeric, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from decimal import Decimal

# Import base from database connection
from app.database.connection import Base


# ============================================
# SQLAlchemy ORM MODEL
# ============================================

class Invoice(Base):
    """
    Invoice entity model.
    
    Maps to the invoices table (adapted from PostgreSQL to MySQL).
    """
    __tablename__ = "invoices"

    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Invoice identification
    invoice_number = Column(String(255), nullable=False, comment="Número de factura")
    cufe = Column(String(255), nullable=False, comment="CUFE (Código Único de Factura Electrónica)")
    
    # Provider information
    provider_name = Column(String(255), nullable=False, comment="Nombre del proveedor")
    provider_nit = Column(String(50), nullable=False, comment="NIT del proveedor")
    
    # Client information
    client_name = Column(String(255), nullable=False, comment="Nombre del cliente")
    client_nit = Column(String(50), nullable=False, comment="NIT del cliente")
    client_address = Column(Text, nullable=True, comment="Dirección del cliente")
    client_email = Column(String(255), nullable=True, comment="Email del cliente")
    
    # Dates
    issue_date = Column(DateTime, nullable=False, comment="Fecha de emisión")
    authorization_date = Column(DateTime, nullable=True, comment="Fecha de autorización")
    arrival_date = Column(Date, nullable=True, comment="Fecha de llegada")
    departure_date = Column(Date, nullable=True, comment="Fecha de salida")
    
    # Additional information
    guest_name = Column(String(255), nullable=True, comment="Nombre del huésped")
    cashier_id = Column(String(100), nullable=True, comment="ID del cajero")
    reservation_number = Column(String(100), nullable=True, comment="Número de reserva")
    
    # Financial information
    total_amount = Column(Numeric(19, 2), nullable=False, comment="Monto total")
    payment_method = Column(String(100), nullable=True, comment="Método de pago")
    payment_terms = Column(Text, nullable=True, comment="Términos de pago")
    bank_account = Column(String(100), nullable=True, comment="Cuenta bancaria")
    
    # Additional info
    additional_info = Column(Text, nullable=True, comment="Información adicional")
    
    # Status flags
    loaded_in_liquidation = Column(Boolean, nullable=False, default=False, comment="Cargado en liquidación")
    paid = Column(Boolean, nullable=False, default=False, comment="Pagado")
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Fecha de creación")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Fecha de actualización")
    reviewed_by = Column(String(255), nullable=True, comment="Revisado por")
    
    # Relationship with invoice items
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_invoice_number', 'invoice_number'),
        Index('idx_invoice_cufe', 'cufe'),
        Index('idx_invoice_provider_nit', 'provider_nit'),
        Index('idx_invoice_client_nit', 'client_nit'),
        Index('idx_invoice_issue_date', 'issue_date'),
        Index('idx_invoice_paid', 'paid'),
        Index('idx_invoice_loaded_liquidation', 'loaded_in_liquidation'),
        Index('idx_invoice_reservation', 'reservation_number'),
        {'comment': 'Tabla de facturas'}
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', total_amount={self.total_amount})>"


# ============================================
# PYDANTIC REQUEST MODELS
# ============================================

class InvoiceCreateRequest(BaseModel):
    """Request model for creating an invoice (without items)."""
    
    invoice_number: str = Field(..., max_length=255, description="Número de factura")
    cufe: str = Field(..., max_length=255, description="CUFE")
    provider_name: str = Field(..., max_length=255, description="Nombre del proveedor")
    provider_nit: str = Field(..., max_length=50, description="NIT del proveedor")
    client_name: str = Field(..., max_length=255, description="Nombre del cliente")
    client_nit: str = Field(..., max_length=50, description="NIT del cliente")
    client_address: Optional[str] = Field(None, description="Dirección del cliente")
    client_email: Optional[EmailStr] = Field(None, description="Email del cliente")
    issue_date: datetime = Field(..., description="Fecha de emisión")
    authorization_date: Optional[datetime] = Field(None, description="Fecha de autorización")
    guest_name: Optional[str] = Field(None, max_length=255, description="Nombre del huésped")
    cashier_id: Optional[str] = Field(None, max_length=100, description="ID del cajero")
    arrival_date: Optional[date] = Field(None, description="Fecha de llegada")
    departure_date: Optional[date] = Field(None, description="Fecha de salida")
    reservation_number: Optional[str] = Field(None, max_length=100, description="Número de reserva")
    total_amount: Decimal = Field(..., ge=0, description="Monto total")
    payment_method: Optional[str] = Field(None, max_length=100, description="Método de pago")
    payment_terms: Optional[str] = Field(None, description="Términos de pago")
    bank_account: Optional[str] = Field(None, max_length=100, description="Cuenta bancaria")
    additional_info: Optional[str] = Field(None, description="Información adicional")
    loaded_in_liquidation: bool = Field(False, description="Cargado en liquidación")
    paid: bool = Field(False, description="Pagado")
    reviewed_by: Optional[str] = Field(None, max_length=255, description="Revisado por")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoice_number": "FAC-001",
                "cufe": "CUFE123456789",
                "provider_name": "Hotel Ejemplo",
                "provider_nit": "900123456-7",
                "client_name": "Cliente Ejemplo",
                "client_nit": "800123456-7",
                "client_address": "Calle 123 #45-67",
                "client_email": "cliente@ejemplo.com",
                "issue_date": "2025-01-15T10:00:00Z",
                "total_amount": 500000.00,
                "paid": False
            }
        }
    )


class InvoiceItemCreateNested(BaseModel):
    """Nested model for creating invoice items within invoice creation."""
    description: str = Field(..., description="Descripción del item")
    unit: Optional[str] = Field(None, max_length=50, description="Unidad")
    quantity: Optional[Decimal] = Field(None, ge=0, description="Cantidad")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Precio unitario")
    subtotal: Optional[Decimal] = Field(None, ge=0, description="Subtotal")
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Tasa de impuesto (%)")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Monto de impuesto")
    total_amount: Decimal = Field(..., ge=0, description="Monto total del item")


class InvoiceCreateWithItemsRequest(BaseModel):
    """Request model for creating an invoice with nested items."""
    
    invoice_number: str = Field(..., max_length=255, description="Número de factura")
    cufe: str = Field(..., max_length=255, description="CUFE")
    provider_name: str = Field(..., max_length=255, description="Nombre del proveedor")
    provider_nit: str = Field(..., max_length=50, description="NIT del proveedor")
    client_name: str = Field(..., max_length=255, description="Nombre del cliente")
    client_nit: str = Field(..., max_length=50, description="NIT del cliente")
    client_address: Optional[str] = Field(None, description="Dirección del cliente")
    client_email: Optional[EmailStr] = Field(None, description="Email del cliente")
    issue_date: datetime = Field(..., description="Fecha de emisión")
    authorization_date: Optional[datetime] = Field(None, description="Fecha de autorización")
    guest_name: Optional[str] = Field(None, max_length=255, description="Nombre del huésped")
    cashier_id: Optional[str] = Field(None, max_length=100, description="ID del cajero")
    arrival_date: Optional[date] = Field(None, description="Fecha de llegada")
    departure_date: Optional[date] = Field(None, description="Fecha de salida")
    reservation_number: Optional[str] = Field(None, max_length=100, description="Número de reserva")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="Monto total (se calculará automáticamente si no se proporciona)")
    payment_method: Optional[str] = Field(None, max_length=100, description="Método de pago")
    payment_terms: Optional[str] = Field(None, description="Términos de pago")
    bank_account: Optional[str] = Field(None, max_length=100, description="Cuenta bancaria")
    additional_info: Optional[str] = Field(None, description="Información adicional")
    loaded_in_liquidation: bool = Field(False, description="Cargado en liquidación")
    paid: bool = Field(False, description="Pagado")
    reviewed_by: Optional[str] = Field(None, max_length=255, description="Revisado por")
    items: List[InvoiceItemCreateNested] = Field(..., min_length=1, description="Items de la factura")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoice_number": "FAC-001",
                "cufe": "CUFE123456789",
                "provider_name": "Hotel Ejemplo",
                "provider_nit": "900123456-7",
                "client_name": "Cliente Ejemplo",
                "client_nit": "800123456-7",
                "issue_date": "2025-01-15T10:00:00Z",
                "items": [
                    {
                        "description": "Habitación estándar",
                        "quantity": 2,
                        "unit_price": 150000.00,
                        "tax_rate": 19,
                        "total_amount": 357000.00
                    }
                ]
            }
        }
    )


class InvoiceUpdateRequest(BaseModel):
    """Request model for updating an invoice."""
    
    invoice_number: Optional[str] = Field(None, max_length=255, description="Número de factura")
    cufe: Optional[str] = Field(None, max_length=255, description="CUFE")
    provider_name: Optional[str] = Field(None, max_length=255, description="Nombre del proveedor")
    provider_nit: Optional[str] = Field(None, max_length=50, description="NIT del proveedor")
    client_name: Optional[str] = Field(None, max_length=255, description="Nombre del cliente")
    client_nit: Optional[str] = Field(None, max_length=50, description="NIT del cliente")
    client_address: Optional[str] = Field(None, description="Dirección del cliente")
    client_email: Optional[EmailStr] = Field(None, description="Email del cliente")
    issue_date: Optional[datetime] = Field(None, description="Fecha de emisión")
    authorization_date: Optional[datetime] = Field(None, description="Fecha de autorización")
    guest_name: Optional[str] = Field(None, max_length=255, description="Nombre del huésped")
    cashier_id: Optional[str] = Field(None, max_length=100, description="ID del cajero")
    arrival_date: Optional[date] = Field(None, description="Fecha de llegada")
    departure_date: Optional[date] = Field(None, description="Fecha de salida")
    reservation_number: Optional[str] = Field(None, max_length=100, description="Número de reserva")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="Monto total")
    payment_method: Optional[str] = Field(None, max_length=100, description="Método de pago")
    payment_terms: Optional[str] = Field(None, description="Términos de pago")
    bank_account: Optional[str] = Field(None, max_length=100, description="Cuenta bancaria")
    additional_info: Optional[str] = Field(None, description="Información adicional")
    loaded_in_liquidation: Optional[bool] = Field(None, description="Cargado en liquidación")
    paid: Optional[bool] = Field(None, description="Pagado")
    reviewed_by: Optional[str] = Field(None, max_length=255, description="Revisado por")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "paid": True,
                "reviewed_by": "admin@example.com"
            }
        }
    )


# ============================================
# PYDANTIC RESPONSE MODELS
# ============================================

class InvoiceResponse(BaseModel):
    """Response model for a single invoice."""
    
    id: int = Field(..., description="ID único")
    invoice_number: str = Field(..., description="Número de factura")
    cufe: str = Field(..., description="CUFE")
    provider_name: str = Field(..., description="Nombre del proveedor")
    provider_nit: str = Field(..., description="NIT del proveedor")
    client_name: str = Field(..., description="Nombre del cliente")
    client_nit: str = Field(..., description="NIT del cliente")
    client_address: Optional[str] = Field(None, description="Dirección del cliente")
    client_email: Optional[str] = Field(None, description="Email del cliente")
    issue_date: datetime = Field(..., description="Fecha de emisión")
    authorization_date: Optional[datetime] = Field(None, description="Fecha de autorización")
    guest_name: Optional[str] = Field(None, description="Nombre del huésped")
    cashier_id: Optional[str] = Field(None, description="ID del cajero")
    arrival_date: Optional[date] = Field(None, description="Fecha de llegada")
    departure_date: Optional[date] = Field(None, description="Fecha de salida")
    reservation_number: Optional[str] = Field(None, description="Número de reserva")
    total_amount: Decimal = Field(..., description="Monto total")
    payment_method: Optional[str] = Field(None, description="Método de pago")
    payment_terms: Optional[str] = Field(None, description="Términos de pago")
    bank_account: Optional[str] = Field(None, description="Cuenta bancaria")
    additional_info: Optional[str] = Field(None, description="Información adicional")
    loaded_in_liquidation: bool = Field(..., description="Cargado en liquidación")
    paid: bool = Field(..., description="Pagado")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")
    reviewed_by: Optional[str] = Field(None, description="Revisado por")
    items: Optional[List] = Field(None, description="Items de la factura (si se incluyen)")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        json_schema_extra={
            "example": {
                "id": 1,
                "invoice_number": "FAC-001",
                "cufe": "CUFE123456789",
                "provider_name": "Hotel Ejemplo",
                "total_amount": 500000.00,
                "paid": False
            }
        }
    )


class InvoiceListResponse(BaseModel):
    """Response model for paginated list of invoices."""
    
    invoices: List[InvoiceResponse] = Field(..., description="Lista de facturas")
    total: int = Field(..., description="Total de facturas")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Elementos por página")
    pages: int = Field(..., description="Total de páginas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "invoices": [
                    {
                        "id": 1,
                        "invoice_number": "FAC-001",
                        "total_amount": 500000.00
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 50,
                "pages": 2
            }
        }
    )


class InvoiceStatsResponse(BaseModel):
    """Response model for invoice statistics."""
    
    total: int = Field(..., description="Total de facturas")
    paid: int = Field(..., description="Facturas pagadas")
    unpaid: int = Field(..., description="Facturas sin pagar")
    loaded_in_liquidation: int = Field(..., description="Facturas cargadas en liquidación")
    total_amount: Decimal = Field(..., description="Monto total de todas las facturas")
    paid_amount: Decimal = Field(..., description="Monto total de facturas pagadas")
    unpaid_amount: Decimal = Field(..., description="Monto total de facturas sin pagar")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150,
                "paid": 120,
                "unpaid": 30,
                "loaded_in_liquidation": 100,
                "total_amount": 75000000.00,
                "paid_amount": 60000000.00,
                "unpaid_amount": 15000000.00
            }
        }
    )


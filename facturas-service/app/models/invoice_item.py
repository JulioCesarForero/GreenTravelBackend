"""
InvoiceItem model demonstrating best practices for SQLAlchemy + Pydantic models.

This module shows:
- SQLAlchemy ORM models with ForeignKey relationships
- Pydantic models for request/response validation
- Model configuration
"""

from sqlalchemy import Column, BigInteger, String, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# Import base from database connection
from app.database.connection import Base


# ============================================
# SQLAlchemy ORM MODEL
# ============================================

class InvoiceItem(Base):
    """
    InvoiceItem entity model.
    
    Maps to the invoice_items table (adapted from PostgreSQL to MySQL).
    Represents an item within an invoice.
    """
    __tablename__ = "invoice_items"

    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign key to invoice
    invoice_id = Column(
        BigInteger, 
        ForeignKey('invoices.id', ondelete='CASCADE'), 
        nullable=False, 
        comment="ID de la factura"
    )
    
    # Item details
    description = Column(String(500), nullable=False, comment="Descripción del item")
    unit = Column(String(50), nullable=True, comment="Unidad de medida")
    quantity = Column(Numeric(19, 4), nullable=True, comment="Cantidad")
    unit_price = Column(Numeric(19, 2), nullable=True, comment="Precio unitario")
    
    # Financial details
    subtotal = Column(Numeric(19, 2), nullable=True, comment="Subtotal")
    tax_rate = Column(Numeric(5, 2), nullable=True, comment="Tasa de impuesto (%)")
    tax_amount = Column(Numeric(19, 2), nullable=True, comment="Monto de impuesto")
    total_amount = Column(Numeric(19, 2), nullable=False, comment="Monto total del item")
    
    # Relationship with invoice
    invoice = relationship("Invoice", back_populates="items")
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_invoice_item_invoice_id', 'invoice_id'),
        Index('idx_invoice_item_description', 'description'),
        {'comment': 'Tabla de items de factura'}
    )

    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, invoice_id={self.invoice_id}, description='{self.description}', total_amount={self.total_amount})>"


# ============================================
# PYDANTIC REQUEST MODELS
# ============================================

class InvoiceItemCreateRequest(BaseModel):
    """Request model for creating an invoice item."""
    
    description: str = Field(..., max_length=500, description="Descripción del item")
    unit: Optional[str] = Field(None, max_length=50, description="Unidad de medida")
    quantity: Optional[Decimal] = Field(None, ge=0, description="Cantidad")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Precio unitario")
    subtotal: Optional[Decimal] = Field(None, ge=0, description="Subtotal (se calculará si no se proporciona)")
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Tasa de impuesto (%)")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Monto de impuesto (se calculará si no se proporciona)")
    total_amount: Decimal = Field(..., ge=0, description="Monto total del item")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Habitación estándar",
                "unit": "noche",
                "quantity": 2,
                "unit_price": 150000.00,
                "tax_rate": 19,
                "total_amount": 357000.00
            }
        }
    )


class InvoiceItemUpdateRequest(BaseModel):
    """Request model for updating an invoice item."""
    
    description: Optional[str] = Field(None, max_length=500, description="Descripción del item")
    unit: Optional[str] = Field(None, max_length=50, description="Unidad de medida")
    quantity: Optional[Decimal] = Field(None, ge=0, description="Cantidad")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Precio unitario")
    subtotal: Optional[Decimal] = Field(None, ge=0, description="Subtotal")
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Tasa de impuesto (%)")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Monto de impuesto")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="Monto total del item")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity": 3,
                "total_amount": 500000.00
            }
        }
    )


# ============================================
# PYDANTIC RESPONSE MODELS
# ============================================

class InvoiceItemResponse(BaseModel):
    """Response model for a single invoice item."""
    
    id: int = Field(..., description="ID único")
    invoice_id: int = Field(..., description="ID de la factura")
    description: str = Field(..., description="Descripción del item")
    unit: Optional[str] = Field(None, description="Unidad de medida")
    quantity: Optional[Decimal] = Field(None, description="Cantidad")
    unit_price: Optional[Decimal] = Field(None, description="Precio unitario")
    subtotal: Optional[Decimal] = Field(None, description="Subtotal")
    tax_rate: Optional[Decimal] = Field(None, description="Tasa de impuesto (%)")
    tax_amount: Optional[Decimal] = Field(None, description="Monto de impuesto")
    total_amount: Decimal = Field(..., description="Monto total del item")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        json_schema_extra={
            "example": {
                "id": 1,
                "invoice_id": 1,
                "description": "Habitación estándar",
                "quantity": 2,
                "unit_price": 150000.00,
                "total_amount": 357000.00
            }
        }
    )


class InvoiceItemListResponse(BaseModel):
    """Response model for list of invoice items."""
    
    items: List[InvoiceItemResponse] = Field(..., description="Lista de items")
    total: int = Field(..., description="Total de items")
    invoice_id: int = Field(..., description="ID de la factura")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "invoice_id": 1,
                        "description": "Habitación estándar",
                        "total_amount": 357000.00
                    }
                ],
                "total": 1,
                "invoice_id": 1
            }
        }
    )


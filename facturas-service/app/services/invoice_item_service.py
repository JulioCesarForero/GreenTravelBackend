"""
InvoiceItem service layer with business logic.

This module demonstrates:
- Service layer pattern (separation of concerns)
- CRUD operations for invoice items
- Automatic recalculation of invoice totals
- Relationship validation
"""

import logging
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.invoice import Invoice
from app.models.invoice_item import (
    InvoiceItem,
    InvoiceItemCreateRequest,
    InvoiceItemUpdateRequest,
    InvoiceItemResponse,
    InvoiceItemListResponse
)
from app.services.invoice_service import InvoiceService

logger = logging.getLogger("uvicorn")


class InvoiceItemService:
    """
    Business logic layer for InvoiceItem entity operations.
    
    This service handles:
    - CRUD operations for invoice items
    - Automatic recalculation of invoice totals
    - Relationship validation
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.invoice_service = InvoiceService(db)

    def _calculate_totals(
        self,
        quantity: Optional[Decimal],
        unit_price: Optional[Decimal],
        subtotal: Optional[Decimal],
        tax_rate: Optional[Decimal],
        tax_amount: Optional[Decimal],
        total_amount: Optional[Decimal]
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calculate subtotal, tax_amount, and total_amount for an item.
        
        Args:
            quantity: Item quantity
            unit_price: Unit price
            subtotal: Provided subtotal (optional)
            tax_rate: Tax rate percentage
            tax_amount: Provided tax amount (optional)
            total_amount: Provided total amount (optional)
            
        Returns:
            tuple: (subtotal, tax_amount, total_amount)
        """
        # Calculate subtotal
        if subtotal is not None:
            calculated_subtotal = subtotal
        elif quantity is not None and unit_price is not None:
            calculated_subtotal = quantity * unit_price
        else:
            calculated_subtotal = Decimal('0')
        
        # Calculate tax_amount
        if tax_amount is not None:
            calculated_tax_amount = tax_amount
        elif tax_rate is not None and calculated_subtotal > 0:
            calculated_tax_amount = calculated_subtotal * (tax_rate / Decimal('100'))
        else:
            calculated_tax_amount = Decimal('0')
        
        # Calculate total_amount
        if total_amount is not None:
            calculated_total = total_amount
        else:
            calculated_total = calculated_subtotal + calculated_tax_amount
        
        return calculated_subtotal, calculated_tax_amount, calculated_total

    def _recalculate_invoice_total(self, invoice_id: int) -> None:
        """
        Recalculate and update invoice total_amount based on items.
        
        Args:
            invoice_id: Invoice ID
        """
        try:
            items = self.db.query(InvoiceItem).filter(
                InvoiceItem.invoice_id == invoice_id
            ).all()
            
            total = sum(item.total_amount for item in items)
            
            # Update invoice total
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if invoice:
                invoice.total_amount = total
                self.db.commit()
                logger.info(f"✅ Recalculated invoice {invoice_id} total: {total}")
        except Exception as e:
            logger.error(f"Error recalculating invoice total: {str(e)}")
            raise

    def get_by_invoice_id(self, invoice_id: int) -> InvoiceItemListResponse:
        """
        Get all items for an invoice.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            InvoiceItemListResponse: List of items
        """
        try:
            # Verify invoice exists
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise ValueError(f"Invoice with id {invoice_id} not found")
            
            items = self.db.query(InvoiceItem).filter(
                InvoiceItem.invoice_id == invoice_id
            ).all()
            
            return InvoiceItemListResponse(
                items=[InvoiceItemResponse.model_validate(item) for item in items],
                total=len(items),
                invoice_id=invoice_id
            )
            
        except Exception as e:
            logger.error(f"Error in get_by_invoice_id({invoice_id}): {str(e)}")
            raise

    def get_by_id(self, item_id: int) -> Optional[InvoiceItemResponse]:
        """
        Get invoice item by ID.
        
        Args:
            item_id: Invoice item ID
            
        Returns:
            InvoiceItemResponse or None if not found
        """
        try:
            item = self.db.query(InvoiceItem).filter(
                InvoiceItem.id == item_id
            ).first()
            
            if item:
                return InvoiceItemResponse.model_validate(item)
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id({item_id}): {str(e)}")
            raise

    def create(self, invoice_id: int, request: InvoiceItemCreateRequest) -> InvoiceItemResponse:
        """
        Create new invoice item.
        
        Args:
            invoice_id: Invoice ID
            request: Invoice item creation data
            
        Returns:
            InvoiceItemResponse: Created item
            
        Raises:
            ValueError: If invoice doesn't exist
        """
        try:
            # Verify invoice exists
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise ValueError(f"Invoice with id {invoice_id} not found")
            
            # Calculate totals
            subtotal, tax_amount, total_amount = self._calculate_totals(
                request.quantity,
                request.unit_price,
                request.subtotal,
                request.tax_rate,
                request.tax_amount,
                request.total_amount
            )
            
            # Create item
            item = InvoiceItem(
                invoice_id=invoice_id,
                description=request.description,
                unit=request.unit,
                quantity=request.quantity,
                unit_price=request.unit_price,
                subtotal=subtotal,
                tax_rate=request.tax_rate,
                tax_amount=tax_amount,
                total_amount=total_amount
            )
            
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            
            # Recalculate invoice total
            self._recalculate_invoice_total(invoice_id)
            
            logger.info(f"✅ Created invoice item {item.id} for invoice {invoice_id}")
            return InvoiceItemResponse.model_validate(item)
            
        except ValueError as e:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice item: {str(e)}")
            raise

    def update(self, item_id: int, request: InvoiceItemUpdateRequest) -> Optional[InvoiceItemResponse]:
        """
        Update existing invoice item.
        
        Args:
            item_id: Invoice item ID to update
            request: Update data
            
        Returns:
            InvoiceItemResponse or None if not found
        """
        try:
            # Find item
            item = self.db.query(InvoiceItem).filter(
                InvoiceItem.id == item_id
            ).first()
            
            if not item:
                return None
            
            # Get current values for calculation
            quantity = request.quantity if request.quantity is not None else item.quantity
            unit_price = request.unit_price if request.unit_price is not None else item.unit_price
            subtotal = request.subtotal if request.subtotal is not None else item.subtotal
            tax_rate = request.tax_rate if request.tax_rate is not None else item.tax_rate
            tax_amount = request.tax_amount if request.tax_amount is not None else item.tax_amount
            total_amount = request.total_amount if request.total_amount is not None else item.total_amount
            
            # Recalculate totals if needed
            if any([
                request.quantity is not None,
                request.unit_price is not None,
                request.subtotal is not None,
                request.tax_rate is not None
            ]):
                subtotal, tax_amount, total_amount = self._calculate_totals(
                    quantity, unit_price, subtotal, tax_rate, tax_amount, total_amount
                )
            
            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(item, field, value)
            
            # Update calculated fields
            item.subtotal = subtotal
            item.tax_amount = tax_amount
            item.total_amount = total_amount
            
            self.db.commit()
            self.db.refresh(item)
            
            # Recalculate invoice total
            self._recalculate_invoice_total(item.invoice_id)
            
            logger.info(f"✅ Updated invoice item {item_id}")
            return InvoiceItemResponse.model_validate(item)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating invoice item {item_id}: {str(e)}")
            raise

    def delete(self, item_id: int) -> bool:
        """
        Delete invoice item.
        
        Args:
            item_id: Invoice item ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            item = self.db.query(InvoiceItem).filter(
                InvoiceItem.id == item_id
            ).first()
            
            if not item:
                return False
            
            invoice_id = item.invoice_id
            
            # Delete item
            self.db.delete(item)
            self.db.commit()
            
            # Recalculate invoice total
            self._recalculate_invoice_total(invoice_id)
            
            logger.info(f"🗑️  Deleted invoice item {item_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting invoice item {item_id}: {str(e)}")
            raise


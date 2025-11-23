"""
Invoice service layer with business logic.

This module demonstrates:
- Service layer pattern (separation of concerns)
- CRUD operations
- Pagination
- Search/filtering
- Error handling
- Transaction management
- Relationship handling with invoice items
"""

import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from app.models.invoice import (
    Invoice,
    InvoiceCreateRequest,
    InvoiceUpdateRequest,
    InvoiceCreateWithItemsRequest,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceStatsResponse,
    InvoiceItemCreateNested
)
from app.models.invoice_item import InvoiceItem

logger = logging.getLogger("uvicorn")


class InvoiceService:
    """
    Business logic layer for Invoice entity operations.
    
    This service handles:
    - CRUD operations
    - Business rules validation
    - Data transformation
    - Transaction management
    - Invoice items relationship
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def _calculate_item_totals(self, item: InvoiceItemCreateNested) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calculate subtotal, tax_amount, and total_amount for an item.
        
        Args:
            item: Invoice item data
            
        Returns:
            tuple: (subtotal, tax_amount, total_amount)
        """
        # Calculate subtotal
        if item.subtotal is not None:
            subtotal = item.subtotal
        elif item.quantity is not None and item.unit_price is not None:
            subtotal = item.quantity * item.unit_price
        else:
            subtotal = Decimal('0')
        
        # Calculate tax_amount
        if item.tax_amount is not None:
            tax_amount = item.tax_amount
        elif item.tax_rate is not None and subtotal > 0:
            tax_amount = subtotal * (item.tax_rate / Decimal('100'))
        else:
            tax_amount = Decimal('0')
        
        # Calculate total_amount
        if item.total_amount is not None:
            total_amount = item.total_amount
        else:
            total_amount = subtotal + tax_amount
        
        return subtotal, tax_amount, total_amount

    def _recalculate_invoice_total(self, invoice_id: int) -> Decimal:
        """
        Recalculate total_amount of an invoice based on its items.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Decimal: New total amount
        """
        items = self.db.query(InvoiceItem).filter(
            InvoiceItem.invoice_id == invoice_id
        ).all()
        
        total = sum(item.total_amount for item in items)
        
        # Update invoice total
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.total_amount = total
            self.db.commit()
        
        return total

    def get_all(
        self,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        paid: Optional[bool] = None,
        loaded_in_liquidation: Optional[bool] = None,
        provider_nit: Optional[str] = None,
        client_nit: Optional[str] = None,
        reservation_number: Optional[str] = None,
        issue_date_from: Optional[datetime] = None,
        issue_date_to: Optional[datetime] = None
    ) -> InvoiceListResponse:
        """
        Get paginated list of invoices with filtering.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for invoice_number, provider_name, client_name
            paid: Filter by paid status
            loaded_in_liquidation: Filter by loaded_in_liquidation status
            provider_nit: Filter by provider NIT
            client_nit: Filter by client NIT
            reservation_number: Filter by reservation number
            issue_date_from: Filter by issue date from
            issue_date_to: Filter by issue date to
            
        Returns:
            InvoiceListResponse: Paginated list with metadata
        """
        try:
            # Base query
            query = self.db.query(Invoice)
            
            # Apply paid filter
            if paid is not None:
                query = query.filter(Invoice.paid == paid)
            
            # Apply loaded_in_liquidation filter
            if loaded_in_liquidation is not None:
                query = query.filter(Invoice.loaded_in_liquidation == loaded_in_liquidation)
            
            # Apply provider_nit filter
            if provider_nit:
                query = query.filter(Invoice.provider_nit == provider_nit)
            
            # Apply client_nit filter
            if client_nit:
                query = query.filter(Invoice.client_nit == client_nit)
            
            # Apply reservation_number filter
            if reservation_number:
                query = query.filter(Invoice.reservation_number == reservation_number)
            
            # Apply date range filters
            if issue_date_from:
                query = query.filter(Invoice.issue_date >= issue_date_from)
            if issue_date_to:
                query = query.filter(Invoice.issue_date <= issue_date_to)
            
            # Apply search filter
            if search:
                search_pattern = f"%{search}%"
                # Use LIKE for MySQL compatibility (case-insensitive search)
                query = query.filter(
                    or_(
                        Invoice.invoice_number.like(search_pattern),
                        Invoice.provider_name.like(search_pattern),
                        Invoice.client_name.like(search_pattern),
                        Invoice.cufe.like(search_pattern)
                    )
                )
            
            # Count total
            total = query.count()
            
            # Calculate pages
            pages = (total + limit - 1) // limit if total > 0 else 0
            
            # Apply pagination and ordering
            offset = (page - 1) * limit
            invoices = query.order_by(desc(Invoice.issue_date)).offset(offset).limit(limit).all()
            
            return InvoiceListResponse(
                invoices=[InvoiceResponse.model_validate(inv) for inv in invoices],
                total=total,
                page=page,
                limit=limit,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            raise

    def get_by_id(self, invoice_id: int, include_items: bool = True) -> Optional[InvoiceResponse]:
        """
        Get invoice by ID.
        
        Args:
            invoice_id: Invoice ID
            include_items: Whether to include invoice items in response
            
        Returns:
            InvoiceResponse or None if not found
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            if invoice:
                response = InvoiceResponse.model_validate(invoice)
                if include_items:
                    # Load items
                    from app.models.invoice_item import InvoiceItemResponse
                    items = self.db.query(InvoiceItem).filter(
                        InvoiceItem.invoice_id == invoice_id
                    ).all()
                    response.items = [InvoiceItemResponse.model_validate(item) for item in items]
                return response
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id({invoice_id}): {str(e)}")
            raise

    def create(self, request: InvoiceCreateRequest) -> InvoiceResponse:
        """
        Create new invoice (without items).
        
        Args:
            request: Invoice creation data
            
        Returns:
            InvoiceResponse: Created invoice
        """
        try:
            # Validate dates
            if request.departure_date and request.arrival_date:
                if request.departure_date < request.arrival_date:
                    raise ValueError("departure_date must be >= arrival_date")
            
            # Create new invoice
            invoice = Invoice(
                invoice_number=request.invoice_number,
                cufe=request.cufe,
                provider_name=request.provider_name,
                provider_nit=request.provider_nit,
                client_name=request.client_name,
                client_nit=request.client_nit,
                client_address=request.client_address,
                client_email=request.client_email,
                issue_date=request.issue_date,
                authorization_date=request.authorization_date,
                guest_name=request.guest_name,
                cashier_id=request.cashier_id,
                arrival_date=request.arrival_date,
                departure_date=request.departure_date,
                reservation_number=request.reservation_number,
                total_amount=request.total_amount,
                payment_method=request.payment_method,
                payment_terms=request.payment_terms,
                bank_account=request.bank_account,
                additional_info=request.additional_info,
                loaded_in_liquidation=request.loaded_in_liquidation,
                paid=request.paid,
                reviewed_by=request.reviewed_by
            )
            
            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)
            
            logger.info(f"✅ Created invoice {invoice.id}")
            return InvoiceResponse.model_validate(invoice)
            
        except ValueError as e:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice: {str(e)}")
            raise

    def create_with_items(self, request: InvoiceCreateWithItemsRequest) -> InvoiceResponse:
        """
        Create new invoice with nested items.
        
        Args:
            request: Invoice creation data with items
            
        Returns:
            InvoiceResponse: Created invoice with items
            
        Raises:
            ValueError: If total_amount doesn't match sum of items
        """
        try:
            # Validate dates
            if request.departure_date and request.arrival_date:
                if request.departure_date < request.arrival_date:
                    raise ValueError("departure_date must be >= arrival_date")
            
            # Calculate total from items
            items_total = Decimal('0')
            for item in request.items:
                _, _, item_total = self._calculate_item_totals(item)
                items_total += item_total
            
            # Use provided total_amount or calculate from items
            if request.total_amount is not None:
                total_amount = request.total_amount
                # Validate that provided total matches calculated total (allow small difference for rounding)
                if abs(total_amount - items_total) > Decimal('0.01'):
                    raise ValueError(f"total_amount ({total_amount}) doesn't match sum of items ({items_total})")
            else:
                total_amount = items_total
            
            # Create invoice
            invoice = Invoice(
                invoice_number=request.invoice_number,
                cufe=request.cufe,
                provider_name=request.provider_name,
                provider_nit=request.provider_nit,
                client_name=request.client_name,
                client_nit=request.client_nit,
                client_address=request.client_address,
                client_email=request.client_email,
                issue_date=request.issue_date,
                authorization_date=request.authorization_date,
                guest_name=request.guest_name,
                cashier_id=request.cashier_id,
                arrival_date=request.arrival_date,
                departure_date=request.departure_date,
                reservation_number=request.reservation_number,
                total_amount=total_amount,
                payment_method=request.payment_method,
                payment_terms=request.payment_terms,
                bank_account=request.bank_account,
                additional_info=request.additional_info,
                loaded_in_liquidation=request.loaded_in_liquidation,
                paid=request.paid,
                reviewed_by=request.reviewed_by
            )
            
            self.db.add(invoice)
            self.db.flush()  # Get invoice.id without committing
            
            # Create items
            for item_data in request.items:
                subtotal, tax_amount, item_total = self._calculate_item_totals(item_data)
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data.description,
                    unit=item_data.unit,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    subtotal=subtotal,
                    tax_rate=item_data.tax_rate,
                    tax_amount=tax_amount,
                    total_amount=item_total
                )
                self.db.add(item)
            
            self.db.commit()
            self.db.refresh(invoice)
            
            logger.info(f"✅ Created invoice {invoice.id} with {len(request.items)} items")
            
            # Return invoice with items
            response = InvoiceResponse.model_validate(invoice)
            from app.models.invoice_item import InvoiceItemResponse
            items = self.db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
            response.items = [InvoiceItemResponse.model_validate(item) for item in items]
            return response
            
        except ValueError as e:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice with items: {str(e)}")
            raise

    def update(self, invoice_id: int, request: InvoiceUpdateRequest) -> Optional[InvoiceResponse]:
        """
        Update existing invoice.
        
        Args:
            invoice_id: Invoice ID to update
            request: Update data
            
        Returns:
            InvoiceResponse or None if not found
            
        Raises:
            ValueError: If dates are invalid
        """
        try:
            # Find invoice
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            if not invoice:
                return None
            
            # Validate dates
            arrival_date = request.arrival_date if request.arrival_date else invoice.arrival_date
            departure_date = request.departure_date if request.departure_date else invoice.departure_date
            if departure_date and arrival_date:
                if departure_date < arrival_date:
                    raise ValueError("departure_date must be >= arrival_date")
            
            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(invoice, field, value)
            
            self.db.commit()
            self.db.refresh(invoice)
            
            logger.info(f"✅ Updated invoice {invoice_id}")
            return InvoiceResponse.model_validate(invoice)
            
        except ValueError as e:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
            raise

    def delete(self, invoice_id: int) -> bool:
        """
        Delete invoice (hard delete - will cascade delete items).
        
        Args:
            invoice_id: Invoice ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.id == invoice_id
            ).first()
            
            if not invoice:
                return False
            
            # Hard delete (items will be deleted by CASCADE)
            self.db.delete(invoice)
            self.db.commit()
            
            logger.info(f"🗑️  Deleted invoice {invoice_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting invoice {invoice_id}: {str(e)}")
            raise

    def get_stats(self) -> InvoiceStatsResponse:
        """
        Get statistics about invoices.
        
        Returns:
            InvoiceStatsResponse: Statistics data
        """
        try:
            # Total count
            total = self.db.query(Invoice).count()
            
            # Paid/unpaid count
            paid = self.db.query(Invoice).filter(Invoice.paid == True).count()
            unpaid = self.db.query(Invoice).filter(Invoice.paid == False).count()
            
            # Loaded in liquidation count
            loaded_in_liquidation = self.db.query(Invoice).filter(
                Invoice.loaded_in_liquidation == True
            ).count()
            
            # Total amounts
            total_amount_result = self.db.query(func.sum(Invoice.total_amount)).scalar() or Decimal('0')
            paid_amount_result = self.db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.paid == True
            ).scalar() or Decimal('0')
            unpaid_amount_result = self.db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.paid == False
            ).scalar() or Decimal('0')
            
            return InvoiceStatsResponse(
                total=total,
                paid=paid,
                unpaid=unpaid,
                loaded_in_liquidation=loaded_in_liquidation,
                total_amount=total_amount_result,
                paid_amount=paid_amount_result,
                unpaid_amount=unpaid_amount_result
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise


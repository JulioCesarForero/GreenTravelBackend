"""
Routes package for facturas service.
"""

from app.routes.invoice import router as invoice_router
from app.routes.invoice_item import router as invoice_item_router

__all__ = ["invoice_router", "invoice_item_router"]


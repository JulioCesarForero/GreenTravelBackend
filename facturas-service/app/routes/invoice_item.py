"""
InvoiceItem routes module with FastAPI endpoints.

This module demonstrates:
- RESTful API design for nested resources
- Proper HTTP methods and status codes
- Request/response validation
- Error handling
- Documentation with OpenAPI
- Dependency injection
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.invoice_item_service import InvoiceItemService
from app.models.invoice_item import (
    InvoiceItemCreateRequest,
    InvoiceItemUpdateRequest,
    InvoiceItemResponse,
    InvoiceItemListResponse
)

logger = logging.getLogger("uvicorn")

# Create router
router = APIRouter()


# ============================================
# LIST INVOICE ITEMS BY INVOICE ID
# ============================================

@router.get(
    "/invoices/{invoice_id}/items",
    response_model=InvoiceItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar items de una factura",
    description="Obtener todos los items asociados a una factura específica",
    responses={
        200: {"description": "Items encontrados"},
        404: {"description": "Factura no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_invoice_items(
    invoice_id: int = Path(..., ge=1, description="Identificador único de la factura"),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los items de una factura.
    
    **Parámetros de ruta:**
    - **invoice_id**: Identificador único de la factura
    
    **Retorna:**
    - Lista de items de la factura
    
    **Errores:**
    - **404**: Factura no encontrada
    """
    try:
        service = InvoiceItemService(db)
        result = service.get_by_invoice_id(invoice_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in get_invoice_items({invoice_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener items"
        )


# ============================================
# GET SINGLE INVOICE ITEM
# ============================================

@router.get(
    "/invoice-items/{item_id}",
    response_model=InvoiceItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener item por ID",
    description="Obtener un item específico por su identificador único",
    responses={
        200: {"description": "Item encontrado"},
        404: {"description": "Item no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_invoice_item(
    item_id: int = Path(..., ge=1, description="Identificador único del item"),
    db: Session = Depends(get_db)
):
    """
    Obtener un item específico por ID.
    
    **Parámetros de ruta:**
    - **item_id**: Identificador único del item
    
    **Retorna:**
    - Detalles del item
    
    **Errores:**
    - **404**: Item no encontrado
    """
    try:
        service = InvoiceItemService(db)
        item = service.get_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item con id {item_id} no encontrado"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_invoice_item({item_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener item"
        )


# ============================================
# CREATE INVOICE ITEM
# ============================================

@router.post(
    "/invoices/{invoice_id}/items",
    response_model=InvoiceItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear item para una factura",
    description="Crear un nuevo item para una factura específica. El total de la factura se recalculará automáticamente",
    responses={
        201: {"description": "Item creado exitosamente"},
        400: {"description": "Datos de solicitud inválidos"},
        404: {"description": "Factura no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_invoice_item(
    invoice_id: int = Path(..., ge=1, description="Identificador único de la factura"),
    request: InvoiceItemCreateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo item para una factura.
    
    **Parámetros de ruta:**
    - **invoice_id**: Identificador único de la factura
    
    **Cuerpo de la solicitud:**
    - Todos los campos del item (ver modelo)
    
    **Cálculos automáticos:**
    - Si no se proporcionan `subtotal`, `tax_amount` o `total_amount`, se calcularán automáticamente
    - El `total_amount` de la factura se recalculará automáticamente
    
    **Retorna:**
    - Item creado con ID generado
    """
    try:
        service = InvoiceItemService(db)
        item = service.create(invoice_id, request)
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in create_invoice_item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear item"
        )


# ============================================
# UPDATE INVOICE ITEM
# ============================================

@router.put(
    "/invoice-items/{item_id}",
    response_model=InvoiceItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar item",
    description="Actualizar un item existente. El total de la factura se recalculará automáticamente",
    responses={
        200: {"description": "Item actualizado exitosamente"},
        404: {"description": "Item no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_invoice_item(
    item_id: int = Path(..., ge=1, description="Identificador único del item"),
    request: InvoiceItemUpdateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Actualizar un item existente.
    
    **Parámetros de ruta:**
    - **item_id**: Identificador único del item a actualizar
    
    **Cuerpo de la solicitud:**
    - Todos los campos son opcionales
    - Solo los campos proporcionados serán actualizados
    
    **Cálculos automáticos:**
    - Si se actualizan `quantity`, `unit_price`, `subtotal` o `tax_rate`, se recalcularán los totales
    - El `total_amount` de la factura se recalculará automáticamente
    
    **Retorna:**
    - Datos actualizados del item
    
    **Errores:**
    - **404**: Item no encontrado
    """
    try:
        service = InvoiceItemService(db)
        item = service.update(item_id, request)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item con id {item_id} no encontrado"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_invoice_item({item_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar item"
        )


# ============================================
# DELETE INVOICE ITEM
# ============================================

@router.delete(
    "/invoice-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar item",
    description="Eliminar un item. El total de la factura se recalculará automáticamente",
    responses={
        204: {"description": "Item eliminado exitosamente"},
        404: {"description": "Item no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_invoice_item(
    item_id: int = Path(..., ge=1, description="Identificador único del item"),
    db: Session = Depends(get_db)
):
    """
    Eliminar un item.
    
    **Parámetros de ruta:**
    - **item_id**: Identificador único del item a eliminar
    
    **Nota:**
    - El `total_amount` de la factura se recalculará automáticamente después de eliminar el item
    
    **Errores:**
    - **404**: Item no encontrado
    """
    try:
        service = InvoiceItemService(db)
        deleted = service.delete(item_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item con id {item_id} no encontrado"
            )
        
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_invoice_item({item_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar item"
        )


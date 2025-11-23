"""
Invoice routes module with FastAPI endpoints.

This module demonstrates:
- RESTful API design
- Proper HTTP methods and status codes
- Request/response validation
- Error handling
- Documentation with OpenAPI
- Dependency injection
- Nested resource creation
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.invoice_service import InvoiceService
from app.models.invoice import (
    InvoiceCreateRequest,
    InvoiceUpdateRequest,
    InvoiceCreateWithItemsRequest,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceStatsResponse
)

logger = logging.getLogger("uvicorn")

# Create router
router = APIRouter()


# ============================================
# LIST INVOICES (with pagination & filtering)
# ============================================

@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar todas las facturas",
    description="Obtener lista paginada de facturas con filtros opcionales",
    response_description="Lista paginada de facturas con metadatos"
)
async def get_invoices(
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    limit: int = Query(50, ge=1, le=100, description="Elementos por página (máximo 100)"),
    search: Optional[str] = Query(None, description="Búsqueda en número de factura, proveedor, cliente, CUFE"),
    paid: Optional[bool] = Query(None, description="Filtrar por estado de pago"),
    loaded_in_liquidation: Optional[bool] = Query(None, description="Filtrar por cargado en liquidación"),
    provider_nit: Optional[str] = Query(None, description="Filtrar por NIT del proveedor"),
    client_nit: Optional[str] = Query(None, description="Filtrar por NIT del cliente"),
    reservation_number: Optional[str] = Query(None, description="Filtrar por número de reserva"),
    issue_date_from: Optional[datetime] = Query(None, description="Filtrar desde fecha de emisión"),
    issue_date_to: Optional[datetime] = Query(None, description="Filtrar hasta fecha de emisión"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de facturas.
    
    **Parámetros de consulta:**
    - **page**: Número de página (inicia en 1)
    - **limit**: Número de elementos por página (1-100)
    - **search**: Término de búsqueda opcional
    - **paid**: Filtro por estado de pago
    - **loaded_in_liquidation**: Filtro por cargado en liquidación
    - **provider_nit**: Filtro por NIT del proveedor
    - **client_nit**: Filtro por NIT del cliente
    - **reservation_number**: Filtro por número de reserva
    - **issue_date_from**: Filtro desde fecha de emisión
    - **issue_date_to**: Filtro hasta fecha de emisión
    
    **Retorna:**
    - Lista de facturas con metadatos de paginación
    """
    try:
        service = InvoiceService(db)
        result = service.get_all(
            page=page,
            limit=limit,
            search=search,
            paid=paid,
            loaded_in_liquidation=loaded_in_liquidation,
            provider_nit=provider_nit,
            client_nit=client_nit,
            reservation_number=reservation_number,
            issue_date_from=issue_date_from,
            issue_date_to=issue_date_to
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener facturas"
        )


# ============================================
# GET SINGLE INVOICE
# ============================================

@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener factura por ID",
    description="Obtener una factura específica por su identificador único (incluye items)",
    responses={
        200: {"description": "Factura encontrada"},
        404: {"description": "Factura no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_invoice(
    invoice_id: int = Path(..., ge=1, description="Identificador único de la factura"),
    include_items: bool = Query(True, description="Incluir items de la factura"),
    db: Session = Depends(get_db)
):
    """
    Obtener una factura específica por ID.
    
    **Parámetros de ruta:**
    - **invoice_id**: Identificador único de la factura
    
    **Parámetros de consulta:**
    - **include_items**: Incluir items de la factura en la respuesta (default: true)
    
    **Retorna:**
    - Detalles de la factura (con items si include_items=true)
    
    **Errores:**
    - **404**: Factura no encontrada
    """
    try:
        service = InvoiceService(db)
        invoice = service.get_by_id(invoice_id, include_items=include_items)
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factura con id {invoice_id} no encontrada"
            )
        
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_invoice({invoice_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener factura"
        )


# ============================================
# CREATE INVOICE (without items)
# ============================================

@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva factura",
    description="Crear una nueva factura sin items",
    responses={
        201: {"description": "Factura creada exitosamente"},
        400: {"description": "Datos de solicitud inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_invoice(
    request: InvoiceCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva factura (sin items).
    
    **Cuerpo de la solicitud:**
    - Todos los campos de la factura (ver modelo)
    
    **Retorna:**
    - Factura creada con ID generado
    
    **Nota:**
    - Para crear factura con items, usar el endpoint `/invoices/with-items`
    """
    try:
        service = InvoiceService(db)
        invoice = service.create(request)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in create_invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear factura"
        )


# ============================================
# CREATE INVOICE WITH ITEMS
# ============================================

@router.post(
    "/invoices/with-items",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear factura con items",
    description="Crear una nueva factura con items anidados. El total se calculará automáticamente si no se proporciona",
    responses={
        201: {"description": "Factura creada exitosamente con items"},
        400: {"description": "Datos de solicitud inválidos o total no coincide con items"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_invoice_with_items(
    request: InvoiceCreateWithItemsRequest,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva factura con items anidados.
    
    **Cuerpo de la solicitud:**
    - Todos los campos de la factura
    - **items**: Lista de items de la factura (mínimo 1)
    
    **Cálculos automáticos:**
    - Si `total_amount` no se proporciona, se calculará sumando los totales de los items
    - Si se proporciona `total_amount`, debe coincidir con la suma de items (tolerancia 0.01)
    - Los items calcularán automáticamente `subtotal`, `tax_amount` y `total_amount` si no se proporcionan
    
    **Retorna:**
    - Factura creada con items incluidos
    """
    try:
        service = InvoiceService(db)
        invoice = service.create_with_items(request)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in create_invoice_with_items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear factura con items"
        )


# ============================================
# UPDATE INVOICE
# ============================================

@router.put(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar factura",
    description="Actualizar una factura existente con nuevos datos",
    responses={
        200: {"description": "Factura actualizada exitosamente"},
        400: {"description": "Datos de solicitud inválidos"},
        404: {"description": "Factura no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_invoice(
    invoice_id: int = Path(..., ge=1, description="Identificador único de la factura"),
    request: InvoiceUpdateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Actualizar una factura existente.
    
    **Parámetros de ruta:**
    - **invoice_id**: Identificador único de la factura a actualizar
    
    **Cuerpo de la solicitud:**
    - Todos los campos son opcionales
    - Solo los campos proporcionados serán actualizados
    
    **Retorna:**
    - Datos actualizados de la factura
    
    **Errores:**
    - **404**: Factura no encontrada
    - **400**: Datos inválidos (ej: departure_date < arrival_date)
    """
    try:
        service = InvoiceService(db)
        invoice = service.update(invoice_id, request)
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factura con id {invoice_id} no encontrada"
            )
        
        return invoice
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in update_invoice({invoice_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar factura"
        )


# ============================================
# DELETE INVOICE
# ============================================

@router.delete(
    "/invoices/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar factura",
    description="Eliminar una factura (hard delete - también elimina sus items)",
    responses={
        204: {"description": "Factura eliminada exitosamente"},
        404: {"description": "Factura no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_invoice(
    invoice_id: int = Path(..., ge=1, description="Identificador único de la factura"),
    db: Session = Depends(get_db)
):
    """
    Eliminar una factura (hard delete).
    
    **Parámetros de ruta:**
    - **invoice_id**: Identificador único de la factura a eliminar
    
    **Nota:**
    - Esto realiza un hard delete (elimina permanentemente)
    - Los items asociados se eliminarán automáticamente (CASCADE)
    
    **Errores:**
    - **404**: Factura no encontrada
    """
    try:
        service = InvoiceService(db)
        deleted = service.delete(invoice_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factura con id {invoice_id} no encontrada"
            )
        
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_invoice({invoice_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar factura"
        )


# ============================================
# GET STATISTICS
# ============================================

@router.get(
    "/invoices/stats",
    response_model=InvoiceStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de facturas",
    description="Obtener estadísticas agregadas sobre las facturas",
    response_description="Estadísticas incluyendo conteos y montos totales"
)
async def get_invoice_stats(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas sobre facturas.
    
    **Retorna:**
    - Conteo total
    - Conteos pagadas/sin pagar
    - Conteo cargadas en liquidación
    - Montos totales (total, pagado, sin pagar)
    """
    try:
        service = InvoiceService(db)
        stats = service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_invoice_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener estadísticas"
        )


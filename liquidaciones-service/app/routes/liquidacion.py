"""
Liquidacion routes module with FastAPI endpoints.

This module demonstrates:
- RESTful API design
- Proper HTTP methods and status codes
- Request/response validation
- Error handling
- Documentation with OpenAPI
- Dependency injection
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.liquidacion_service import LiquidacionService
from app.models.liquidacion import (
    LiquidacionCreateRequest,
    LiquidacionUpdateRequest,
    LiquidacionResponse,
    LiquidacionListResponse,
    LiquidacionStatsResponse
)

logger = logging.getLogger("uvicorn")

# Create router
router = APIRouter()


# ============================================
# LIST LIQUIDACIONES (with pagination & filtering)
# ============================================

@router.get(
    "/liquidaciones",
    response_model=LiquidacionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar todas las liquidaciones",
    description="Obtener lista paginada de liquidaciones con filtros opcionales",
    response_description="Lista paginada de liquidaciones con metadatos"
)
async def get_liquidaciones(
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    limit: int = Query(50, ge=1, le=100, description="Elementos por página (máximo 100)"),
    search: Optional[str] = Query(None, description="Búsqueda en nombre empresa, pasajero, asesor"),
    estado: Optional[int] = Query(None, ge=0, le=1, description="Filtrar por estado (1=activo, 0=inactivo)"),
    id_reserva: Optional[int] = Query(None, description="Filtrar por ID de reserva"),
    factura: Optional[int] = Query(None, description="Filtrar por número de factura"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de liquidaciones.
    
    **Parámetros de consulta:**
    - **page**: Número de página (inicia en 1)
    - **limit**: Número de elementos por página (1-100)
    - **search**: Término de búsqueda opcional
    - **estado**: Filtro por estado (1=activo, 0=inactivo)
    - **id_reserva**: Filtro por ID de reserva
    - **factura**: Filtro por número de factura
    
    **Retorna:**
    - Lista de liquidaciones con metadatos de paginación
    """
    try:
        service = LiquidacionService(db)
        result = service.get_all(
            page=page,
            limit=limit,
            search=search,
            estado=estado,
            id_reserva=id_reserva,
            factura=factura
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_liquidaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener liquidaciones"
        )


# ============================================
# GET STATISTICS (debe ir ANTES de la ruta con parámetro)
# ============================================

@router.get(
    "/liquidaciones/stats",
    response_model=LiquidacionStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de liquidaciones",
    description="Obtener estadísticas agregadas sobre las liquidaciones",
    response_description="Estadísticas incluyendo conteos por estado"
)
async def get_liquidacion_stats(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas sobre liquidaciones.
    
    **Retorna:**
    - Conteo total
    - Conteos activas/inactivas
    - Conteos por estado
    """
    try:
        service = LiquidacionService(db)
        stats = service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_liquidacion_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener estadísticas"
        )


# ============================================
# GET SINGLE LIQUIDACION
# ============================================

@router.get(
    "/liquidaciones/{liquidacion_id}",
    response_model=LiquidacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener liquidación por ID",
    description="Obtener una liquidación específica por su identificador único",
    responses={
        200: {"description": "Liquidación encontrada"},
        404: {"description": "Liquidación no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_liquidacion(
    liquidacion_id: int = Path(..., ge=1, description="Identificador único de la liquidación"),
    db: Session = Depends(get_db)
):
    """
    Obtener una liquidación específica por ID.
    
    **Parámetros de ruta:**
    - **liquidacion_id**: Identificador único de la liquidación
    
    **Retorna:**
    - Detalles de la liquidación
    
    **Errores:**
    - **404**: Liquidación no encontrada
    """
    try:
        service = LiquidacionService(db)
        liquidacion = service.get_by_id(liquidacion_id)
        
        if not liquidacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Liquidación con id {liquidacion_id} no encontrada"
            )
        
        return liquidacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_liquidacion({liquidacion_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener liquidación"
        )


# ============================================
# CREATE LIQUIDACION
# ============================================

@router.post(
    "/liquidaciones",
    response_model=LiquidacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva liquidación",
    description="Crear una nueva liquidación con los datos proporcionados",
    responses={
        201: {"description": "Liquidación creada exitosamente"},
        400: {"description": "Datos de solicitud inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_liquidacion(
    request: LiquidacionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva liquidación.
    
    **Cuerpo de la solicitud:**
    - Todos los campos de la liquidación (ver modelo)
    
    **Retorna:**
    - Liquidación creada con ID generado
    """
    try:
        service = LiquidacionService(db)
        liquidacion = service.create(request)
        return liquidacion
    except Exception as e:
        logger.error(f"Error in create_liquidacion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear liquidación"
        )


# ============================================
# UPDATE LIQUIDACION
# ============================================

@router.put(
    "/liquidaciones/{liquidacion_id}",
    response_model=LiquidacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar liquidación",
    description="Actualizar una liquidación existente con nuevos datos",
    responses={
        200: {"description": "Liquidación actualizada exitosamente"},
        404: {"description": "Liquidación no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_liquidacion(
    liquidacion_id: int = Path(..., ge=1, description="Identificador único de la liquidación"),
    request: LiquidacionUpdateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Actualizar una liquidación existente.
    
    **Parámetros de ruta:**
    - **liquidacion_id**: Identificador único de la liquidación a actualizar
    
    **Cuerpo de la solicitud:**
    - Todos los campos son opcionales
    - Solo los campos proporcionados serán actualizados
    
    **Retorna:**
    - Datos actualizados de la liquidación
    
    **Errores:**
    - **404**: Liquidación no encontrada
    """
    try:
        service = LiquidacionService(db)
        liquidacion = service.update(liquidacion_id, request)
        
        if not liquidacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Liquidación con id {liquidacion_id} no encontrada"
            )
        
        return liquidacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_liquidacion({liquidacion_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar liquidación"
        )


# ============================================
# DELETE LIQUIDACION
# ============================================

@router.delete(
    "/liquidaciones/{liquidacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar liquidación",
    description="Eliminar una liquidación (soft delete - marca como inactiva)",
    responses={
        204: {"description": "Liquidación eliminada exitosamente"},
        404: {"description": "Liquidación no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_liquidacion(
    liquidacion_id: int = Path(..., ge=1, description="Identificador único de la liquidación"),
    db: Session = Depends(get_db)
):
    """
    Eliminar una liquidación (soft delete).
    
    **Parámetros de ruta:**
    - **liquidacion_id**: Identificador único de la liquidación a eliminar
    
    **Nota:**
    - Esto realiza un soft delete (marca estado=0)
    - El registro permanece en la base de datos
    
    **Errores:**
    - **404**: Liquidación no encontrada
    """
    try:
        service = LiquidacionService(db)
        deleted = service.delete(liquidacion_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Liquidación con id {liquidacion_id} no encontrada"
            )
        
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_liquidacion({liquidacion_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar liquidación"
        )


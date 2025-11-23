"""
Provedor routes module with FastAPI endpoints.

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
from app.services.provedor_service import ProvedorService
from app.models.provedor import (
    ProvedorCreateRequest,
    ProvedorUpdateRequest,
    ProvedorResponse,
    ProvedorListResponse,
    ProvedorStatsResponse
)

logger = logging.getLogger("uvicorn")

# Create router
router = APIRouter()


# ============================================
# LIST PROVEDORES (with pagination & filtering)
# ============================================

@router.get(
    "/provedores",
    response_model=ProvedorListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los proveedores",
    description="Obtener lista paginada de proveedores con filtros opcionales",
    response_description="Lista paginada de proveedores con metadatos"
)
async def get_provedores(
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    limit: int = Query(50, ge=1, le=100, description="Elementos por página (máximo 100)"),
    search: Optional[str] = Query(None, description="Búsqueda en nombre, razón social, identificación"),
    estado: Optional[int] = Query(None, ge=0, le=1, description="Filtrar por estado (1=activo, 0=inactivo)"),
    tipo: Optional[int] = Query(None, description="Filtrar por tipo de proveedor"),
    ciudad: Optional[int] = Query(None, description="Filtrar por ID de ciudad"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de proveedores.
    
    **Parámetros de consulta:**
    - **page**: Número de página (inicia en 1)
    - **limit**: Número de elementos por página (1-100)
    - **search**: Término de búsqueda opcional
    - **estado**: Filtro por estado (1=activo, 0=inactivo)
    - **tipo**: Filtro por tipo de proveedor
    - **ciudad**: Filtro por ID de ciudad
    
    **Retorna:**
    - Lista de proveedores con metadatos de paginación
    """
    try:
        service = ProvedorService(db)
        result = service.get_all(
            page=page,
            limit=limit,
            search=search,
            estado=estado,
            tipo=tipo,
            ciudad=ciudad
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_provedores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener proveedores"
        )


# ============================================
# GET SINGLE PROVEDOR
# ============================================

@router.get(
    "/provedores/{provedor_id}",
    response_model=ProvedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener proveedor por ID",
    description="Obtener un proveedor específico por su identificador único",
    responses={
        200: {"description": "Proveedor encontrado"},
        404: {"description": "Proveedor no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_provedor(
    provedor_id: int = Path(..., ge=1, description="Identificador único del proveedor"),
    db: Session = Depends(get_db)
):
    """
    Obtener un proveedor específico por ID.
    
    **Parámetros de ruta:**
    - **provedor_id**: Identificador único del proveedor
    
    **Retorna:**
    - Detalles del proveedor
    
    **Errores:**
    - **404**: Proveedor no encontrado
    """
    try:
        service = ProvedorService(db)
        provedor = service.get_by_id(provedor_id)
        
        if not provedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con id {provedor_id} no encontrado"
            )
        
        return provedor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_provedor({provedor_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener proveedor"
        )


# ============================================
# CREATE PROVEDOR
# ============================================

@router.post(
    "/provedores",
    response_model=ProvedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo proveedor",
    description="Crear un nuevo proveedor con los datos proporcionados",
    responses={
        201: {"description": "Proveedor creado exitosamente"},
        400: {"description": "Datos de solicitud inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_provedor(
    request: ProvedorCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo proveedor.
    
    **Cuerpo de la solicitud:**
    - Todos los campos del proveedor (ver modelo)
    
    **Retorna:**
    - Proveedor creado con ID generado
    """
    try:
        service = ProvedorService(db)
        provedor = service.create(request)
        return provedor
    except Exception as e:
        logger.error(f"Error in create_provedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear proveedor"
        )


# ============================================
# UPDATE PROVEDOR
# ============================================

@router.put(
    "/provedores/{provedor_id}",
    response_model=ProvedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar proveedor",
    description="Actualizar un proveedor existente con nuevos datos",
    responses={
        200: {"description": "Proveedor actualizado exitosamente"},
        404: {"description": "Proveedor no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_provedor(
    provedor_id: int = Path(..., ge=1, description="Identificador único del proveedor"),
    request: ProvedorUpdateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Actualizar un proveedor existente.
    
    **Parámetros de ruta:**
    - **provedor_id**: Identificador único del proveedor a actualizar
    
    **Cuerpo de la solicitud:**
    - Todos los campos son opcionales
    - Solo los campos proporcionados serán actualizados
    
    **Retorna:**
    - Datos actualizados del proveedor
    
    **Errores:**
    - **404**: Proveedor no encontrado
    """
    try:
        service = ProvedorService(db)
        provedor = service.update(provedor_id, request)
        
        if not provedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con id {provedor_id} no encontrado"
            )
        
        return provedor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_provedor({provedor_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar proveedor"
        )


# ============================================
# DELETE PROVEDOR
# ============================================

@router.delete(
    "/provedores/{provedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar proveedor",
    description="Eliminar un proveedor (soft delete - marca como inactivo)",
    responses={
        204: {"description": "Proveedor eliminado exitosamente"},
        404: {"description": "Proveedor no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_provedor(
    provedor_id: int = Path(..., ge=1, description="Identificador único del proveedor"),
    db: Session = Depends(get_db)
):
    """
    Eliminar un proveedor (soft delete).
    
    **Parámetros de ruta:**
    - **provedor_id**: Identificador único del proveedor a eliminar
    
    **Nota:**
    - Esto realiza un soft delete (marca provedor_estado=0)
    - El registro permanece en la base de datos
    
    **Errores:**
    - **404**: Proveedor no encontrado
    """
    try:
        service = ProvedorService(db)
        deleted = service.delete(provedor_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con id {provedor_id} no encontrado"
            )
        
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_provedor({provedor_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar proveedor"
        )


# ============================================
# GET STATISTICS
# ============================================

@router.get(
    "/provedores/stats",
    response_model=ProvedorStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de proveedores",
    description="Obtener estadísticas agregadas sobre los proveedores",
    response_description="Estadísticas incluyendo conteos por estado y tipo"
)
async def get_provedor_stats(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas sobre proveedores.
    
    **Retorna:**
    - Conteo total
    - Conteos activos/inactivos
    - Conteos por estado
    - Conteos por tipo
    """
    try:
        service = ProvedorService(db)
        stats = service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_provedor_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener estadísticas"
        )


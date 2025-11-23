"""
Liquidacion service layer with business logic.

This module demonstrates:
- Service layer pattern (separation of concerns)
- CRUD operations
- Pagination
- Search/filtering
- Error handling
- Transaction management
"""

import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from app.models.liquidacion import (
    Liquidacion,
    LiquidacionCreateRequest,
    LiquidacionUpdateRequest,
    LiquidacionResponse,
    LiquidacionListResponse,
    LiquidacionStatsResponse
)

logger = logging.getLogger("uvicorn")


class LiquidacionService:
    """
    Business logic layer for Liquidacion entity operations.
    
    This service handles:
    - CRUD operations
    - Business rules validation
    - Data transformation
    - Transaction management
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        estado: Optional[int] = None,
        id_reserva: Optional[int] = None,
        factura: Optional[int] = None
    ) -> LiquidacionListResponse:
        """
        Get paginated list of liquidaciones with filtering.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for nombre_empresa, nombre_pasajero, nombre_asesor
            estado: Filter by estado (1=activo, 0=inactivo)
            id_reserva: Filter by id_reserva
            factura: Filter by factura
            
        Returns:
            LiquidacionListResponse: Paginated list with metadata
        """
        try:
            # Base query
            query = self.db.query(Liquidacion)
            
            # Apply estado filter
            if estado is not None:
                query = query.filter(Liquidacion.estado == estado)
            
            # Apply id_reserva filter
            if id_reserva is not None:
                query = query.filter(Liquidacion.id_reserva == id_reserva)
            
            # Apply factura filter
            if factura is not None:
                query = query.filter(Liquidacion.factura == factura)
            
            # Apply search filter
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Liquidacion.nombre_empresa.ilike(search_pattern),
                        Liquidacion.nombre_pasajero.ilike(search_pattern),
                        Liquidacion.nombre_asesor.ilike(search_pattern),
                        Liquidacion.observaciones.ilike(search_pattern)
                    )
                )
            
            # Count total
            total = query.count()
            
            # Calculate pages
            pages = (total + limit - 1) // limit if total > 0 else 0
            
            # Apply pagination and ordering
            offset = (page - 1) * limit
            liquidaciones = query.order_by(desc(Liquidacion.id)).offset(offset).limit(limit).all()
            
            return LiquidacionListResponse(
                liquidaciones=[LiquidacionResponse.model_validate(l) for l in liquidaciones],
                total=total,
                page=page,
                limit=limit,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            raise

    def get_by_id(self, liquidacion_id: int) -> Optional[LiquidacionResponse]:
        """
        Get liquidacion by ID.
        
        Args:
            liquidacion_id: Liquidacion ID
            
        Returns:
            LiquidacionResponse or None if not found
        """
        try:
            liquidacion = self.db.query(Liquidacion).filter(
                Liquidacion.id == liquidacion_id
            ).first()
            
            if liquidacion:
                return LiquidacionResponse.model_validate(liquidacion)
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id({liquidacion_id}): {str(e)}")
            raise

    def create(self, request: LiquidacionCreateRequest) -> LiquidacionResponse:
        """
        Create new liquidacion.
        
        Args:
            request: Liquidacion creation data
            
        Returns:
            LiquidacionResponse: Created liquidacion
        """
        try:
            # Create new liquidacion
            liquidacion = Liquidacion(
                id_reserva=request.id_reserva,
                nombre_asesor=request.nombre_asesor,
                nombre_empresa=request.nombre_empresa,
                nit_empresa=request.nit_empresa,
                direccion_empresa=request.direccion_empresa,
                telefono_empresa=request.telefono_empresa,
                observaciones=request.observaciones,
                servicio=request.servicio,
                fecha_servicio=request.fecha_servicio,
                incluye_servicio=request.incluye_servicio,
                numero_pasajeros=request.numero_pasajeros,
                valor_liquidacion=request.valor_liquidacion,
                iva=request.iva,
                valor_iva=request.valor_iva,
                valor_total_iva=request.valor_total_iva,
                nombre_pasajero=request.nombre_pasajero,
                fecha=request.fecha,
                factura=request.factura,
                estado=request.estado if request.estado is not None else 1,
                origen_venta=request.origen_venta
            )
            
            self.db.add(liquidacion)
            self.db.commit()
            self.db.refresh(liquidacion)
            
            logger.info(f"✅ Created liquidacion {liquidacion.id}")
            return LiquidacionResponse.model_validate(liquidacion)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating liquidacion: {str(e)}")
            raise

    def update(self, liquidacion_id: int, request: LiquidacionUpdateRequest) -> Optional[LiquidacionResponse]:
        """
        Update existing liquidacion.
        
        Args:
            liquidacion_id: Liquidacion ID to update
            request: Update data
            
        Returns:
            LiquidacionResponse or None if not found
        """
        try:
            # Find liquidacion
            liquidacion = self.db.query(Liquidacion).filter(
                Liquidacion.id == liquidacion_id
            ).first()
            
            if not liquidacion:
                return None
            
            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(liquidacion, field, value)
            
            self.db.commit()
            self.db.refresh(liquidacion)
            
            logger.info(f"✅ Updated liquidacion {liquidacion_id}")
            return LiquidacionResponse.model_validate(liquidacion)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating liquidacion {liquidacion_id}: {str(e)}")
            raise

    def delete(self, liquidacion_id: int) -> bool:
        """
        Soft delete liquidacion (set estado=0).
        
        Args:
            liquidacion_id: Liquidacion ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            liquidacion = self.db.query(Liquidacion).filter(
                Liquidacion.id == liquidacion_id
            ).first()
            
            if not liquidacion:
                return False
            
            # Soft delete
            liquidacion.estado = 0
            
            self.db.commit()
            logger.info(f"🗑️  Deleted liquidacion {liquidacion_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting liquidacion {liquidacion_id}: {str(e)}")
            raise

    def get_stats(self) -> LiquidacionStatsResponse:
        """
        Get statistics about liquidaciones.
        
        Returns:
            LiquidacionStatsResponse: Statistics data
        """
        try:
            # Total count
            total = self.db.query(Liquidacion).count()
            
            # Active/inactive count
            activas = self.db.query(Liquidacion).filter(
                Liquidacion.estado == 1
            ).count()
            
            inactivas = self.db.query(Liquidacion).filter(
                Liquidacion.estado == 0
            ).count()
            
            # Count by estado
            estado_counts = self.db.query(
                Liquidacion.estado,
                func.count(Liquidacion.id).label('count')
            ).group_by(Liquidacion.estado).all()
            
            por_estado = {str(estado): count for estado, count in estado_counts}
            
            return LiquidacionStatsResponse(
                total=total,
                activas=activas,
                inactivas=inactivas,
                por_estado=por_estado
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise


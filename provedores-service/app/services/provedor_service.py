"""
Provedor service layer with business logic.

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
from app.models.provedor import (
    Provedor,
    ProvedorCreateRequest,
    ProvedorUpdateRequest,
    ProvedorResponse,
    ProvedorListResponse,
    ProvedorStatsResponse
)

logger = logging.getLogger("uvicorn")


class ProvedorService:
    """
    Business logic layer for Provedor entity operations.
    
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
        tipo: Optional[int] = None,
        ciudad: Optional[int] = None
    ) -> ProvedorListResponse:
        """
        Get paginated list of provedores with filtering.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for nombre, razonsocial, identificacion
            estado: Filter by estado (1=activo, 0=inactivo)
            tipo: Filter by tipo
            ciudad: Filter by ciudad
            
        Returns:
            ProvedorListResponse: Paginated list with metadata
        """
        try:
            # Base query
            query = self.db.query(Provedor)
            
            # Apply estado filter
            if estado is not None:
                query = query.filter(Provedor.provedor_estado == estado)
            
            # Apply tipo filter
            if tipo is not None:
                query = query.filter(Provedor.provedor_tipo == tipo)
            
            # Apply ciudad filter
            if ciudad is not None:
                query = query.filter(Provedor.provedor_ciudad == ciudad)
            
            # Apply search filter
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Provedor.provedor_nombre.ilike(search_pattern),
                        Provedor.provedor_razonsocial.ilike(search_pattern),
                        Provedor.provedor_identificacion.ilike(search_pattern)
                    )
                )
            
            # Count total
            total = query.count()
            
            # Calculate pages
            pages = (total + limit - 1) // limit if total > 0 else 0
            
            # Apply pagination and ordering
            offset = (page - 1) * limit
            provedores = query.order_by(desc(Provedor.id)).offset(offset).limit(limit).all()
            
            return ProvedorListResponse(
                provedores=[ProvedorResponse.model_validate(p) for p in provedores],
                total=total,
                page=page,
                limit=limit,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            raise

    def get_by_id(self, provedor_id: int) -> Optional[ProvedorResponse]:
        """
        Get provedor by ID.
        
        Args:
            provedor_id: Provedor ID
            
        Returns:
            ProvedorResponse or None if not found
        """
        try:
            provedor = self.db.query(Provedor).filter(
                Provedor.id == provedor_id
            ).first()
            
            if provedor:
                return ProvedorResponse.model_validate(provedor)
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id({provedor_id}): {str(e)}")
            raise

    def create(self, request: ProvedorCreateRequest) -> ProvedorResponse:
        """
        Create new provedor.
        
        Args:
            request: Provedor creation data
            
        Returns:
            ProvedorResponse: Created provedor
        """
        try:
            # Create new provedor
            provedor = Provedor(
                provedor_hotel_code=request.provedor_hotel_code,
                provedor_razonsocial=request.provedor_razonsocial,
                provedor_nombre=request.provedor_nombre,
                provedor_identificacion=request.provedor_identificacion,
                provedor_direccion=request.provedor_direccion,
                provedor_telefono=request.provedor_telefono,
                provedor_tipo=request.provedor_tipo,
                provedor_estado=request.provedor_estado if request.provedor_estado is not None else 1,
                provedor_ciudad=request.provedor_ciudad,
                provedor_link_dropbox=request.provedor_link_dropbox
            )
            
            self.db.add(provedor)
            self.db.commit()
            self.db.refresh(provedor)
            
            logger.info(f"✅ Created provedor {provedor.id}")
            return ProvedorResponse.model_validate(provedor)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating provedor: {str(e)}")
            raise

    def update(self, provedor_id: int, request: ProvedorUpdateRequest) -> Optional[ProvedorResponse]:
        """
        Update existing provedor.
        
        Args:
            provedor_id: Provedor ID to update
            request: Update data
            
        Returns:
            ProvedorResponse or None if not found
        """
        try:
            # Find provedor
            provedor = self.db.query(Provedor).filter(
                Provedor.id == provedor_id
            ).first()
            
            if not provedor:
                return None
            
            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(provedor, field, value)
            
            self.db.commit()
            self.db.refresh(provedor)
            
            logger.info(f"✅ Updated provedor {provedor_id}")
            return ProvedorResponse.model_validate(provedor)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating provedor {provedor_id}: {str(e)}")
            raise

    def delete(self, provedor_id: int) -> bool:
        """
        Soft delete provedor (set provedor_estado=0).
        
        Args:
            provedor_id: Provedor ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            provedor = self.db.query(Provedor).filter(
                Provedor.id == provedor_id
            ).first()
            
            if not provedor:
                return False
            
            # Soft delete
            provedor.provedor_estado = 0
            
            self.db.commit()
            logger.info(f"🗑️  Deleted provedor {provedor_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting provedor {provedor_id}: {str(e)}")
            raise

    def get_stats(self) -> ProvedorStatsResponse:
        """
        Get statistics about provedores.
        
        Returns:
            ProvedorStatsResponse: Statistics data
        """
        try:
            # Total count
            total = self.db.query(Provedor).count()
            
            # Active/inactive count
            activos = self.db.query(Provedor).filter(
                Provedor.provedor_estado == 1
            ).count()
            
            inactivos = self.db.query(Provedor).filter(
                Provedor.provedor_estado == 0
            ).count()
            
            # Count by estado
            estado_counts = self.db.query(
                Provedor.provedor_estado,
                func.count(Provedor.id).label('count')
            ).group_by(Provedor.provedor_estado).all()
            
            por_estado = {str(estado): count for estado, count in estado_counts if estado is not None}
            
            # Count by tipo
            tipo_counts = self.db.query(
                Provedor.provedor_tipo,
                func.count(Provedor.id).label('count')
            ).group_by(Provedor.provedor_tipo).all()
            
            por_tipo = {str(tipo): count for tipo, count in tipo_counts if tipo is not None}
            
            return ProvedorStatsResponse(
                total=total,
                activos=activos,
                inactivos=inactivos,
                por_estado=por_estado,
                por_tipo=por_tipo
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise


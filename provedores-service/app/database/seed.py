"""
Optional database seeding module.

This module populates the database with initial or test data.
Useful for:
- Development environments
- Testing
- Demo data
- Initial configuration

Delete this file if not needed.
"""

import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn")


def run_seeds(db: Session) -> None:
    """
    Run database seeds.
    
    Args:
        db: SQLAlchemy session
    """
    try:
        logger.info("🌱 Running database seeds...")
        
        # Check if data already exists
        from app.models.provedor import Provedor
        existing_count = db.query(Provedor).count()
        if existing_count > 0:
            logger.info(f"ℹ️  Database already seeded ({existing_count} provedores exist)")
            return
        
        # Add seed data if needed
        # Example:
        # sample_data = [
        #     Provedor(
        #         provedor_nombre="Test Proveedor",
        #         provedor_razonsocial="Test Proveedor S.A.",
        #         provedor_estado=1
        #     ),
        # ]
        # db.add_all(sample_data)
        # db.commit()
        # logger.info(f"✅ Seeded {len(sample_data)} provedor records")
        
        logger.info("✅ Seeding completed (no seed data configured)")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Seeding error: {str(e)}")
        # Don't raise - allow service to start even if seeding fails


def clear_seeds(db: Session) -> None:
    """
    Clear all seeded data (for testing).
    
    Args:
        db: SQLAlchemy session
    """
    try:
        logger.warning("🗑️  Clearing all data...")
        
        from app.models.provedor import Provedor
        # Delete all provedores (use with caution!)
        # db.query(Provedor).delete()
        # db.commit()
        
        logger.info("✅ All data cleared")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error clearing data: {str(e)}")
        raise


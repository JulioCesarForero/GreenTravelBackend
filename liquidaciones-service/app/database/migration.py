"""
Optional database migration module.

This module handles schema migrations and updates.
Use for production environments or complex schema changes.

For simple projects, you can delete this file and use init_db() instead.
For advanced migrations, consider using Alembic.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger("uvicorn")


def run_migrations(db: Session) -> None:
    """
    Run database migrations.
    
    Args:
        db: SQLAlchemy session
        
    Example migrations:
        - Add new columns
        - Create indexes
        - Update data
        - Schema modifications
    """
    try:
        logger.info("🔄 Running database migrations...")
        
        # Example migration: Add index
        # db.execute(text("""
        #     CREATE INDEX IF NOT EXISTS idx_liquidacion_fecha 
        #     ON liquidaciones(fecha)
        # """))
        
        # Commit migrations
        db.commit()
        logger.info("✅ Migrations completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Migration error: {str(e)}")
        # Don't raise - allow service to start even if migrations fail
        # In production, you might want to raise the error


def get_migration_version(db: Session) -> int:
    """
    Get current migration version.
    
    Args:
        db: SQLAlchemy session
        
    Returns:
        int: Current migration version
    """
    try:
        # Create migrations table if not exists
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.commit()
        
        # Get latest version
        result = db.execute(text(
            "SELECT COALESCE(MAX(version), 0) as version FROM schema_migrations"
        ))
        version = result.fetchone()[0]
        return version
        
    except Exception as e:
        logger.error(f"Error getting migration version: {str(e)}")
        return 0


def set_migration_version(db: Session, version: int) -> None:
    """
    Set current migration version.
    
    Args:
        db: SQLAlchemy session
        version: Migration version to set
    """
    try:
        db.execute(text(
            "INSERT INTO schema_migrations (version) VALUES (:version)"
        ), {"version": version})
        db.commit()
        logger.info(f"✅ Migration version set to {version}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting migration version: {str(e)}")


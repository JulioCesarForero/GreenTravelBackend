"""
Database connection module with SQLAlchemy engine and session management.

This module implements:
- Connection pooling with optimization
- Database existence verification
- Health checks
- Dependency injection for FastAPI
- MySQL/MariaDB specific configuration
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError

# Configure logging
logger = logging.getLogger("uvicorn")

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Get DATABASE_URL from environment, with fallback
# Handle case where docker-compose passes empty string instead of None
DATABASE_URL = os.getenv("DATABASE_URL") or None
if not DATABASE_URL:
    # Fallback: construct from individual environment variables
    mysql_user = os.getenv("MYSQL_USER", "appuser")
    mysql_password = os.getenv("MYSQL_PASSWORD", "AppPass123!")
    mysql_host = os.getenv("MYSQL_HOST", "mysql-db")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_database = os.getenv("MYSQL_DATABASE", "colombia_green_travel")
    DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"

SERVICE_NAME = os.getenv("SERVICE_NAME", "facturas-service")

# ============================================
# DATABASE ENGINE WITH CONNECTION POOLING
# ============================================

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", "20")),        # Base connections
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "40")),  # Additional connections
    pool_pre_ping=True,                                     # Verify connections before use
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),# Recycle every 30 min
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),  # Connection timeout
    connect_args={
        "connect_timeout": 10,
        "charset": "utf8mb4"
    }
)

# ============================================
# SESSION FACTORY
# ============================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Avoid additional queries after commit
)

# ============================================
# DECLARATIVE BASE FOR MODELS
# ============================================

Base = declarative_base()

# ============================================
# DATABASE UTILITIES
# ============================================

def ensure_database_exists() -> bool:
    """
    Ensure database exists, verify connection.
    
    Returns:
        bool: True if database connection successful
    """
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying database connection: {str(e)}")
        return False


def test_db_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection test successful")
        return True
    except OperationalError as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error testing connection: {str(e)}")
        return False


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLAlchemy models.
    Note: For existing databases, this will only create tables that don't exist.
    """
    try:
        # Import all models here to ensure they're registered
        from app.models.invoice import Base as ModelBase
        from app.models.invoice_item import Base as ItemModelBase
        
        # Create all tables (only if they don't exist)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified successfully")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        raise


# ============================================
# DEPENDENCY INJECTION
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# REDIS CACHE (Disabled for development)
# ============================================
# Redis caching has been disabled for this development stage.
# To enable Redis in the future, uncomment and configure below.

def get_redis_client():
    """
    Redis client function (disabled).
    
    Returns:
        None: Redis is disabled for development
    """
    return None


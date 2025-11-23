"""
Main FastAPI application entry point.

This module demonstrates The Twelve-Factor App principles:
I.   Codebase - Single codebase in version control
II.  Dependencies - Explicitly declared in requirements.txt
III. Config - All config in environment variables
IV.  Backing services - Database as attached resource
V.   Build/Release/Run - Separated via Docker
VI.  Processes - Stateless, share-nothing process
VII. Port binding - Self-contained, exports HTTP via port
VIII.Concurrency - Scale via process model (multiple containers)
IX.  Disposability - Fast startup, graceful shutdown
X.   Dev/Prod parity - Same stack in all environments
XI.  Logs - Treat logs as event streams (stdout)
XII. Admin processes - Run as one-off processes (migrations, seeds)
"""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# Import application components
from app.routes.invoice import router as invoice_router
from app.routes.invoice_item import router as invoice_item_router
from app.database.connection import (
    init_db,
    test_db_connection,
    ensure_database_exists,
    SessionLocal
)
from app.database.migration import run_migrations
from app.database.seed import run_seeds

# Configure logging to stdout (Factor XI: Logs)
# Handle empty string from docker-compose (convert to None to use default)
log_level = os.getenv("LOG_LEVEL") or "INFO"
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Stream to stdout
)
logger = logging.getLogger("uvicorn")

# Service configuration from environment (Factor III: Config)
SERVICE_NAME = os.getenv("SERVICE_NAME", "facturas-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# ============================================
# LIFESPAN EVENTS (Factor IX: Disposability)
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.
    
    Handles:
    - Fast startup with database initialization
    - Graceful shutdown with cleanup
    """
    # STARTUP
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"📍 Environment: {ENVIRONMENT}")
    
    # Ensure database exists (Factor IV: Backing services)
    if not ensure_database_exists():
        logger.error("❌ Failed to ensure database exists")
        # Continue anyway - service might be used without DB
    
    # Test connection with retries (Factor IX: Fast startup)
    max_retries = 5
    for attempt in range(max_retries):
        if test_db_connection():
            logger.info("✅ Database connection established")
            break
        logger.warning(f"⏳ Connection attempt {attempt + 1}/{max_retries} failed. Retrying in 3s...")
        await asyncio.sleep(3)
    else:
        logger.error("❌ Could not connect to database after retries")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {str(e)}")
    
    # Run migrations (Factor XII: Admin processes)
    try:
        with SessionLocal() as db:
            run_migrations(db)
    except Exception as e:
        logger.error(f"⚠️  Migration error: {str(e)}")
    
    # Run seeds in development (Factor X: Dev/prod parity)
    if ENVIRONMENT == "development":
        try:
            with SessionLocal() as db:
                run_seeds(db)
        except Exception as e:
            logger.error(f"⚠️  Seeding error: {str(e)}")
    
    logger.info("✅ Application started successfully")
    
    yield  # Application runs here
    
    # SHUTDOWN (Factor IX: Graceful shutdown)
    logger.info("🛑 Shutting down gracefully...")
    # Close database connections, cleanup resources
    logger.info("✅ Shutdown complete")


# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title=SERVICE_NAME,
    description=f"Microservicio de facturas siguiendo principios Clean Code y Twelve-Factor App",
    version=SERVICE_VERSION,
    debug=DEBUG,
    lifespan=lifespan,
    # OpenAPI documentation
    docs_url="/docs" if DEBUG else None,  # Disable in production
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
)


# ============================================
# MIDDLEWARE
# ============================================

# CORS Configuration (Factor III: Config from environment)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests (Factor XI: Logs as event streams)."""
    logger.info(f"➡️  {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"⬅️  {request.method} {request.url.path} - {response.status_code}")
    return response


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.warning(f"⚠️  Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"❌ Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )


# ============================================
# ROUTES
# ============================================

# Include API routers
app.include_router(
    invoice_router,
    prefix="/api/v1",
    tags=["invoices"]
)

app.include_router(
    invoice_item_router,
    prefix="/api/v1",
    tags=["invoice-items"]
)


# Health check endpoint (Factor VII: Port binding)
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for container orchestration.
    
    Returns service status and version.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {SERVICE_NAME}",
        "version": SERVICE_VERSION,
        "docs": "/docs" if DEBUG else "Documentation disabled in production",
        "health": "/health"
    }


# ============================================
# MAIN EXECUTION (Factor VII: Port binding)
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    # Port binding from environment
    port = int(os.getenv("PORT", "8003"))
    host = os.getenv("HOST", "0.0.0.0")
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    
    # Run with uvicorn (Factor VIII: Concurrency via process model)
    # Handle empty string from docker-compose (convert to None to use default)
    log_level = (os.getenv("LOG_LEVEL") or "info").lower()
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,  # Scale via multiple workers
        loop="asyncio",
        log_level=log_level,
        access_log=DEBUG,  # Disable access logs in production for performance
        reload=DEBUG  # Auto-reload in development only
    )


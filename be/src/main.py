"""
Main application module.
Initializes the FastAPI application and all its components.
"""

import logging
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.config.logging import setup_logging
from src.db.session import get_engine, get_session_factory, close_db_connection
from src.db.base import Base, load_all_models
from src.core.algorithms import initialize_algorithms, load_algorithms_from_db
from src.core.registry import get_algorithm_registry
from src.services import init_services, shutdown_services
from src.cache import init_cache, shutdown_cache, get_cache_client
from src.api.routes import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(
    title="Digital Signature Verification API",
    description="API for verifying digital signatures using various cryptographic algorithms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
cors_settings = get_settings()
origins = [origin.strip() for origin in cors_settings.cors_origins.split(",")] if cors_settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Perform startup tasks."""
    logger.info("Starting up application")
    
    settings = get_settings()
    
    # Load all models
    logger.info("Loading all database models")
    load_all_models()
    
    # Initialize database
    engine = get_engine()
    
    # Create database tables
    # In production, use migrations instead
    if settings.auto_create_tables:
        logger.info("Creating database tables (auto_create_tables=True)")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        logger.info("Skipping auto table creation (auto_create_tables=False)")
    
    # Initialize cache
    cache_client = await init_cache(settings.redis_url)
    
    # Initialize database session factory
    session_factory = get_session_factory()
    
    # Initialize algorithm providers
    logger.info("Initializing algorithm providers")
    algorithm_providers = initialize_algorithms()
    
    # Load algorithm data from database
    logger.info("Loading algorithms and curves from database")
    # Create a temporary session for loading algorithms
    async with session_factory() as db_session:
        algorithms_data = await load_algorithms_from_db()
    
    # Register the loaded data with the registry
    if algorithms_data:
        registry = get_algorithm_registry()
        registry.set_db_data(algorithms_data)
        
        # Set ECDSA as the default algorithm if available
        if "ECDSA" in algorithm_providers:
            registry.set_default_algorithm("ECDSA")
    
    # Initialize services
    # Use the session factory for services initialization
    await init_services(session_factory, cache_client)
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Perform shutdown tasks."""
    logger.info("Shutting down application")
    
    # Shutdown services
    await shutdown_services()
    
    # Shutdown cache
    await shutdown_cache()
    
    # Close database connection
    await close_db_connection()
    
    logger.info("Application shutdown complete")


# Include all API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Digital Signature Verification API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "description": "API for verifying digital signatures using various cryptographic algorithms",
        "endpoints": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json",
            "health_check": "/health",
            "api_base": "/api/v1"
        }
    }

# Đảm bảo rằng tất cả các bảng được tạo khi khởi động với uvicorn
if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="debug" if settings.debug else "info"
    ) 
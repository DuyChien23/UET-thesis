"""
Main application module.
Initializes the FastAPI application and all its components.
"""

import logging
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from config.logging import setup_logging
from db.session import get_engine, get_db_session, close_db_connection
from db.base import Base
from algorithms import initialize_algorithms
from services import init_services, shutdown_services
from cache import init_cache, shutdown_cache, get_cache_client
from api.routes import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(
    title="Digital Signature Verification API",
    description="API for verifying digital signatures",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Perform startup tasks."""
    logger.info("Starting up application")
    
    settings = get_settings()
    
    # Initialize database
    engine = get_engine()
    
    # Create database tables
    # In production, use migrations instead
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize cache
    cache_client = await init_cache(settings.redis_url)
    
    # Initialize database session
    db_session = await get_db_session()
    
    # Initialize algorithm providers
    initialize_algorithms()
    
    # Initialize services
    await init_services(db_session, cache_client)
    
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
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    ) 
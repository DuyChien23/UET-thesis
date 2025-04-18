from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api.router import api_router
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure app
app_name = os.getenv("APP_NAME", "ECDSA Signature Service")
app = FastAPI(
    title=app_name,
    description="Secure Digital Signature Service using ECDSA (Elliptic Curve Digital Signature Algorithm)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ECDSA Signature Service API"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
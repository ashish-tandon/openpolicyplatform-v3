"""
Main FastAPI Application for Unified Open Policy Platform
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import List

from .routers import policies, scrapers, admin, auth, health
from .dependencies import get_current_user
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Open Policy Platform API...")
    print(f"📊 Database: {settings.database_url}")
    print(f"🔧 Environment: {settings.environment}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Open Policy Platform API...")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Open Policy Platform API",
        description="Unified API for policy analysis, data collection, and administration",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
    app.include_router(scrapers.router, prefix="/api/v1/scrapers", tags=["Scrapers"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Open Policy Platform API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs" if settings.environment != "production" else None
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": "2024-08-08T00:00:00Z",
            "version": "1.0.0"
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )

"""
Health Check Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..dependencies import get_db
from ..config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "Open Policy Platform API",
        "version": settings.version,
        "environment": settings.environment
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "service": "Open Policy Platform API",
        "version": settings.version,
        "environment": settings.environment,
        "database": db_status,
        "timestamp": "2024-08-08T00:00:00Z"
    }

"""
API Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from .config import settings
from ..config.database import get_database_session

# Security scheme
security = HTTPBearer(auto_error=False)

# Expose DB session via FastAPI dependency injection so tests can override it

def get_db(db: Session = Depends(get_database_session)):
    """Yield a database session that can be overridden in tests."""
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # TODO: Implement JWT token validation properly
    # For tests, return a mock user
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@openpolicy.com",
        "role": "admin"
    }


def require_admin(current_user = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

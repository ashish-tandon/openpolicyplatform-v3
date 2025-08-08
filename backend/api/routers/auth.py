"""
Authentication Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..dependencies import get_db, get_current_user
from ..config import settings

router = APIRouter()

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login"""
    # TODO: Implement actual authentication
    if form_data.username == "admin" and form_data.password == "admin":
        return {
            "access_token": "mock_token_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@openpolicy.com",
                "role": "admin"
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Successfully logged out"}

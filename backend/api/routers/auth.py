"""
Enhanced Authentication Router
Provides comprehensive authentication, user management, and security functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import jwt
import bcrypt
import json
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from ..dependencies import get_db, get_current_user
from ..config import settings

router = APIRouter()

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Data models (input)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

# Data models (output)
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    permissions: List[str] = []
    is_active: Optional[bool] = True
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserPublic

class MessageResponse(BaseModel):
    message: str
    timestamp: Optional[str] = None

class UsersListResponse(BaseModel):
    users: List[UserPublic]
    total_users: int
    active_users: int

class PermissionsResponse(BaseModel):
    permissions: List[str]
    role: str

# Mock user database - in real implementation, this would be a database table
MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@openpolicy.com",
        "full_name": "System Administrator",
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
        "role": "admin",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-08-08T00:00:00Z",
        "permissions": ["read", "write", "admin", "delete"]
    },
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@openpolicy.com",
        "full_name": "Regular User",
        "password_hash": bcrypt.hashpw("user123".encode(), bcrypt.gensalt()),
        "role": "user",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-08-07T00:00:00Z",
        "permissions": ["read"]
    }
}

# JWT settings
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def get_user(username: str):
    """Get user by username"""
    return MOCK_USERS.get(username)

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login with JWT token generation"""
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": user["username"]}
        )
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "permissions": user["permissions"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/register", response_model=Dict[str, UserPublic])
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if username already exists
        if user_data.username in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        for user in MOCK_USERS.values():
            if user["email"] == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Create new user
        new_user = {
            "id": len(MOCK_USERS) + 1,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name or user_data.username,
            "password_hash": bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()),
            "role": user_data.role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": ["read"] if user_data.role == "user" else ["read", "write"]
        }
        
        # Add to mock database
        MOCK_USERS[user_data.username] = new_user
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
                "full_name": new_user["full_name"],
                "role": new_user["role"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        
        if not username or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = get_user(username)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    try:
        user = get_user(current_user["username"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "permissions": user["permissions"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user info: {str(e)}"
        )

@router.put("/me", response_model=Dict[str, UserPublic])
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        user = get_user(current_user["username"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        if user_update.email is not None:
            # Check if email is already taken
            for other_user in MOCK_USERS.values():
                if other_user["email"] == user_update.email and other_user["username"] != user["username"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            user["email"] = user_update.email
        
        if user_update.full_name is not None:
            user["full_name"] = user_update.full_name
        
        if user_update.password is not None:
            user["password_hash"] = bcrypt.hashpw(user_update.password.encode(), bcrypt.gensalt())
        
        if user_update.is_active is not None:
            user["is_active"] = user_update.is_active
        
        return {
            "message": "User updated successfully",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user["is_active"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_change: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        user = get_user(current_user["username"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_change.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user["password_hash"] = bcrypt.hashpw(password_change.new_password.encode(), bcrypt.gensalt())
        
        return {
            "message": "Password changed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user = Depends(get_current_user)):
    """User logout"""
    try:
        # In a real implementation, you might want to blacklist the token
        # For now, we'll just return a success message
        return {
            "message": "Successfully logged out",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout error: {str(e)}"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    password_reset: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    try:
        # Find user by email
        user = None
        for u in MOCK_USERS.values():
            if u["email"] == password_reset.email:
                user = u
                break
        
        if not user:
            # Don't reveal if email exists or not
            return {
                "message": "If the email exists, a password reset link has been sent"
            }
        
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": user["username"], "type": "reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Add background task to send email
        background_tasks.add_task(send_password_reset_email, user["email"], reset_token)
        
        return {
            "message": "If the email exists, a password reset link has been sent"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing password reset: {str(e)}"
        )

@router.get("/users", response_model=UsersListResponse)
async def get_all_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        user = get_user(current_user["username"])
        if not user or user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        users = []
        for u in MOCK_USERS.values():
            users.append({
                "id": u["id"],
                "username": u["username"],
                "email": u["email"],
                "full_name": u["full_name"],
                "role": u["role"],
                "is_active": u["is_active"],
                "created_at": u["created_at"],
                "last_login": u["last_login"]
            })
        
        return {
            "users": users,
            "total_users": len(users),
            "active_users": len([u for u in users if u["is_active"]])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

@router.get("/permissions", response_model=PermissionsResponse)
async def get_user_permissions(current_user = Depends(get_current_user)):
    """Get current user permissions"""
    try:
        user = get_user(current_user["username"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "permissions": user["permissions"],
            "role": user["role"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving permissions: {str(e)}"
        )

async def send_password_reset_email(email: str, reset_token: str):
    """Background task to send password reset email"""
    try:
        # Mock email sending - in real implementation, use email service
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # Log the reset link for testing
        with open(f"password_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", 'w') as f:
            f.write(f"Password reset for: {email}\n")
            f.write(f"Reset link: {reset_link}\n")
            f.write(f"Token: {reset_token}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        
    except Exception as e:
        # Log error
        with open(f"password_reset_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", 'w') as f:
            f.write(f"Error sending password reset email to {email}: {str(e)}\n")

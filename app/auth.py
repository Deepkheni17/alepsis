"""
Supabase Authentication Module

Handles JWT token verification and user management for FastAPI endpoints.
Supports email/password and OAuth (Google) authentication via Supabase Auth.
"""

import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime
import uuid
import logging

from app.database import get_db
from app.models.orm_models import User

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Load Supabase configuration from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Validate required environment variables
if not SUPABASE_JWT_SECRET:
    raise ValueError("SUPABASE_JWT_SECRET environment variable is required")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")


class AuthError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, error: str, status_code: int):
        self.error = error
        self.status_code = status_code


def verify_jwt_token(token: str) -> Dict:
    """
    Verify and decode Supabase JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Decoded token payload containing user information
        
    Raises:
        AuthError: If token is invalid, expired, or malformed
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_signature": True
            }
        )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise AuthError("Token has expired", status.HTTP_401_UNAUTHORIZED)
    
    except jwt.InvalidAudienceError:
        logger.warning("Invalid token audience")
        raise AuthError("Invalid token audience", status.HTTP_401_UNAUTHORIZED)
    
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise AuthError(f"Invalid token: {str(e)}", status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}", exc_info=True)
        raise AuthError(f"Token verification failed: {str(e)}", status.HTTP_401_UNAUTHORIZED)


def get_or_create_user(db: Session, user_id: str, email: str) -> User:
    """
    Get existing user or create new user in local database.
    
    Synchronizes Supabase Auth users with local User table for foreign key relationships.
    
    Args:
        db: Database session
        user_id: Supabase user UUID
        email: User email address
        
    Returns:
        User ORM instance
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise AuthError(f"Invalid user_id format: {user_id}", status.HTTP_401_UNAUTHORIZED)
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        # Create new user
        user = User(
            id=user_uuid,
            email=email,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {email} (id={user_uuid})")
    
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency for protected endpoints.
    
    Extracts JWT from Authorization header, verifies it, and returns authenticated user.
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": str(current_user.id)}
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Authenticated User instance
        
    Raises:
        HTTPException 401: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify JWT token
        payload = verify_jwt_token(token)
        
        # Extract user information
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user_id or email",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get or create user in local database
        user = get_or_create_user(db, user_id, email)
        
        return user
    
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    
    Returns user if valid token is provided, None otherwise.
    Does not raise exceptions for missing/invalid tokens.
    
    Usage:
        @router.get("/maybe-protected")
        async def route(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return {"message": "Authenticated"}
            return {"message": "Anonymous"}
    
    Args:
        credentials: Optional HTTP Bearer token
        db: Database session
        
    Returns:
        User instance if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

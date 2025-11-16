from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from app.services.auth_service import verify_token
from app.database import get_db
from app.models.user import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """Get current user from JWT token (Authorization header or cookie)"""
    # Try Authorization header first (for development with localStorage)
    auth_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.replace("Bearer ", "")
    elif token:
        # Fall back to cookie (for production with HTTP-only cookies)
        auth_token = token
    
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = verify_token(auth_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database (convert string UUID to UUID object)
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def require_farmer(current_user: User = Depends(get_current_user)):
    """Dependency that requires farmer role"""
    if current_user.role != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmer access required"
        )
    return current_user


async def require_buyer(current_user: User = Depends(get_current_user)):
    """Dependency that requires buyer role"""
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buyer access required"
        )
    return current_user

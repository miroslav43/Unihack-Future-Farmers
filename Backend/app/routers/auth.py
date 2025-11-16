from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if request.role not in ["farmer", "buyer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'farmer' or 'buyer'"
        )
    
    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
        role=request.role,
        is_active=True,
        last_login=datetime.utcnow()
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create JWT token
    token_data = {
        "user_id": str(user.id),  # Convert UUID to string for JSON serialization
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="none",  # Required for cross-origin (different ports on localhost)
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    # Return token and user data
    user_response = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Login a user"""
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create JWT token
    token_data = {
        "user_id": str(user.id),  # Convert UUID to string for JSON serialization
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="none",  # Required for cross-origin (different ports on localhost)
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    # Return token and user data
    user_response = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout a user by clearing the cookie"""
    response.delete_cookie(key="token", samesite="none")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active
    }

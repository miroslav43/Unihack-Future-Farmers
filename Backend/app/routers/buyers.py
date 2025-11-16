from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import BuyerCreate, BuyerUpdate, BuyerResponse
from app.database import get_db
from app.dependencies import get_current_user, require_buyer
from app.models.user import User, BuyerProfile
from datetime import datetime
from typing import List

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.post("/", response_model=BuyerResponse)
async def create_buyer_profile(
    buyer_data: BuyerCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    """Create buyer profile (requires buyer role)"""
    # Check if buyer profile already exists
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    existing_buyer = result.scalar_one_or_none()
    
    if existing_buyer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer profile already exists"
        )
    
    # Create buyer profile
    buyer = BuyerProfile(
        user_id=current_user.id,
        **buyer_data.model_dump()
    )
    
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    
    return BuyerResponse(
        id=str(buyer.id),
        user_id=str(buyer.user_id),
        company_name=buyer.company_name,
        contact_person=buyer.contact_person,
        phone=buyer.phone,
        email=buyer.email,
        business_type=buyer.business_type,
        tax_id=buyer.tax_id,
        address=buyer.address,
        city=buyer.city,
        county=buyer.county,
        postal_code=buyer.postal_code,
        created_at=buyer.created_at,
        updated_at=buyer.updated_at
    )


@router.get("/me/profile", response_model=BuyerResponse)
async def get_my_buyer_profile(
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    """Get current buyer's profile"""
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    buyer = result.scalar_one_or_none()
    
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer profile not found"
        )
    
    return BuyerResponse(
        id=str(buyer.id),
        user_id=str(buyer.user_id),
        company_name=buyer.company_name,
        contact_person=buyer.contact_person,
        phone=buyer.phone,
        email=buyer.email,
        business_type=buyer.business_type,
        tax_id=buyer.tax_id,
        address=buyer.address,
        city=buyer.city,
        county=buyer.county,
        postal_code=buyer.postal_code,
        created_at=buyer.created_at,
        updated_at=buyer.updated_at
    )


@router.get("/{buyer_id}", response_model=BuyerResponse)
async def get_buyer_by_id(
    buyer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get buyer by ID"""
    from uuid import UUID
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.id == UUID(buyer_id))
    )
    buyer = result.scalar_one_or_none()
    
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )
    
    return BuyerResponse(
        id=str(buyer.id),
        user_id=str(buyer.user_id),
        company_name=buyer.company_name,
        contact_person=buyer.contact_person,
        phone=buyer.phone,
        email=buyer.email,
        business_type=buyer.business_type,
        tax_id=buyer.tax_id,
        address=buyer.address,
        city=buyer.city,
        county=buyer.county,
        postal_code=buyer.postal_code,
        created_at=buyer.created_at,
        updated_at=buyer.updated_at
    )


@router.put("/{buyer_id}", response_model=BuyerResponse)
async def update_buyer_profile(
    buyer_id: str,
    buyer_data: BuyerUpdate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    """Update buyer profile"""
    from uuid import UUID
    # Check if buyer exists and belongs to current user
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.id == UUID(buyer_id))
    )
    buyer = result.scalar_one_or_none()
    
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer profile not found"
        )
    
    if buyer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Update buyer profile
    update_data = buyer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(buyer, field, value)
    
    buyer.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(buyer)
    
    return BuyerResponse(
        id=str(buyer.id),
        user_id=str(buyer.user_id),
        company_name=buyer.company_name,
        contact_person=buyer.contact_person,
        phone=buyer.phone,
        email=buyer.email,
        business_type=buyer.business_type,
        tax_id=buyer.tax_id,
        address=buyer.address,
        city=buyer.city,
        county=buyer.county,
        postal_code=buyer.postal_code,
        created_at=buyer.created_at,
        updated_at=buyer.updated_at
    )

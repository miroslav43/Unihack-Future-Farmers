from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import FarmerCreate, FarmerUpdate, FarmerResponse
from app.database import get_db
from app.dependencies import get_current_user, require_farmer
from app.models.user import User, FarmerProfile
from datetime import datetime
from typing import List

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post("/", response_model=FarmerResponse)
async def create_farmer_profile(
    farmer_data: FarmerCreate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Create farmer profile (requires farmer role)"""
    # Check if farmer profile already exists
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    existing_farmer = result.scalar_one_or_none()
    
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer profile already exists"
        )
    
    # Create farmer profile
    farmer = FarmerProfile(
        user_id=current_user.id,
        **farmer_data.model_dump()
    )
    
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        farm_name=farmer.farm_name,
        contact_person=farmer.contact_person,
        phone=farmer.phone,
        email=farmer.email,
        address=farmer.address,
        city=farmer.city,
        county=farmer.county,
        postal_code=farmer.postal_code,
        farm_size_hectares=farmer.farm_size_hectares,
        certifications=farmer.certifications,
        created_at=farmer.created_at,
        updated_at=farmer.updated_at
    )


@router.get("/me/profile", response_model=FarmerResponse)
async def get_my_farmer_profile(
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Get current farmer's profile"""
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found"
        )
    
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        farm_name=farmer.farm_name,
        contact_person=farmer.contact_person,
        phone=farmer.phone,
        email=farmer.email,
        address=farmer.address,
        city=farmer.city,
        county=farmer.county,
        postal_code=farmer.postal_code,
        farm_size_hectares=farmer.farm_size_hectares,
        certifications=farmer.certifications,
        created_at=farmer.created_at,
        updated_at=farmer.updated_at
    )


@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(db: AsyncSession = Depends(get_db)):
    """List all farmers"""
    result = await db.execute(select(FarmerProfile))
    farmers = result.scalars().all()
    
    return [
        FarmerResponse(
            id=str(farmer.id),
            user_id=str(farmer.user_id),
            farm_name=farmer.farm_name,
            contact_person=farmer.contact_person,
            phone=farmer.phone,
            email=farmer.email,
            address=farmer.address,
            city=farmer.city,
            county=farmer.county,
            postal_code=farmer.postal_code,
            farm_size_hectares=farmer.farm_size_hectares,
            certifications=farmer.certifications,
            created_at=farmer.created_at,
            updated_at=farmer.updated_at
        )
        for farmer in farmers
    ]


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer_by_id(
    farmer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get farmer by ID"""
    from uuid import UUID
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.id == UUID(farmer_id))
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        farm_name=farmer.farm_name,
        contact_person=farmer.contact_person,
        phone=farmer.phone,
        email=farmer.email,
        address=farmer.address,
        city=farmer.city,
        county=farmer.county,
        postal_code=farmer.postal_code,
        farm_size_hectares=farmer.farm_size_hectares,
        certifications=farmer.certifications,
        created_at=farmer.created_at,
        updated_at=farmer.updated_at
    )


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer_profile(
    farmer_id: str,
    farmer_data: FarmerUpdate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Update farmer profile"""
    from uuid import UUID
    # Check if farmer exists and belongs to current user
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.id == UUID(farmer_id))
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found"
        )
    
    if farmer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Update farmer profile
    update_data = farmer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farmer, field, value)
    
    farmer.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(farmer)
    
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        farm_name=farmer.farm_name,
        contact_person=farmer.contact_person,
        phone=farmer.phone,
        email=farmer.email,
        address=farmer.address,
        city=farmer.city,
        county=farmer.county,
        postal_code=farmer.postal_code,
        farm_size_hectares=farmer.farm_size_hectares,
        certifications=farmer.certifications,
        created_at=farmer.created_at,
        updated_at=farmer.updated_at
    )

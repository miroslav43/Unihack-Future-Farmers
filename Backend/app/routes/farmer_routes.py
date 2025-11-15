"""Farmer API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from ..models.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from ..services.farmer_service import FarmerService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    farmer_data: FarmerCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new farmer"""
    service = FarmerService(db)
    try:
        return await service.create_farmer(farmer_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get farmer by ID"""
    service = FarmerService(db)
    farmer = await service.get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return farmer


@router.get("/cnp/{cnp}", response_model=FarmerResponse)
async def get_farmer_by_cnp(
    cnp: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get farmer by CNP"""
    service = FarmerService(db)
    farmer = await service.get_farmer_by_cnp(cnp)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with CNP {cnp} not found"
        )
    return farmer


@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    county: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List farmers with pagination and filtering"""
    service = FarmerService(db)
    return await service.list_farmers(skip=skip, limit=limit, county=county)


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(
    farmer_id: str,
    farmer_update: FarmerUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update farmer information"""
    service = FarmerService(db)
    updated_farmer = await service.update_farmer(farmer_id, farmer_update)
    if not updated_farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return updated_farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete farmer"""
    service = FarmerService(db)
    deleted = await service.delete_farmer(farmer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )


@router.get("/statistics/overview")
async def get_farmer_statistics(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get overall farmer statistics"""
    service = FarmerService(db)
    return await service.get_farmer_statistics()

"""Crop API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.crop import CropCreate, CropUpdate, CropResponse, CropStatus
from ..services.crop_service import CropService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/crops", tags=["crops"])


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_data: CropCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new crop record"""
    service = CropService(db)
    return await service.create_crop(crop_data)


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get crop by ID"""
    service = CropService(db)
    crop = await service.get_crop(crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )
    return crop


@router.get("/farmer/{farmer_id}", response_model=List[CropResponse])
async def list_farmer_crops(
    farmer_id: str,
    status: Optional[CropStatus] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List crops for a farmer"""
    service = CropService(db)
    return await service.list_farmer_crops(
        farmer_id=farmer_id,
        status=status
    )


@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: str,
    crop_update: CropUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update crop"""
    service = CropService(db)
    updated_crop = await service.update_crop(crop_id, crop_update)
    if not updated_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )
    return updated_crop


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete crop"""
    service = CropService(db)
    deleted = await service.delete_crop(crop_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )


@router.get("/farmer/{farmer_id}/active", response_model=List[CropResponse])
async def get_active_crops(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get active (planted/growing) crops for a farmer"""
    service = CropService(db)
    return await service.get_active_crops(farmer_id)


@router.get("/farmer/{farmer_id}/harvest-ready", response_model=List[CropResponse])
async def get_harvest_ready(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get crops ready for harvest"""
    service = CropService(db)
    return await service.get_harvest_ready(farmer_id)


@router.get("/farmer/{farmer_id}/statistics")
async def get_crop_statistics(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get crop statistics for a farmer"""
    service = CropService(db)
    return await service.get_crop_statistics(farmer_id)

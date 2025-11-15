"""Crop/Culture data models"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class CropStatus(str, Enum):
    """Crop growing status"""
    PLANNED = "planned"
    PLANTED = "planted"
    GROWING = "growing"
    READY = "ready"
    HARVESTED = "harvested"


class CropBase(BaseModel):
    """Base crop information"""
    farmer_id: str
    crop_name: str
    parcel_id: Optional[str] = None
    area_hectares: float
    
    planting_date: date
    expected_harvest_date: date
    
    estimated_yield: Optional[float] = None  # tone/ha
    notes: Optional[str] = None


class CropCreate(CropBase):
    """Crop creation model"""
    pass


class CropUpdate(BaseModel):
    """Crop update model"""
    status: Optional[CropStatus] = None
    actual_harvest_date: Optional[date] = None
    actual_yield: Optional[float] = None
    notes: Optional[str] = None


class CropResponse(CropBase):
    """Crop response model"""
    id: str = Field(..., alias="_id")
    status: CropStatus
    actual_harvest_date: Optional[date] = None
    actual_yield: Optional[float] = None
    days_until_harvest: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class Crop(CropBase):
    """Internal crop model"""
    id: Optional[str] = Field(None, alias="_id")
    status: CropStatus = CropStatus.PLANNED
    actual_harvest_date: Optional[date] = None
    actual_yield: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

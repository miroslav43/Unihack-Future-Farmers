"""Harvest daily log data models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class EquipmentType(str, Enum):
    """Types of equipment used on farm"""
    TRACTOR = "Tractor"
    WHEAT_HARVESTER = "Wheat Harvester"
    SUNFLOWER_HARVESTER = "Sunflower Harvester"
    BEAN_HARVESTER = "Bean Harvester"
    TOMATO_HARVESTER = "Tomato Harvester"
    OTHER = "Other"


class EquipmentUsage(BaseModel):
    """Equipment usage record for a day"""
    equipment_type: str
    farmer_id: str  # Reference to farmer who used this equipment
    work_hours: float = Field(..., ge=0)
    fuel_consumed_liters: float = Field(..., ge=0)


class HarvestLogBase(BaseModel):
    """Base harvest log information"""
    date: date
    notes: Optional[str] = None
    
    # Crops - sown/harvested hectares
    wheat_sown_hectares: float = Field(default=0.0, ge=0)
    sunflower_harvested_hectares: float = Field(default=0.0, ge=0)
    beans_harvested_hectares: float = Field(default=0.0, ge=0)
    tomatoes_harvested_hectares: float = Field(default=0.0, ge=0)
    
    # Pricing
    oil_price_per_liter: float = Field(default=0.0, ge=0)
    
    # Equipment used
    equipment: List[EquipmentUsage] = []


class HarvestLogCreate(HarvestLogBase):
    """Harvest log creation model"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-15",
                "notes": "Normal work day",
                "wheat_sown_hectares": 8.5,
                "sunflower_harvested_hectares": 2.3,
                "beans_harvested_hectares": 1.2,
                "tomatoes_harvested_hectares": 0.5,
                "oil_price_per_liter": 6.5,
                "equipment": [
                    {
                        "equipment_type": "Tractor",
                        "farmer_id": "507f1f77bcf86cd799439011",
                        "work_hours": 8.0,
                        "fuel_consumed_liters": 45.5
                    }
                ]
            }
        }


class HarvestLogUpdate(BaseModel):
    """Harvest log update model - all fields optional"""
    notes: Optional[str] = None
    wheat_sown_hectares: Optional[float] = Field(None, ge=0)
    sunflower_harvested_hectares: Optional[float] = Field(None, ge=0)
    beans_harvested_hectares: Optional[float] = Field(None, ge=0)
    tomatoes_harvested_hectares: Optional[float] = Field(None, ge=0)
    oil_price_per_liter: Optional[float] = Field(None, ge=0)
    equipment: Optional[List[EquipmentUsage]] = None


class HarvestLogResponse(HarvestLogBase):
    """Harvest log response model"""
    id: str = Field(..., alias="_id")
    
    # Computed fields
    total_hectares_sown: float = 0.0
    total_hectares_harvested: float = 0.0
    total_work_hours: float = 0.0
    total_fuel_consumed: float = 0.0
    fuel_cost: float = 0.0
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439015",
                "date": "2025-11-15",
                "notes": "Normal work day",
                "wheat_sown_hectares": 8.57,
                "sunflower_harvested_hectares": 0.82,
                "beans_harvested_hectares": 1.23,
                "tomatoes_harvested_hectares": 0.62,
                "oil_price_per_liter": 6.81,
                "equipment": [
                    {
                        "equipment_type": "Tractor",
                        "farmer_id": "507f1f77bcf86cd799439011",
                        "work_hours": 0.71,
                        "fuel_consumed_liters": 16.3
                    }
                ],
                "total_hectares_sown": 8.57,
                "total_hectares_harvested": 2.67,
                "total_work_hours": 12.57,
                "total_fuel_consumed": 518.2,
                "fuel_cost": 3528.94,
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00"
            }
        }


class HarvestLog(HarvestLogBase):
    """Internal harvest log model with metadata"""
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


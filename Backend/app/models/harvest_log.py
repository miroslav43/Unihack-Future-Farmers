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
    
    # Hectare recoltate pentru fiecare cultura
    wheat_harvested_hectares: float = Field(default=0.0, ge=0)
    sunflower_harvested_hectares: float = Field(default=0.0, ge=0)
    beans_harvested_hectares: float = Field(default=0.0, ge=0)
    tomatoes_harvested_hectares: float = Field(default=0.0, ge=0)
    
    # Kilograme recoltate pentru fiecare cultura
    wheat_harvested_kg: float = Field(default=0.0, ge=0)
    sunflower_harvested_kg: float = Field(default=0.0, ge=0)
    beans_harvested_kg: float = Field(default=0.0, ge=0)
    tomatoes_harvested_kg: float = Field(default=0.0, ge=0)
    
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
                "wheat_harvested_hectares": 2.5,
                "sunflower_harvested_hectares": 1.3,
                "beans_harvested_hectares": 0.8,
                "tomatoes_harvested_hectares": 0.5,
                "wheat_harvested_kg": 10000,
                "sunflower_harvested_kg": 2600,
                "beans_harvested_kg": 1600,
                "tomatoes_harvested_kg": 25000,
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
    wheat_harvested_hectares: Optional[float] = Field(None, ge=0)
    sunflower_harvested_hectares: Optional[float] = Field(None, ge=0)
    beans_harvested_hectares: Optional[float] = Field(None, ge=0)
    tomatoes_harvested_hectares: Optional[float] = Field(None, ge=0)
    wheat_harvested_kg: Optional[float] = Field(None, ge=0)
    sunflower_harvested_kg: Optional[float] = Field(None, ge=0)
    beans_harvested_kg: Optional[float] = Field(None, ge=0)
    tomatoes_harvested_kg: Optional[float] = Field(None, ge=0)
    oil_price_per_liter: Optional[float] = Field(None, ge=0)
    equipment: Optional[List[EquipmentUsage]] = None


class HarvestLogResponse(HarvestLogBase):
    """Harvest log response model"""
    id: str = Field(..., alias="_id")
    
    # Computed fields
    total_hectares_harvested: float = 0.0
    total_kg_harvested: float = 0.0
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
                "wheat_harvested_hectares": 2.5,
                "sunflower_harvested_hectares": 1.3,
                "beans_harvested_hectares": 0.8,
                "tomatoes_harvested_hectares": 0.5,
                "wheat_harvested_kg": 10000,
                "sunflower_harvested_kg": 2600,
                "beans_harvested_kg": 1600,
                "tomatoes_harvested_kg": 25000,
                "oil_price_per_liter": 6.81,
                "equipment": [
                    {
                        "equipment_type": "Tractor",
                        "farmer_id": "507f1f77bcf86cd799439011",
                        "work_hours": 8.0,
                        "fuel_consumed_liters": 45.5
                    }
                ],
                "total_hectares_harvested": 5.1,
                "total_kg_harvested": 39200,
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


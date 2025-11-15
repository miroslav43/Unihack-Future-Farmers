"""Inventory/Stock data models"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProductCategory(str, Enum):
    """Product categories"""
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    GRAINS = "grains"
    DAIRY = "dairy"
    MEAT = "meat"
    OTHER = "other"


class InventoryBase(BaseModel):
    """Base inventory information"""
    farmer_id: str
    product_name: str
    category: ProductCategory
    quantity: float
    unit: str  # kg, tone, litri, bucati
    price_per_unit: float
    location: Optional[str] = None  # depozit, camp, etc.


class InventoryCreate(InventoryBase):
    """Inventory creation model"""
    pass


class InventoryUpdate(BaseModel):
    """Inventory update model"""
    quantity: Optional[float] = None
    price_per_unit: Optional[float] = None
    location: Optional[str] = None


class InventoryResponse(InventoryBase):
    """Inventory response model"""
    id: str = Field(..., alias="_id")
    total_value: float
    created_at: datetime
    updated_at: datetime
    last_updated_by: Optional[str] = None
    
    class Config:
        populate_by_name = True


class Inventory(InventoryBase):
    """Internal inventory model"""
    id: Optional[str] = Field(None, alias="_id")
    total_value: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_by: Optional[str] = None
    
    class Config:
        populate_by_name = True

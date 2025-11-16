from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryCreate(BaseModel):
    product_name: str
    category: str
    quantity: float
    unit: str
    price_per_unit: float
    is_available_for_sale: bool = False
    location: Optional[str] = None
    description: Optional[str] = None
    min_order_quantity: Optional[float] = None
    max_order_quantity: Optional[float] = None


class InventoryUpdate(BaseModel):
    product_name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None
    is_available_for_sale: Optional[bool] = None
    location: Optional[str] = None
    description: Optional[str] = None
    min_order_quantity: Optional[float] = None
    max_order_quantity: Optional[float] = None


class InventoryResponse(BaseModel):
    id: str = Field(..., alias="_id")  # Use "id" internally, serialize as "_id"
    farmer_id: str
    product_name: str
    category: str
    quantity: float
    unit: str
    price_per_unit: float
    total_value: float
    is_available_for_sale: bool
    location: Optional[str] = None
    description: Optional[str] = None
    min_order_quantity: Optional[float] = None
    max_order_quantity: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

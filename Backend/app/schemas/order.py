from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemCreate(BaseModel):
    inventory_id: str
    quantity: float


class OrderCreate(BaseModel):
    farmer_id: str
    items: List[OrderItemCreate]
    buyer_message: Optional[str] = None
    expected_delivery_date: Optional[str] = None


class OrderItemResponse(BaseModel):
    inventory_id: str
    product_name: str
    quantity: float
    unit: str
    price_per_unit: float
    total: float


class OrderResponse(BaseModel):
    id: str = Field(..., alias="_id")
    buyer_id: str
    buyer_name: str
    farmer_id: str
    farmer_name: str
    items: List[OrderItemResponse]
    total_amount: float
    status: str
    buyer_message: Optional[str] = None
    farmer_response: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class OrderUpdate(BaseModel):
    farmer_response: Optional[str] = None
    status: Optional[str] = None


class AcceptOrderResponse(BaseModel):
    message: str
    order_id: str
    contract_id: str


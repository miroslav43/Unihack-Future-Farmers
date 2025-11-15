r"""Order/Sales data models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Individual item in order"""
    product_name: str
    quantity: float
    unit: str  # kg, tone, bucati, etc.
    price_per_unit: float
    total_price: float


class OrderBase(BaseModel):
    """Base order information"""
    farmer_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    
    items: List[OrderItem]
    total_amount: float
    
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation model"""
    pass


class OrderUpdate(BaseModel):
    """Order update model"""
    status: Optional[OrderStatus] = None
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response model"""
    id: str = Field(..., alias="_id")
    order_number: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class Order(OrderBase):
    """Internal order model"""
    id: Optional[str] = Field(None, alias="_id")
    order_number: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

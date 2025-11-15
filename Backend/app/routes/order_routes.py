"""Order API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from ..models.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatus
from ..services.order_service import OrderService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new order"""
    service = OrderService(db)
    return await service.create_order(order_data)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get order by ID"""
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@router.get("/farmer/{farmer_id}", response_model=List[OrderResponse])
async def list_farmer_orders(
    farmer_id: str,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List orders for a farmer"""
    service = OrderService(db)
    return await service.list_farmer_orders(
        farmer_id=farmer_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update order"""
    service = OrderService(db)
    updated_order = await service.update_order(order_id, order_update)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return updated_order


@router.get("/farmer/{farmer_id}/today", response_model=List[OrderResponse])
async def get_today_orders(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get today's orders for a farmer"""
    service = OrderService(db)
    return await service.get_today_orders(farmer_id)


@router.get("/farmer/{farmer_id}/statistics")
async def get_orders_statistics(
    farmer_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get order statistics for a farmer"""
    service = OrderService(db)
    return await service.get_orders_statistics(
        farmer_id=farmer_id,
        start_date=start_date,
        end_date=end_date
    )

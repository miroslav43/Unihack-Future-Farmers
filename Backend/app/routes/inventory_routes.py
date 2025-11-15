"""Inventory API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse, ProductCategory
)
from ..services.inventory_service import InventoryService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    inventory_data: InventoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new inventory item"""
    service = InventoryService(db)
    return await service.create_inventory_item(inventory_data)


@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inventory item by ID"""
    service = InventoryService(db)
    item = await service.get_inventory_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found"
        )
    return item


@router.get("/farmer/{farmer_id}", response_model=List[InventoryResponse])
async def list_farmer_inventory(
    farmer_id: str,
    category: Optional[ProductCategory] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List inventory items for a farmer"""
    service = InventoryService(db)
    return await service.list_farmer_inventory(
        farmer_id=farmer_id,
        category=category
    )


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: str,
    inventory_update: InventoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update inventory item"""
    service = InventoryService(db)
    updated_item = await service.update_inventory_item(item_id, inventory_update)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found"
        )
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete inventory item"""
    service = InventoryService(db)
    deleted = await service.delete_inventory_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with ID {item_id} not found"
        )


@router.get("/farmer/{farmer_id}/value")
async def get_inventory_value(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get total inventory value for farmer"""
    service = InventoryService(db)
    total_value = await service.get_inventory_value(farmer_id)
    return {"farmer_id": farmer_id, "total_value": total_value}


@router.get("/farmer/{farmer_id}/by-category")
async def get_inventory_by_category(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inventory summary by category"""
    service = InventoryService(db)
    return await service.get_inventory_by_category(farmer_id)

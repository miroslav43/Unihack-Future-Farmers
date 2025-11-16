from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.database import get_db
from app.dependencies import get_current_user, require_farmer
from app.models.user import User, FarmerProfile
from app.models.inventory import InventoryItem
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_model=List[InventoryResponse])
async def get_all_inventory(db: AsyncSession = Depends(get_db)):
    """Get all inventory items"""
    result = await db.execute(select(InventoryItem))
    items = result.scalars().all()
    
    return [
        InventoryResponse(
            id=str(item.id),
            farmer_id=str(item.farmer_id),
            product_name=item.product_name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            price_per_unit=item.price_per_unit,
            total_value=item.quantity * item.price_per_unit,
            is_available_for_sale=item.is_available_for_sale,
            location=item.location,
            description=item.description,
            min_order_quantity=item.min_order_quantity,
            max_order_quantity=item.max_order_quantity,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        for item in items
    ]


@router.get("/available", response_model=List[InventoryResponse])
async def get_available_inventory(
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get available inventory items with optional filters"""
    query = select(InventoryItem).where(InventoryItem.is_available_for_sale == True)
    
    if category:
        query = query.where(InventoryItem.category == category)
    
    if min_price is not None:
        query = query.where(InventoryItem.price_per_unit >= min_price)
    
    if max_price is not None:
        query = query.where(InventoryItem.price_per_unit <= max_price)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [
        InventoryResponse(
            id=str(item.id),
            farmer_id=str(item.farmer_id),
            product_name=item.product_name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            price_per_unit=item.price_per_unit,
            total_value=item.quantity * item.price_per_unit,
            is_available_for_sale=item.is_available_for_sale,
            location=item.location,
            description=item.description,
            min_order_quantity=item.min_order_quantity,
            max_order_quantity=item.max_order_quantity,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        for item in items
    ]


@router.get("/farmer/{farmer_id}", response_model=List[InventoryResponse])
async def get_inventory_by_farmer(
    farmer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get inventory by farmer ID"""
    from uuid import UUID
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.farmer_id == UUID(farmer_id))
    )
    items = result.scalars().all()
    
    return [
        InventoryResponse(
            id=str(item.id),
            farmer_id=str(item.farmer_id),
            product_name=item.product_name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            price_per_unit=item.price_per_unit,
            total_value=item.quantity * item.price_per_unit,
            is_available_for_sale=item.is_available_for_sale,
            location=item.location,
            description=item.description,
            min_order_quantity=item.min_order_quantity,
            max_order_quantity=item.max_order_quantity,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        for item in items
    ]


@router.post("/", response_model=InventoryResponse)
async def create_inventory_item(
    item_data: InventoryCreate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Create inventory item (farmer only)"""
    # Get farmer profile to use farmer's ID
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Please create your profile first."
        )
    
    # Create inventory item
    item = InventoryItem(
        farmer_id=farmer.id,
        **item_data.model_dump()
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return InventoryResponse(
        _id=str(item.id),
        farmer_id=str(item.farmer_id),
        product_name=item.product_name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        price_per_unit=item.price_per_unit,
        total_value=item.quantity * item.price_per_unit,
        is_available_for_sale=item.is_available_for_sale,
        location=item.location,
        description=item.description,
        min_order_quantity=item.min_order_quantity,
        max_order_quantity=item.max_order_quantity,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: str,
    item_data: InventoryUpdate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Update inventory item (farmer only, ownership check)"""
    from uuid import UUID
    # Get farmer profile
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found"
        )
    
    # Check if item exists and belongs to current farmer
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == UUID(item_id))
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    if item.farmer_id != farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )
    
    # Update item
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    
    return InventoryResponse(
        _id=str(item.id),
        farmer_id=str(item.farmer_id),
        product_name=item.product_name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        price_per_unit=item.price_per_unit,
        total_value=item.quantity * item.price_per_unit,
        is_available_for_sale=item.is_available_for_sale,
        location=item.location,
        description=item.description,
        min_order_quantity=item.min_order_quantity,
        max_order_quantity=item.max_order_quantity,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Delete inventory item (farmer only, ownership check)"""
    from uuid import UUID
    # Get farmer profile
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found"
        )
    
    # Check if item exists and belongs to current farmer
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == UUID(item_id))
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    if item.farmer_id != farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )
    
    # Delete item
    await db.delete(item)
    await db.commit()
    
    return {"message": "Item deleted successfully"}

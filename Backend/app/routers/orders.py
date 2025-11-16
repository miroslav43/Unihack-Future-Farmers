from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderUpdate,
    AcceptOrderResponse
)
from app.database import get_db
from app.dependencies import get_current_user, require_buyer, require_farmer
from app.models.user import User, FarmerProfile, BuyerProfile
from app.models.order import Order, OrderStatus
from app.models.inventory import InventoryItem
from app.models.contract import Contract, ContractStatus
from app.services.contract_service import generate_contract_hash
from datetime import datetime
from typing import List, Optional
from uuid import UUID

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order (buyer only) - prices are snapshot at order time"""
    # Get buyer profile
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    buyer_profile = result.scalar_one_or_none()
    
    if not buyer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer profile not found. Please complete your profile setup."
        )
    
    # Get farmer profile
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.id == UUID(order_data.farmer_id))
    )
    farmer_profile = result.scalar_one_or_none()
    
    if not farmer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Fetch inventory items and snapshot prices
    order_items = []
    total_amount = 0.0
    
    for item_data in order_data.items:
        result = await db.execute(
            select(InventoryItem).where(InventoryItem.id == UUID(item_data.inventory_id))
        )
        inventory_item = result.scalar_one_or_none()
        
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item {item_data.inventory_id} not found"
            )
        
        if inventory_item.farmer_id != UUID(order_data.farmer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item {inventory_item.product_name} does not belong to selected farmer"
            )
        
        if not inventory_item.is_available_for_sale:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item {inventory_item.product_name} is not available for sale"
            )
        
        if item_data.quantity > inventory_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity for {inventory_item.product_name} exceeds available stock"
            )
        
        # Snapshot the price at order time
        item_total = item_data.quantity * inventory_item.price_per_unit
        total_amount += item_total
        
        order_items.append({
            "inventory_id": str(inventory_item.id),
            "product_name": inventory_item.product_name,
            "quantity": item_data.quantity,
            "unit": inventory_item.unit,
            "price_per_unit": inventory_item.price_per_unit,
            "total": item_total
        })
    
    # Create order
    order = Order(
        buyer_id=buyer_profile.id,
        buyer_name=buyer_profile.company_name,
        farmer_id=farmer_profile.id,
        farmer_name=farmer_profile.farm_name,
        items=order_items,
        total_amount=total_amount,
        status=OrderStatus.PENDING.value,
        buyer_message=order_data.buyer_message,
        expected_delivery_date=order_data.expected_delivery_date
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse(
        id=str(order.id),
        buyer_id=str(order.buyer_id),
        buyer_name=order.buyer_name,
        farmer_id=str(order.farmer_id),
        farmer_name=order.farmer_name,
        items=[OrderItemResponse(**item) for item in order.items],
        total_amount=order.total_amount,
        status=order.status,
        buyer_message=order.buyer_message,
        farmer_response=order.farmer_response,
        expected_delivery_date=order.expected_delivery_date,
        created_at=order.created_at,
        updated_at=order.updated_at
    )


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get orders filtered by role (buyer sees their orders, farmer sees orders for them)"""
    if current_user.role == "buyer":
        # Get buyer profile
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer:
            return []
        
        query = select(Order).where(Order.buyer_id == buyer.id).order_by(Order.created_at.desc())
    
    elif current_user.role == "farmer":
        # Get farmer profile
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer:
            return []
        
        query = select(Order).where(Order.farmer_id == farmer.id).order_by(Order.created_at.desc())
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role"
        )
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return [
        OrderResponse(
            id=str(order.id),
            buyer_id=str(order.buyer_id),
            buyer_name=order.buyer_name,
            farmer_id=str(order.farmer_id),
            farmer_name=order.farmer_name,
            items=[OrderItemResponse(**item) for item in order.items],
            total_amount=order.total_amount,
            status=order.status,
            buyer_message=order.buyer_message,
            farmer_response=order.farmer_response,
            expected_delivery_date=order.expected_delivery_date,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get single order with ownership check"""
    result = await db.execute(
        select(Order).where(Order.id == UUID(order_id))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify user has access to this order
    if current_user.role == "buyer":
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer or order.buyer_id != buyer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )
    elif current_user.role == "farmer":
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer or order.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )
    
    return OrderResponse(
        id=str(order.id),
        buyer_id=str(order.buyer_id),
        buyer_name=order.buyer_name,
        farmer_id=str(order.farmer_id),
        farmer_name=order.farmer_name,
        items=[OrderItemResponse(**item) for item in order.items],
        total_amount=order.total_amount,
        status=order.status,
        buyer_message=order.buyer_message,
        farmer_response=order.farmer_response,
        expected_delivery_date=order.expected_delivery_date,
        created_at=order.created_at,
        updated_at=order.updated_at
    )


@router.put("/{order_id}/accept", response_model=AcceptOrderResponse)
async def accept_order(
    order_id: str,
    order_update: Optional[OrderUpdate] = None,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Farmer accepts order → status=ACCEPTED → auto-create contract"""
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
    
    # Get order
    result = await db.execute(
        select(Order).where(Order.id == UUID(order_id))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify farmer owns this order
    if order.farmer_id != farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to accept this order"
        )
    
    # Check order status
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept order with status: {order.status}"
        )
    
    # Update order status
    order.status = OrderStatus.ACCEPTED.value
    if order_update and order_update.farmer_response:
        order.farmer_response = order_update.farmer_response
    order.updated_at = datetime.utcnow()
    
    # Auto-create contract
    contract_items = []
    for item in order.items:
        contract_items.append({
            "product_name": item["product_name"],
            "quantity": item["quantity"],
            "unit": item["unit"],
            "price_per_unit": item["price_per_unit"],
            "total": item["total"]
        })
    
    # Generate contract hash
    hash_data = {
        "buyer_id": str(order.buyer_id),
        "farmer_id": str(order.farmer_id),
        "items": contract_items,
        "total_amount": order.total_amount,
        "delivery_date": order.expected_delivery_date
    }
    contract_hash = generate_contract_hash(hash_data)
    
    # Create contract
    contract = Contract(
        buyer_id=order.buyer_id,
        buyer_name=order.buyer_name,
        farmer_id=order.farmer_id,
        farmer_name=order.farmer_name,
        items=contract_items,
        total_amount=order.total_amount,
        delivery_date=order.expected_delivery_date,
        terms=f"Contract auto-generated from Order #{str(order.id)[:8]}",
        notes=f"Buyer message: {order.buyer_message or 'None'}. Farmer response: {order.farmer_response or 'None'}",
        status=ContractStatus.PENDING.value,
        contract_hash=contract_hash
    )
    
    db.add(contract)
    await db.commit()
    await db.refresh(order)
    await db.refresh(contract)
    
    return AcceptOrderResponse(
        message="Order accepted successfully. Contract created.",
        order_id=str(order.id),
        contract_id=str(contract.id)
    )


@router.put("/{order_id}/reject")
async def reject_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: User = Depends(require_farmer),
    db: AsyncSession = Depends(get_db)
):
    """Farmer rejects order → status=REJECTED + farmer_response"""
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
    
    # Get order
    result = await db.execute(
        select(Order).where(Order.id == UUID(order_id))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify farmer owns this order
    if order.farmer_id != farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this order"
        )
    
    # Check order status
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject order with status: {order.status}"
        )
    
    # Require rejection reason
    if not order_update.farmer_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer response (rejection reason) is required"
        )
    
    # Update order
    order.status = OrderStatus.REJECTED.value
    order.farmer_response = order_update.farmer_response
    order.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": "Order rejected successfully",
        "order_id": str(order.id)
    }


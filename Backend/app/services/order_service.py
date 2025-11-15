"""Order service - business logic for orders/sales"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from ..models.order import Order, OrderCreate, OrderUpdate, OrderResponse, OrderStatus


class OrderService:
    """Service for managing orders and sales"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.orders
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Create a new order"""
        order_dict = order_data.model_dump()
        
        # Generate order number
        order_dict["order_number"] = self._generate_order_number()
        order_dict["status"] = OrderStatus.PENDING
        order_dict["created_at"] = datetime.utcnow()
        order_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(order_dict)
        
        created_order = await self.collection.find_one({"_id": result.inserted_id})
        created_order["_id"] = str(created_order["_id"])
        
        return OrderResponse(**created_order)
    
    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Get order by ID"""
        if not ObjectId.is_valid(order_id):
            return None
        
        order = await self.collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            return None
        
        order["_id"] = str(order["_id"])
        return OrderResponse(**order)
    
    async def list_farmer_orders(
        self,
        farmer_id: str,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderResponse]:
        """List orders for a farmer with optional filters"""
        query = {"farmer_id": farmer_id}
        
        if status:
            query["status"] = status
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        orders = []
        
        async for order in cursor:
            order["_id"] = str(order["_id"])
            orders.append(OrderResponse(**order))
        
        return orders
    
    async def update_order(
        self,
        order_id: str,
        order_update: OrderUpdate
    ) -> Optional[OrderResponse]:
        """Update order"""
        if not ObjectId.is_valid(order_id):
            return None
        
        update_data = order_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_order(order_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # If status is delivered, set delivered_at
        if update_data.get("status") == OrderStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_order(order_id)
    
    async def get_today_orders(self, farmer_id: str) -> List[OrderResponse]:
        """Get today's orders"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return await self.list_farmer_orders(
            farmer_id=farmer_id,
            start_date=today_start,
            end_date=today_end
        )
    
    async def get_orders_count(
        self,
        farmer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count orders in date range"""
        query = {"farmer_id": farmer_id}
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        return await self.collection.count_documents(query)
    
    async def get_orders_statistics(
        self,
        farmer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get order statistics"""
        query = {"farmer_id": farmer_id}
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        # Aggregate statistics
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"},
                "avg_order_value": {"$avg": "$total_amount"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            return {
                "total_orders": stats["total_orders"],
                "total_revenue": round(stats["total_revenue"], 2),
                "avg_order_value": round(stats["avg_order_value"], 2)
            }
        
        return {
            "total_orders": 0,
            "total_revenue": 0.0,
            "avg_order_value": 0.0
        }
    
    @staticmethod
    def _generate_order_number() -> str:
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

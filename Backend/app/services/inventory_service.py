"""Inventory service - business logic for inventory management"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..models.inventory import (
    Inventory, InventoryCreate, InventoryUpdate, 
    InventoryResponse, ProductCategory
)


class InventoryService:
    """Service for managing inventory/stock"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.inventory
    
    async def create_inventory_item(
        self, 
        inventory_data: InventoryCreate
    ) -> InventoryResponse:
        """Create a new inventory item"""
        inventory_dict = inventory_data.model_dump()
        
        # Calculate total value
        inventory_dict["total_value"] = (
            inventory_dict["quantity"] * inventory_dict["price_per_unit"]
        )
        inventory_dict["created_at"] = datetime.utcnow()
        inventory_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(inventory_dict)
        
        created_item = await self.collection.find_one({"_id": result.inserted_id})
        created_item["_id"] = str(created_item["_id"])
        
        return InventoryResponse(**created_item)
    
    async def get_inventory_item(self, item_id: str) -> Optional[InventoryResponse]:
        """Get inventory item by ID"""
        if not ObjectId.is_valid(item_id):
            return None
        
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            return None
        
        item["_id"] = str(item["_id"])
        return InventoryResponse(**item)
    
    async def list_farmer_inventory(
        self,
        farmer_id: str,
        category: Optional[ProductCategory] = None
    ) -> List[InventoryResponse]:
        """List inventory items for a farmer"""
        query = {"farmer_id": farmer_id}
        
        if category:
            query["category"] = category
        
        cursor = self.collection.find(query).sort("product_name", 1)
        items = []
        
        async for item in cursor:
            item["_id"] = str(item["_id"])
            items.append(InventoryResponse(**item))
        
        return items
    
    async def update_inventory_item(
        self,
        item_id: str,
        inventory_update: InventoryUpdate
    ) -> Optional[InventoryResponse]:
        """Update inventory item"""
        if not ObjectId.is_valid(item_id):
            return None
        
        update_data = inventory_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_inventory_item(item_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Recalculate total value if quantity or price changed
        if "quantity" in update_data or "price_per_unit" in update_data:
            current_item = await self.collection.find_one({"_id": ObjectId(item_id)})
            if current_item:
                quantity = update_data.get("quantity", current_item.get("quantity", 0))
                price = update_data.get("price_per_unit", current_item.get("price_per_unit", 0))
                update_data["total_value"] = quantity * price
        
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_inventory_item(item_id)
    
    async def delete_inventory_item(self, item_id: str) -> bool:
        """Delete inventory item"""
        if not ObjectId.is_valid(item_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0
    
    async def get_inventory_value(self, farmer_id: str) -> float:
        """Get total inventory value for farmer"""
        pipeline = [
            {"$match": {"farmer_id": farmer_id}},
            {"$group": {
                "_id": None,
                "total_value": {"$sum": "$total_value"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            return round(result[0]["total_value"], 2)
        
        return 0.0
    
    async def get_inventory_by_category(self, farmer_id: str) -> dict:
        """Get inventory summary by category"""
        pipeline = [
            {"$match": {"farmer_id": farmer_id}},
            {"$group": {
                "_id": "$category",
                "total_quantity": {"$sum": "$quantity"},
                "total_value": {"$sum": "$total_value"},
                "item_count": {"$sum": 1}
            }}
        ]
        
        result = {}
        async for doc in self.collection.aggregate(pipeline):
            result[doc["_id"]] = {
                "total_quantity": doc["total_quantity"],
                "total_value": round(doc["total_value"], 2),
                "item_count": doc["item_count"]
            }
        
        return result

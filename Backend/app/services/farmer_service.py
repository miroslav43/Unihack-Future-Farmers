"""Farmer service - business logic for farmer operations"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..models.farmer import Farmer, FarmerCreate, FarmerUpdate, FarmerResponse


class FarmerService:
    """Service for managing farmer data"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.farmers
    
    async def create_farmer(self, farmer_data: FarmerCreate) -> FarmerResponse:
        """Create a new farmer record"""
        # Check if CNP already exists
        existing = await self.collection.find_one({"cnp": farmer_data.cnp})
        if existing:
            raise ValueError(f"Farmer with CNP {farmer_data.cnp} already exists")
        
        # Create farmer document
        farmer_dict = farmer_data.model_dump()
        farmer_dict["created_at"] = datetime.utcnow()
        farmer_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(farmer_dict)
        
        # Retrieve and return created farmer
        created_farmer = await self.collection.find_one({"_id": result.inserted_id})
        created_farmer["_id"] = str(created_farmer["_id"])
        
        return FarmerResponse(**created_farmer)
    
    async def get_farmer(self, farmer_id: str) -> Optional[FarmerResponse]:
        """Get farmer by ID"""
        if not ObjectId.is_valid(farmer_id):
            return None
        
        farmer = await self.collection.find_one({"_id": ObjectId(farmer_id)})
        if not farmer:
            return None
        
        farmer["_id"] = str(farmer["_id"])
        return FarmerResponse(**farmer)
    
    async def get_farmer_by_cnp(self, cnp: str) -> Optional[FarmerResponse]:
        """Get farmer by CNP"""
        farmer = await self.collection.find_one({"cnp": cnp})
        if not farmer:
            return None
        
        farmer["_id"] = str(farmer["_id"])
        return FarmerResponse(**farmer)
    
    async def list_farmers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        county: Optional[str] = None
    ) -> List[FarmerResponse]:
        """List farmers with pagination and optional filtering"""
        query = {}
        if county:
            query["county"] = county
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        farmers = []
        
        async for farmer in cursor:
            farmer["_id"] = str(farmer["_id"])
            farmers.append(FarmerResponse(**farmer))
        
        return farmers
    
    async def update_farmer(
        self, 
        farmer_id: str, 
        farmer_update: FarmerUpdate
    ) -> Optional[FarmerResponse]:
        """Update farmer information"""
        if not ObjectId.is_valid(farmer_id):
            return None
        
        # Only update provided fields
        update_data = farmer_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_farmer(farmer_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(farmer_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_farmer(farmer_id)
    
    async def delete_farmer(self, farmer_id: str) -> bool:
        """Delete farmer record"""
        if not ObjectId.is_valid(farmer_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(farmer_id)})
        return result.deleted_count > 0
    
    async def get_farmer_statistics(self) -> dict:
        """Get overall farmer statistics"""
        total = await self.collection.count_documents({})
        
        # Experience level distribution
        pipeline = [
            {"$group": {
                "_id": "$experience_level",
                "count": {"$sum": 1}
            }}
        ]
        experience_dist = {}
        async for doc in self.collection.aggregate(pipeline):
            experience_dist[doc["_id"]] = doc["count"]
        
        # Average land area
        avg_land = await self.collection.aggregate([
            {"$group": {
                "_id": None,
                "avg_land": {"$avg": "$total_land_area"}
            }}
        ]).to_list(1)
        
        return {
            "total_farmers": total,
            "experience_distribution": experience_dist,
            "average_land_area": avg_land[0]["avg_land"] if avg_land else 0.0
        }

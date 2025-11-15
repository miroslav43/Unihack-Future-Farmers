"""Crop service - business logic for crop management"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, date

from ..models.crop import Crop, CropCreate, CropUpdate, CropResponse, CropStatus


class CropService:
    """Service for managing crops and plantings"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.crops
    
    async def create_crop(self, crop_data: CropCreate) -> CropResponse:
        """Create a new crop record"""
        crop_dict = crop_data.model_dump()
        
        # Convert date to datetime for MongoDB compatibility
        if isinstance(crop_dict.get("planting_date"), date) and not isinstance(crop_dict.get("planting_date"), datetime):
            crop_dict["planting_date"] = datetime.combine(crop_dict["planting_date"], datetime.min.time())
        if isinstance(crop_dict.get("expected_harvest_date"), date) and not isinstance(crop_dict.get("expected_harvest_date"), datetime):
            crop_dict["expected_harvest_date"] = datetime.combine(crop_dict["expected_harvest_date"], datetime.min.time())
        
        crop_dict["status"] = CropStatus.PLANNED
        crop_dict["created_at"] = datetime.utcnow()
        crop_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(crop_dict)
        
        created_crop = await self.collection.find_one({"_id": result.inserted_id})
        created_crop["_id"] = str(created_crop["_id"])
        
        # Add days until harvest
        created_crop = self._add_days_until_harvest(created_crop)
        
        return CropResponse(**created_crop)
    
    async def get_crop(self, crop_id: str) -> Optional[CropResponse]:
        """Get crop by ID"""
        if not ObjectId.is_valid(crop_id):
            return None
        
        crop = await self.collection.find_one({"_id": ObjectId(crop_id)})
        if not crop:
            return None
        
        crop["_id"] = str(crop["_id"])
        crop = self._add_days_until_harvest(crop)
        
        return CropResponse(**crop)
    
    async def list_farmer_crops(
        self,
        farmer_id: str,
        status: Optional[CropStatus] = None
    ) -> List[CropResponse]:
        """List crops for a farmer"""
        query = {"farmer_id": farmer_id}
        
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort("planting_date", -1)
        crops = []
        
        async for crop in cursor:
            crop["_id"] = str(crop["_id"])
            crop = self._add_days_until_harvest(crop)
            crops.append(CropResponse(**crop))
        
        return crops
    
    async def update_crop(
        self,
        crop_id: str,
        crop_update: CropUpdate
    ) -> Optional[CropResponse]:
        """Update crop"""
        if not ObjectId.is_valid(crop_id):
            return None
        
        update_data = crop_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_crop(crop_id)
        
        # Convert dates for MongoDB
        if "actual_harvest_date" in update_data and isinstance(update_data["actual_harvest_date"], date):
            if not isinstance(update_data["actual_harvest_date"], datetime):
                update_data["actual_harvest_date"] = datetime.combine(update_data["actual_harvest_date"], datetime.min.time())
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(crop_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_crop(crop_id)
    
    async def delete_crop(self, crop_id: str) -> bool:
        """Delete crop"""
        if not ObjectId.is_valid(crop_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(crop_id)})
        return result.deleted_count > 0
    
    async def get_active_crops(self, farmer_id: str) -> List[CropResponse]:
        """Get active (planted/growing) crops"""
        query = {
            "farmer_id": farmer_id,
            "status": {"$in": [CropStatus.PLANTED, CropStatus.GROWING]}
        }
        
        cursor = self.collection.find(query).sort("expected_harvest_date", 1)
        crops = []
        
        async for crop in cursor:
            crop["_id"] = str(crop["_id"])
            crop = self._add_days_until_harvest(crop)
            crops.append(CropResponse(**crop))
        
        return crops
    
    async def get_harvest_ready(self, farmer_id: str) -> List[CropResponse]:
        """Get crops ready for harvest"""
        today = date.today()
        
        query = {
            "farmer_id": farmer_id,
            "status": {"$in": [CropStatus.GROWING, CropStatus.READY]},
            "expected_harvest_date": {"$lte": today}
        }
        
        cursor = self.collection.find(query).sort("expected_harvest_date", 1)
        crops = []
        
        async for crop in cursor:
            crop["_id"] = str(crop["_id"])
            crop = self._add_days_until_harvest(crop)
            
            # Auto-update status to READY if not already
            if crop["status"] != CropStatus.READY:
                await self.collection.update_one(
                    {"_id": ObjectId(crop["_id"])},
                    {"$set": {"status": CropStatus.READY}}
                )
                crop["status"] = CropStatus.READY
            
            crops.append(CropResponse(**crop))
        
        return crops
    
    async def get_crop_statistics(self, farmer_id: str) -> dict:
        """Get crop statistics"""
        # Count by status
        pipeline = [
            {"$match": {"farmer_id": farmer_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_area": {"$sum": "$area_hectares"}
            }}
        ]
        
        status_stats = {}
        async for doc in self.collection.aggregate(pipeline):
            status_stats[doc["_id"]] = {
                "count": doc["count"],
                "total_area": round(doc["total_area"], 2)
            }
        
        # Total area planted
        total_pipeline = [
            {"$match": {"farmer_id": farmer_id}},
            {"$group": {
                "_id": None,
                "total_area": {"$sum": "$area_hectares"},
                "total_crops": {"$sum": 1}
            }}
        ]
        
        total = await self.collection.aggregate(total_pipeline).to_list(1)
        
        return {
            "by_status": status_stats,
            "total_area": round(total[0]["total_area"], 2) if total else 0.0,
            "total_crops": total[0]["total_crops"] if total else 0
        }
    
    @staticmethod
    def _add_days_until_harvest(crop_dict: dict) -> dict:
        """Calculate and add days until harvest"""
        if crop_dict.get("status") == CropStatus.HARVESTED:
            crop_dict["days_until_harvest"] = None
            return crop_dict
        
        expected_date = crop_dict.get("expected_harvest_date")
        if expected_date:
            # Convert to date for comparison
            if isinstance(expected_date, str):
                expected_date = datetime.strptime(expected_date, "%Y-%m-%d").date()
            elif isinstance(expected_date, datetime):
                expected_date = expected_date.date()
            
            today = date.today()
            delta = (expected_date - today).days
            crop_dict["days_until_harvest"] = delta
        else:
            crop_dict["days_until_harvest"] = None
        
        return crop_dict

"""Harvest log service - business logic for daily harvest operations"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, date, timedelta

from ..models.harvest_log import (
    HarvestLog, HarvestLogCreate, HarvestLogUpdate, 
    HarvestLogResponse, EquipmentUsage
)


class HarvestService:
    """Service for managing harvest logs and daily operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.harvest_logs
    
    async def create_harvest_log(
        self, 
        harvest_data: HarvestLogCreate
    ) -> HarvestLogResponse:
        """Create a new harvest log entry"""
        harvest_dict = harvest_data.model_dump()
        
        # Validate all farmer_ids in equipment exist in farmers collection
        if harvest_dict.get("equipment"):
            await self._validate_worker_ids(harvest_dict["equipment"])
        
        # Convert date to datetime for MongoDB
        if isinstance(harvest_dict.get("date"), date):
            if not isinstance(harvest_dict.get("date"), datetime):
                harvest_dict["date"] = datetime.combine(harvest_dict["date"], datetime.min.time())
        
        harvest_dict["created_at"] = datetime.utcnow()
        harvest_dict["updated_at"] = datetime.utcnow()
        
        # Convert equipment list to dicts
        if "equipment" in harvest_dict:
            harvest_dict["equipment"] = [
                eq.dict() if hasattr(eq, 'dict') else eq 
                for eq in harvest_dict["equipment"]
            ]
        
        result = await self.collection.insert_one(harvest_dict)
        
        created_log = await self.collection.find_one({"_id": result.inserted_id})
        created_log["_id"] = str(created_log["_id"])
        
        # Add computed fields
        created_log = self._add_computed_fields(created_log)
        
        return HarvestLogResponse(**created_log)
    
    async def get_harvest_log(self, log_id: str) -> Optional[HarvestLogResponse]:
        """Get harvest log by ID"""
        if not ObjectId.is_valid(log_id):
            return None
        
        log = await self.collection.find_one({"_id": ObjectId(log_id)})
        if not log:
            return None
        
        log["_id"] = str(log["_id"])
        log = self._add_computed_fields(log)
        
        return HarvestLogResponse(**log)
    
    async def get_harvest_log_by_date(
        self, 
        target_date: date
    ) -> Optional[HarvestLogResponse]:
        """Get harvest log for a specific date"""
        # Convert date to datetime range
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        
        log = await self.collection.find_one({
            "date": {"$gte": start_dt, "$lt": end_dt}
        })
        
        if not log:
            return None
        
        log["_id"] = str(log["_id"])
        log = self._add_computed_fields(log)
        
        return HarvestLogResponse(**log)
    
    async def list_harvest_logs(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[HarvestLogResponse]:
        """List harvest logs with optional date range filtering"""
        query = {}
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                query["date"]["$lte"] = datetime.combine(end_date, datetime.max.time())
        
        cursor = self.collection.find(query).sort("date", -1).skip(skip).limit(limit)
        logs = []
        
        async for log in cursor:
            log["_id"] = str(log["_id"])
            log = self._add_computed_fields(log)
            logs.append(HarvestLogResponse(**log))
        
        return logs
    
    async def update_harvest_log(
        self,
        log_id: str,
        harvest_update: HarvestLogUpdate
    ) -> Optional[HarvestLogResponse]:
        """Update harvest log"""
        if not ObjectId.is_valid(log_id):
            return None
        
        update_data = harvest_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_harvest_log(log_id)
        
        # Validate farmer_ids if equipment is being updated
        if "equipment" in update_data and update_data["equipment"]:
            await self._validate_worker_ids(update_data["equipment"])
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Convert equipment if present
        if "equipment" in update_data:
            update_data["equipment"] = [
                eq.dict() if hasattr(eq, 'dict') else eq 
                for eq in update_data["equipment"]
            ]
        
        result = await self.collection.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_harvest_log(log_id)
    
    async def delete_harvest_log(self, log_id: str) -> bool:
        """Delete harvest log"""
        if not ObjectId.is_valid(log_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(log_id)})
        return result.deleted_count > 0
    
    async def get_harvest_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get harvest statistics for a date range"""
        query = {}
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                query["date"]["$lte"] = datetime.combine(end_date, datetime.max.time())
        
        # Aggregate statistics
        pipeline = [
            {"$match": query},
            {"$unwind": {"path": "$equipment", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": None,
                "total_days": {"$sum": 1},
                "total_wheat_harvested": {"$sum": "$wheat_harvested_hectares"},
                "total_sunflower_harvested": {"$sum": "$sunflower_harvested_hectares"},
                "total_beans_harvested": {"$sum": "$beans_harvested_hectares"},
                "total_tomatoes_harvested": {"$sum": "$tomatoes_harvested_hectares"},
                "total_wheat_kg": {"$sum": "$wheat_harvested_kg"},
                "total_sunflower_kg": {"$sum": "$sunflower_harvested_kg"},
                "total_beans_kg": {"$sum": "$beans_harvested_kg"},
                "total_tomatoes_kg": {"$sum": "$tomatoes_harvested_kg"},
                "total_work_hours": {"$sum": "$equipment.work_hours"},
                "total_fuel_consumed": {"$sum": "$equipment.fuel_consumed_liters"},
                "avg_oil_price": {"$avg": "$oil_price_per_liter"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            total_fuel = stats["total_fuel_consumed"] or 0
            avg_price = stats["avg_oil_price"] or 0
            
            return {
                "total_days": stats["total_days"],
                "total_wheat_harvested_hectares": round(stats["total_wheat_harvested"] or 0, 2),
                "total_sunflower_harvested_hectares": round(stats["total_sunflower_harvested"] or 0, 2),
                "total_beans_harvested_hectares": round(stats["total_beans_harvested"] or 0, 2),
                "total_tomatoes_harvested_hectares": round(stats["total_tomatoes_harvested"] or 0, 2),
                "total_wheat_harvested_kg": round(stats["total_wheat_kg"] or 0, 2),
                "total_sunflower_harvested_kg": round(stats["total_sunflower_kg"] or 0, 2),
                "total_beans_harvested_kg": round(stats["total_beans_kg"] or 0, 2),
                "total_tomatoes_harvested_kg": round(stats["total_tomatoes_kg"] or 0, 2),
                "total_work_hours": round(stats["total_work_hours"] or 0, 2),
                "total_fuel_consumed_liters": round(total_fuel, 2),
                "total_fuel_cost": round(total_fuel * avg_price, 2),
                "average_oil_price_per_liter": round(avg_price, 2)
            }
        
        return {
            "total_days": 0,
            "total_wheat_harvested_hectares": 0.0,
            "total_sunflower_harvested_hectares": 0.0,
            "total_beans_harvested_hectares": 0.0,
            "total_tomatoes_harvested_hectares": 0.0,
            "total_wheat_harvested_kg": 0.0,
            "total_sunflower_harvested_kg": 0.0,
            "total_beans_harvested_kg": 0.0,
            "total_tomatoes_harvested_kg": 0.0,
            "total_work_hours": 0.0,
            "total_fuel_consumed_liters": 0.0,
            "total_fuel_cost": 0.0,
            "average_oil_price_per_liter": 0.0
        }
    
    async def get_equipment_usage_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get equipment usage statistics"""
        query = {}
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                query["date"]["$lte"] = datetime.combine(end_date, datetime.max.time())
        
        pipeline = [
            {"$match": query},
            {"$unwind": "$equipment"},
            {"$group": {
                "_id": "$equipment.equipment_type",
                "total_hours": {"$sum": "$equipment.work_hours"},
                "total_fuel": {"$sum": "$equipment.fuel_consumed_liters"},
                "usage_count": {"$sum": 1}
            }},
            {"$sort": {"total_hours": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(None)
        
        equipment_stats = {}
        for doc in results:
            equipment_stats[doc["_id"]] = {
                "total_hours": round(doc["total_hours"], 2),
                "total_fuel_liters": round(doc["total_fuel"], 2),
                "usage_count": doc["usage_count"],
                "avg_hours_per_use": round(doc["total_hours"] / doc["usage_count"], 2) if doc["usage_count"] > 0 else 0
            }
        
        return equipment_stats
    
    async def _validate_worker_ids(self, equipment_list: List) -> None:
        """Validate that all farmer_ids in equipment exist in farmers collection"""
        farmer_ids = []
        for eq in equipment_list:
            if isinstance(eq, dict):
                farmer_id = eq.get("farmer_id")
            else:
                farmer_id = getattr(eq, "farmer_id", None)
            
            if farmer_id is not None:
                farmer_ids.append(farmer_id)
        
        if not farmer_ids:
            return
        
        # Validate ObjectIds
        for fid in farmer_ids:
            if not ObjectId.is_valid(fid):
                raise ValueError(f"Invalid farmer_id format in equipment: {fid}")
        
        # Check if all farmer_ids exist in farmers collection
        object_ids = [ObjectId(fid) for fid in farmer_ids]
        farmers_cursor = self.db.farmers.find(
            {"_id": {"$in": object_ids}},
            {"_id": 1}
        )
        
        existing_farmer_ids = {str(farmer["_id"]) async for farmer in farmers_cursor}
        
        # Find invalid farmer_ids
        invalid_farmer_ids = set(farmer_ids) - existing_farmer_ids
        
        if invalid_farmer_ids:
            raise ValueError(
                f"The following farmer_ids in equipment do not exist in farmers database: {', '.join(invalid_farmer_ids)}"
            )
    
    @staticmethod
    def _add_computed_fields(log_dict: dict) -> dict:
        """Calculate and add computed fields to log"""
        # Total hectares harvested
        log_dict["total_hectares_harvested"] = (
            log_dict.get("wheat_harvested_hectares", 0) +
            log_dict.get("sunflower_harvested_hectares", 0) +
            log_dict.get("beans_harvested_hectares", 0) +
            log_dict.get("tomatoes_harvested_hectares", 0)
        )
        
        # Total kg harvested
        log_dict["total_kg_harvested"] = (
            log_dict.get("wheat_harvested_kg", 0) +
            log_dict.get("sunflower_harvested_kg", 0) +
            log_dict.get("beans_harvested_kg", 0) +
            log_dict.get("tomatoes_harvested_kg", 0)
        )
        
        # Equipment totals
        equipment = log_dict.get("equipment", [])
        total_work_hours = sum(eq.get("work_hours", 0) for eq in equipment)
        total_fuel = sum(eq.get("fuel_consumed_liters", 0) for eq in equipment)
        
        log_dict["total_work_hours"] = round(total_work_hours, 2)
        log_dict["total_fuel_consumed"] = round(total_fuel, 2)
        log_dict["fuel_cost"] = round(total_fuel * log_dict.get("oil_price_per_liter", 0), 2)
        
        return log_dict


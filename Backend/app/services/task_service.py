"""Task service - business logic for task management"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, date

from ..models.task import Task, TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority


class TaskService:
    """Service for managing tasks and activities"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.tasks
    
    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """Create a new task"""
        task_dict = task_data.model_dump()
        
        # Convert date to datetime for MongoDB
        if "due_date" in task_dict and isinstance(task_dict["due_date"], date):
            if not isinstance(task_dict["due_date"], datetime):
                task_dict["due_date"] = datetime.combine(task_dict["due_date"], datetime.min.time())
        
        task_dict["status"] = TaskStatus.TODO
        task_dict["created_at"] = datetime.utcnow()
        task_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(task_dict)
        
        created_task = await self.collection.find_one({"_id": result.inserted_id})
        created_task["_id"] = str(created_task["_id"])
        created_task = self._add_is_overdue(created_task)
        
        return TaskResponse(**created_task)
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get task by ID"""
        if not ObjectId.is_valid(task_id):
            return None
        
        task = await self.collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return None
        
        task["_id"] = str(task["_id"])
        task = self._add_is_overdue(task)
        
        return TaskResponse(**task)
    
    async def list_farmer_tasks(
        self,
        farmer_id: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[TaskResponse]:
        """List tasks for a farmer"""
        query = {"farmer_id": farmer_id}
        
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        
        cursor = self.collection.find(query).sort("due_date", 1)
        tasks = []
        
        async for task in cursor:
            task["_id"] = str(task["_id"])
            task = self._add_is_overdue(task)
            tasks.append(TaskResponse(**task))
        
        return tasks
    
    async def update_task(
        self,
        task_id: str,
        task_update: TaskUpdate
    ) -> Optional[TaskResponse]:
        """Update task"""
        if not ObjectId.is_valid(task_id):
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_task(task_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # If status is completed, set completed_at
        if update_data.get("status") == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_task(task_id)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        if not ObjectId.is_valid(task_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
    async def get_today_tasks(self, farmer_id: str) -> List[TaskResponse]:
        """Get tasks due today"""
        today = datetime.combine(date.today(), datetime.min.time())
        
        query = {
            "farmer_id": farmer_id,
            "due_date": today,
            "status": {"$ne": TaskStatus.COMPLETED}
        }
        
        cursor = self.collection.find(query).sort("priority", -1)
        tasks = []
        
        async for task in cursor:
            task["_id"] = str(task["_id"])
            task = self._add_is_overdue(task)
            tasks.append(TaskResponse(**task))
        
        return tasks
    
    async def get_overdue_tasks(self, farmer_id: str) -> List[TaskResponse]:
        """Get overdue tasks"""
        today = datetime.combine(date.today(), datetime.min.time())
        
        query = {
            "farmer_id": farmer_id,
            "due_date": {"$lt": today},
            "status": {"$ne": TaskStatus.COMPLETED}
        }
        
        cursor = self.collection.find(query).sort("due_date", 1)
        tasks = []
        
        async for task in cursor:
            task["_id"] = str(task["_id"])
            task["is_overdue"] = True
            tasks.append(TaskResponse(**task))
        
        return tasks
    
    async def get_pending_tasks(self, farmer_id: str) -> List[TaskResponse]:
        """Get all pending (not completed) tasks"""
        query = {
            "farmer_id": farmer_id,
            "status": {"$ne": TaskStatus.COMPLETED}
        }
        
        cursor = self.collection.find(query).sort([("priority", -1), ("due_date", 1)])
        tasks = []
        
        async for task in cursor:
            task["_id"] = str(task["_id"])
            task = self._add_is_overdue(task)
            tasks.append(TaskResponse(**task))
        
        return tasks
    
    async def get_task_statistics(self, farmer_id: str) -> dict:
        """Get task statistics"""
        # Count by status
        pipeline = [
            {"$match": {"farmer_id": farmer_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_stats = {}
        async for doc in self.collection.aggregate(pipeline):
            status_stats[doc["_id"]] = doc["count"]
        
        # Count overdue
        today = datetime.combine(date.today(), datetime.min.time())
        overdue_count = await self.collection.count_documents({
            "farmer_id": farmer_id,
            "due_date": {"$lt": today},
            "status": {"$ne": TaskStatus.COMPLETED}
        })
        
        # Count by priority
        priority_pipeline = [
            {"$match": {
                "farmer_id": farmer_id,
                "status": {"$ne": TaskStatus.COMPLETED}
            }},
            {"$group": {
                "_id": "$priority",
                "count": {"$sum": 1}
            }}
        ]
        
        priority_stats = {}
        async for doc in self.collection.aggregate(priority_pipeline):
            priority_stats[doc["_id"]] = doc["count"]
        
        return {
            "by_status": status_stats,
            "by_priority": priority_stats,
            "overdue": overdue_count
        }
    
    @staticmethod
    def _add_is_overdue(task_dict: dict) -> dict:
        """Check and add is_overdue flag"""
        if task_dict.get("status") == TaskStatus.COMPLETED:
            task_dict["is_overdue"] = False
            return task_dict
        
        due_date = task_dict.get("due_date")
        if due_date:
            # Convert to date for comparison
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            elif isinstance(due_date, datetime):
                due_date = due_date.date()
            
            today = date.today()
            task_dict["is_overdue"] = due_date < today
        else:
            task_dict["is_overdue"] = False
        
        return task_dict

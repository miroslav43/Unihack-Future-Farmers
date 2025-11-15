"""Task/Activity data models"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task completion status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """Base task information"""
    farmer_id: str
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    crop_id: Optional[str] = None  # Link to specific crop
    parcel_id: Optional[str] = None


class TaskCreate(TaskBase):
    """Task creation model"""
    pass


class TaskUpdate(BaseModel):
    """Task update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class TaskResponse(TaskBase):
    """Task response model"""
    id: str = Field(..., alias="_id")
    status: TaskStatus
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False
    
    class Config:
        populate_by_name = True


class Task(TaskBase):
    """Internal task model"""
    id: Optional[str] = Field(None, alias="_id")
    status: TaskStatus = TaskStatus.TODO
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

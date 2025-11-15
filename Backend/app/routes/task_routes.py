"""Task API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
from ..services.task_service import TaskService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new task"""
    service = TaskService(db)
    return await service.create_task(task_data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task by ID"""
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task


@router.get("/farmer/{farmer_id}", response_model=List[TaskResponse])
async def list_farmer_tasks(
    farmer_id: str,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List tasks for a farmer"""
    service = TaskService(db)
    return await service.list_farmer_tasks(
        farmer_id=farmer_id,
        status=status,
        priority=priority
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update task"""
    service = TaskService(db)
    updated_task = await service.update_task(task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete task"""
    service = TaskService(db)
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )


@router.get("/farmer/{farmer_id}/today", response_model=List[TaskResponse])
async def get_today_tasks(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get tasks due today"""
    service = TaskService(db)
    return await service.get_today_tasks(farmer_id)


@router.get("/farmer/{farmer_id}/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get overdue tasks"""
    service = TaskService(db)
    return await service.get_overdue_tasks(farmer_id)


@router.get("/farmer/{farmer_id}/pending", response_model=List[TaskResponse])
async def get_pending_tasks(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all pending (not completed) tasks"""
    service = TaskService(db)
    return await service.get_pending_tasks(farmer_id)


@router.get("/farmer/{farmer_id}/statistics")
async def get_task_statistics(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task statistics for a farmer"""
    service = TaskService(db)
    return await service.get_task_statistics(farmer_id)

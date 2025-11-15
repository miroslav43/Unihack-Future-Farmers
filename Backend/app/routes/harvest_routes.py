"""Harvest log API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from ..models.harvest_log import HarvestLogCreate, HarvestLogUpdate, HarvestLogResponse
from ..services.harvest_service import HarvestService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/harvest-logs", tags=["harvest-logs"])


@router.post("/", response_model=HarvestLogResponse, status_code=status.HTTP_201_CREATED)
async def create_harvest_log(
    harvest_data: HarvestLogCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new harvest log entry"""
    service = HarvestService(db)
    return await service.create_harvest_log(harvest_data)


@router.get("/{log_id}", response_model=HarvestLogResponse)
async def get_harvest_log(
    log_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get harvest log by ID"""
    service = HarvestService(db)
    log = await service.get_harvest_log(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Harvest log with ID {log_id} not found"
        )
    return log


@router.get("/date/{target_date}", response_model=HarvestLogResponse)
async def get_harvest_log_by_date(
    target_date: date,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get harvest log for a specific date"""
    service = HarvestService(db)
    log = await service.get_harvest_log_by_date(target_date)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No harvest log found for date {target_date}"
        )
    return log


@router.get("/", response_model=List[HarvestLogResponse])
async def list_harvest_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List harvest logs with optional date range filtering"""
    service = HarvestService(db)
    return await service.list_harvest_logs(
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.put("/{log_id}", response_model=HarvestLogResponse)
async def update_harvest_log(
    log_id: str,
    harvest_update: HarvestLogUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update harvest log"""
    service = HarvestService(db)
    updated_log = await service.update_harvest_log(log_id, harvest_update)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Harvest log with ID {log_id} not found"
        )
    return updated_log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_harvest_log(
    log_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete harvest log"""
    service = HarvestService(db)
    deleted = await service.delete_harvest_log(log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Harvest log with ID {log_id} not found"
        )


@router.get("/statistics/overview")
async def get_harvest_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get harvest statistics for a date range"""
    service = HarvestService(db)
    return await service.get_harvest_statistics(
        start_date=start_date,
        end_date=end_date
    )


@router.get("/statistics/equipment")
async def get_equipment_usage_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get equipment usage statistics"""
    service = HarvestService(db)
    return await service.get_equipment_usage_stats(
        start_date=start_date,
        end_date=end_date
    )


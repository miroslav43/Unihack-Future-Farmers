"""Application/CHM API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.application import (
    ApplicationCreate, ApplicationResponse, ApplicationStatus
)
from ..services.application_service import ApplicationService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new application/CHM"""
    service = ApplicationService(db)
    try:
        return await service.create_application(application_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get application by ID"""
    service = ApplicationService(db)
    application = await service.get_application(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    return application


@router.get("/farmer/{farmer_id}", response_model=List[ApplicationResponse])
async def list_farmer_applications(
    farmer_id: str,
    status: Optional[ApplicationStatus] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all applications for a farmer"""
    service = ApplicationService(db)
    return await service.list_farmer_applications(
        farmer_id=farmer_id,
        status=status
    )


@router.post("/{application_id}/generate", response_model=ApplicationResponse)
async def generate_chm_document(
    application_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Generate CHM document for application"""
    service = ApplicationService(db)
    application = await service.generate_chm_document(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    return application


@router.post("/{application_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    application_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Submit application"""
    service = ApplicationService(db)
    try:
        application = await service.submit_application(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found"
            )
        return application
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str,
    status: ApplicationStatus,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update application status"""
    service = ApplicationService(db)
    application = await service.update_application_status(application_id, status)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    return application


@router.get("/statistics/overview")
async def get_application_statistics(
    farmer_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get application statistics"""
    service = ApplicationService(db)
    return await service.get_application_statistics(farmer_id=farmer_id)

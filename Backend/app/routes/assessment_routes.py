"""Assessment API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..models.assessment import AssessmentCreate, AssessmentResponse
from ..services.assessment_service import AssessmentService
from ..config.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new assessment for a farmer"""
    service = AssessmentService(db)
    try:
        return await service.create_assessment(assessment_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get assessment by ID"""
    service = AssessmentService(db)
    assessment = await service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with ID {assessment_id} not found"
        )
    return assessment


@router.get("/farmer/{farmer_id}/latest", response_model=AssessmentResponse)
async def get_farmer_latest_assessment(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get most recent assessment for a farmer"""
    service = AssessmentService(db)
    assessment = await service.get_farmer_latest_assessment(farmer_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No assessments found for farmer {farmer_id}"
        )
    return assessment


@router.get("/farmer/{farmer_id}", response_model=List[AssessmentResponse])
async def list_farmer_assessments(
    farmer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all assessments for a farmer"""
    service = AssessmentService(db)
    return await service.list_farmer_assessments(farmer_id)

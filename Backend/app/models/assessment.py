"""Assessment and scoring data models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BonitateScore(BaseModel):
    """Land quality (bonitate) scoring"""
    soil_quality: int = Field(..., ge=0, le=100)
    irrigation_access: int = Field(..., ge=0, le=100)
    location_score: int = Field(..., ge=0, le=100)
    infrastructure_score: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "soil_quality": 85,
                "irrigation_access": 90,
                "location_score": 75,
                "infrastructure_score": 80,
                "overall_score": 82
            }
        }


class FarmerScore(BaseModel):
    """Farmer experience and capability scoring"""
    experience_score: int = Field(..., ge=0, le=100)
    education_score: int = Field(..., ge=0, le=100)
    equipment_score: int = Field(..., ge=0, le=100)
    financial_score: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)


class RiskAssessment(BaseModel):
    """Risk assessment analysis"""
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    risk_factors: list[str] = []
    mitigation_suggestions: list[str] = []
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class AssessmentBase(BaseModel):
    """Base assessment information"""
    farmer_id: str
    bonitate_score: BonitateScore
    farmer_score: FarmerScore
    risk_assessment: RiskAssessment


class AssessmentCreate(BaseModel):
    """Assessment creation model"""
    farmer_id: str


class AssessmentResponse(AssessmentBase):
    """Assessment response model"""
    id: str = Field(..., alias="_id")
    overall_rating: str  # excellent, good, average, poor
    eligibility_score: int = Field(..., ge=0, le=100)
    recommendations: list[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439013",
                "farmer_id": "507f1f77bcf86cd799439011",
                "bonitate_score": {
                    "soil_quality": 85,
                    "irrigation_access": 90,
                    "location_score": 75,
                    "infrastructure_score": 80,
                    "overall_score": 82
                },
                "farmer_score": {
                    "experience_score": 90,
                    "education_score": 75,
                    "equipment_score": 85,
                    "financial_score": 70,
                    "overall_score": 80
                },
                "risk_assessment": {
                    "risk_level": "low",
                    "risk_factors": ["Limited financial reserves"],
                    "mitigation_suggestions": ["Consider agricultural insurance"],
                    "confidence_score": 0.87
                },
                "overall_rating": "excellent",
                "eligibility_score": 85,
                "recommendations": [
                    "Eligible for agricultural subsidies",
                    "Consider expanding irrigation system"
                ],
                "created_at": "2024-01-15T11:00:00",
                "updated_at": "2024-01-15T11:00:00"
            }
        }


class Assessment(AssessmentBase):
    """Internal assessment model with metadata"""
    id: Optional[str] = Field(None, alias="_id")
    overall_rating: Optional[str] = None
    eligibility_score: Optional[int] = None
    recommendations: list[str] = []
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

"""Application (CHM) data models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationType(str, Enum):
    """Types of applications/CHM forms"""
    SUBSIDIES = "subsidies"  # Subventii
    DEVELOPMENT_FUNDS = "development_funds"  # Fonduri dezvoltare
    YOUNG_FARMER = "young_farmer"  # Tineri fermieri
    ECOLOGICAL = "ecological"  # Agricultura ecologica
    EQUIPMENT = "equipment"  # Achizitie echipament
    OTHER = "other"


class ApplicationStatus(str, Enum):
    """Application processing status"""
    DRAFT = "draft"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApplicationBase(BaseModel):
    """Base application information"""
    farmer_id: str
    assessment_id: str
    application_type: ApplicationType
    requested_amount: float = Field(..., ge=0.0)
    description: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """Application creation model"""
    pass


class ApplicationResponse(ApplicationBase):
    """Application response model"""
    id: str = Field(..., alias="_id")
    status: ApplicationStatus
    application_number: str  # Unique application reference
    
    # Generated documents
    chm_file_path: Optional[str] = None
    supporting_docs: list[str] = []
    
    # Processing information
    eligibility_check: Dict[str, Any] = {}
    generated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439014",
                "farmer_id": "507f1f77bcf86cd799439011",
                "assessment_id": "507f1f77bcf86cd799439013",
                "application_type": "subsidies",
                "application_number": "CHM-2024-001234",
                "requested_amount": 50000.0,
                "description": "Cerere subventii pentru imbunatatirea sistemului de irigatii",
                "status": "generated",
                "chm_file_path": "/applications/CHM-2024-001234.pdf",
                "supporting_docs": [
                    "/documents/cni.pdf",
                    "/documents/ownership.pdf"
                ],
                "eligibility_check": {
                    "eligible": True,
                    "score": 85,
                    "criteria_met": ["land_ownership", "experience", "financial"]
                },
                "generated_at": "2024-01-15T12:00:00",
                "created_at": "2024-01-15T11:30:00",
                "updated_at": "2024-01-15T12:00:00"
            }
        }


class Application(ApplicationBase):
    """Internal application model with metadata"""
    id: Optional[str] = Field(None, alias="_id")
    status: ApplicationStatus = ApplicationStatus.DRAFT
    application_number: Optional[str] = None
    chm_file_path: Optional[str] = None
    supporting_docs: list[str] = []
    eligibility_check: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = None
    generated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

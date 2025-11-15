"""Document data models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents that can be uploaded"""
    CNI = "cni"  # Identity card
    CERTIFICATE = "certificate"  # Agricultural certificate
    PARCEL = "parcel"  # Parcel documentation
    CADASTRAL = "cadastral"  # Cadastral documents
    OWNERSHIP = "ownership"  # Ownership proof
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentBase(BaseModel):
    """Base document information"""
    farmer_id: str
    document_type: DocumentType
    filename: str
    file_path: str
    file_size: int = Field(..., ge=0)
    mime_type: str


class DocumentCreate(DocumentBase):
    """Document creation model"""
    pass


class DocumentResponse(DocumentBase):
    """Document response model"""
    id: str = Field(..., alias="_id")
    status: DocumentStatus
    extracted_data: Optional[Dict[str, Any]] = None
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "farmer_id": "507f1f77bcf86cd799439011",
                "document_type": "cni",
                "filename": "cni_ion_popescu.pdf",
                "file_path": "/uploads/507f1f77bcf86cd799439011/cni_ion_popescu.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "status": "processed",
                "extracted_data": {
                    "cnp": "1234567890123",
                    "first_name": "Ion",
                    "last_name": "Popescu",
                    "birth_date": "1978-05-20",
                    "address": "Bucuresti"
                },
                "ocr_confidence": 0.95,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:31:00",
                "processed_at": "2024-01-15T10:31:00"
            }
        }


class Document(DocumentBase):
    """Internal document model with metadata"""
    id: Optional[str] = Field(None, alias="_id")
    status: DocumentStatus = DocumentStatus.UPLOADED
    extracted_data: Optional[Dict[str, Any]] = None
    ocr_confidence: Optional[float] = None
    processing_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

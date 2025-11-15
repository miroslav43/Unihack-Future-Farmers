"""Farmer data models"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Farmer experience level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FarmerBase(BaseModel):
    """Base farmer information"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    cnp: str = Field(..., min_length=13, max_length=13)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    age: int = Field(..., ge=18, le=100)
    
    # Agricultural information
    experience_years: int = Field(..., ge=0, le=80)
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    
    # Land information
    total_parcels: int = Field(default=0, ge=0)
    total_land_area: float = Field(default=0.0, ge=0.0)  # in hectares
    
    # Resources
    has_equipment: bool = Field(default=False)
    has_irrigation: bool = Field(default=False)
    has_storage: bool = Field(default=False)
    
    # Address
    county: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=500)
    
    @field_validator('cnp')
    @classmethod
    def validate_cnp(cls, v: str) -> str:
        """Validate Romanian CNP format"""
        if not v.isdigit():
            raise ValueError('CNP must contain only digits')
        if len(v) != 13:
            raise ValueError('CNP must be exactly 13 digits')
        return v


class FarmerCreate(FarmerBase):
    """Farmer creation model"""
    pass


class FarmerUpdate(BaseModel):
    """Farmer update model - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    experience_years: Optional[int] = Field(None, ge=0, le=80)
    experience_level: Optional[ExperienceLevel] = None
    total_parcels: Optional[int] = Field(None, ge=0)
    total_land_area: Optional[float] = Field(None, ge=0.0)
    has_equipment: Optional[bool] = None
    has_irrigation: Optional[bool] = None
    has_storage: Optional[bool] = None
    county: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, min_length=5, max_length=500)


class FarmerResponse(FarmerBase):
    """Farmer response model"""
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "first_name": "Ion",
                "last_name": "Popescu",
                "cnp": "1234567890123",
                "email": "ion.popescu@example.com",
                "phone": "0712345678",
                "age": 45,
                "experience_years": 20,
                "experience_level": "advanced",
                "total_parcels": 3,
                "total_land_area": 15.5,
                "has_equipment": True,
                "has_irrigation": True,
                "has_storage": True,
                "county": "Ilfov",
                "city": "Bucuresti",
                "address": "Str. Agricultorilor nr. 10",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class Farmer(FarmerBase):
    """Internal farmer model with metadata"""
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

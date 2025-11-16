from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    is_active: bool


class FarmerCreate(BaseModel):
    farm_name: str
    contact_person: str
    phone: str
    email: EmailStr
    address: str
    city: str
    county: str
    postal_code: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    certifications: Optional[List[str]] = None


class FarmerUpdate(BaseModel):
    farm_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    postal_code: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    certifications: Optional[List[str]] = None


class FarmerResponse(BaseModel):
    id: str
    user_id: str
    farm_name: str
    contact_person: str
    phone: str
    email: EmailStr
    address: str
    city: str
    county: str
    postal_code: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    certifications: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class BuyerCreate(BaseModel):
    company_name: str
    contact_person: str
    phone: str
    email: EmailStr
    business_type: Optional[str] = "other"
    tax_id: Optional[str] = None
    address: str
    city: str
    county: str
    postal_code: Optional[str] = None


class BuyerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    postal_code: Optional[str] = None


class BuyerResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    contact_person: str
    phone: str
    email: EmailStr
    business_type: Optional[str]
    tax_id: Optional[str]
    address: str
    city: str
    county: str
    postal_code: Optional[str]
    created_at: datetime
    updated_at: datetime

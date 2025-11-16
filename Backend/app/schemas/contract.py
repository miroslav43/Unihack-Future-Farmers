from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ContractItemSchema(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    unit: str
    price_per_unit: float
    total_price: float


class SignatureSchema(BaseModel):
    signer_id: str
    signer_name: str
    signer_role: str
    signature: str
    signed_at: datetime
    public_key: str


class ContractCreate(BaseModel):
    buyer_id: str
    buyer_name: str
    farmer_id: str
    farmer_name: str
    items: List[ContractItemSchema]
    total_amount: float
    delivery_date: Optional[str] = None
    delivery_address: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None


class ContractResponse(BaseModel):
    _id: str
    buyer_id: str
    buyer_name: str
    farmer_id: str
    farmer_name: str
    items: List[ContractItemSchema]
    total_amount: float
    delivery_date: Optional[str] = None
    delivery_address: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    status: str
    contract_hash: str
    blockchain_tx_id: Optional[str] = None
    farmer_signature: Optional[SignatureSchema] = None
    buyer_signature: Optional[SignatureSchema] = None
    created_at: datetime
    updated_at: datetime
    signed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class SignContractRequest(BaseModel):
    signature: str
    public_key: str


class KeyPairResponse(BaseModel):
    private_key: str
    public_key: str
    note: str

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base
from enum import Enum


class ContractStatus(str, Enum):
    PENDING = "pending"
    SIGNED_FARMER = "signed_farmer"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    buyer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    buyer_name = Column(String, nullable=False)
    farmer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    farmer_name = Column(String, nullable=False)
    items = Column(JSON, nullable=False)  # Array of contract items
    total_amount = Column(Float, nullable=False)
    delivery_date = Column(String, nullable=True)
    delivery_address = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default=ContractStatus.PENDING.value, nullable=False)
    contract_hash = Column(String, nullable=False)
    blockchain_tx_id = Column(String, nullable=True)
    farmer_signature = Column(JSON, nullable=True)
    buyer_signature = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    signed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    buyer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    buyer_name = Column(String, nullable=False)
    farmer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    farmer_name = Column(String, nullable=False)
    items = Column(JSON, nullable=False)  # [{inventory_id, product_name, quantity, unit, price_per_unit (snapshot)}]
    total_amount = Column(Float, nullable=False)
    status = Column(String, default=OrderStatus.PENDING.value, nullable=False)
    buyer_message = Column(Text, nullable=True)
    farmer_response = Column(Text, nullable=True)
    expected_delivery_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


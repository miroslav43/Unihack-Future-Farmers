from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    is_available_for_sale = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    min_order_quantity = Column(Float, nullable=True)
    max_order_quantity = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

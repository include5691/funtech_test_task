import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, JSON, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.db.session import Base
from src.schemas.order import OrderStatus

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items = Column(JSON, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
import uuid
import enum
from datetime import datetime
from pydantic import BaseModel, Field

class OrderStatus(enum.StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"

class OrderBase(BaseModel):
    "Base model also uses for create order"
    items: list
    total_price: float

class OrderUpdate(BaseModel):
    "Update order status"
    status: OrderStatus

class OrderRead(OrderBase):
    "Read order"
    id: uuid.UUID
    user_id: int
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True
import uuid
import enum
from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class OrderStatus(str, enum.Enum):
    "Enumeration for possible order statuses."

    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class OrderBase(BaseModel):
    "Base schema for order data, used for creation."

    items: List[Dict[str, Any]] = Field(
        ...,
        description="List of items included in the order. Each item should be a dictionary.",
        example=[
            {"name": "xbox", "quantity": 2, "price": 15.50},
            {"name": "ps5", "quantity": 1, "price": 42.0},
        ],
    )
    total_price: float = Field(
        ...,
        gt=0,
        description="The total calculated price for all items in the order.",
        example=73.00,
    )


class OrderUpdate(BaseModel):
    "Schema used specifically for updating the status of an order."

    status: OrderStatus = Field(
        ...,
        description="The new status to assign to the order.",
        example=OrderStatus.SHIPPED,
    )


class OrderRead(OrderBase):
    "Schema representing a complete order record as read from the system."

    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) for the order.",
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479",
    )
    user_id: int = Field(
        ..., description="Identifier of the user who placed the order.", example=101
    )
    status: OrderStatus = Field(
        ..., description="The current status of the order.", example=OrderStatus.PENDING
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp indicating when the order was created (in UTC).",
        example="2023-10-27T12:30:00Z",
    )

    class Config:
        from_attributes = True  # ORM mode for Pydantic v2

    def dump_for_kafka(self) -> dict:
        "Serializes order data for Kafka message payload."
        return {
            "id": str(self.id),  # Kafka might prefer string UUID
            "user_id": self.user_id,
            "items": self.items,
            "total_price": self.total_price,
            "status": self.status.value,  # Send enum value
            "created_at": self.created_at.isoformat(),  # Use ISO format string
        }

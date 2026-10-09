from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(StrEnum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    product: str = Field(min_length=1, max_length=255)
    quantity: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: str
    product: str
    quantity: int
    amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

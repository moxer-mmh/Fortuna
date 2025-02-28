# fortuna/backend/app/schemas/subscription.py
from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    name: str = Field(..., example="Netflix")
    amount: float = Field(..., example=15.99)
    frequency: str = Field(
        ..., example="monthly"
    )  # Allowed values: weekly, monthly, yearly
    next_payment: datetime = Field(..., example="2023-02-01T00:00:00")
    category_id: str = Field(..., example="expense_category_id")
    account_id: str = Field(..., example="account_id")


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    name: str = Field(None, example="Netflix Premium")
    amount: float = Field(None, example=17.99)
    frequency: str = Field(None, example="monthly")
    next_payment: datetime = Field(None, example="2023-03-01T00:00:00")
    category_id: str = Field(None, example="expense_category_id")
    account_id: str = Field(None, example="account_id")
    active: bool = Field(None, example=True)


class Subscription(SubscriptionBase):
    id: str
    active: bool

    class Config:
        from_attributes = True

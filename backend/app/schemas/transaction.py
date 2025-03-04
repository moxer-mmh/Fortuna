# fortuna/backend/app/schemas/transaction.py
from datetime import datetime
from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    date: datetime = Field(..., example="2023-01-15T00:00:00")
    amount: float = Field(..., example=50.0)
    description: str = Field(..., example="Grocery shopping")
    account_id: str = Field(..., example="some_account_id")
    category_id: str = Field(..., example="some_category_id")
    type: str = Field(
        ..., example="expense"
    )  # could be "income" or "subscription" as well


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: datetime = Field(None, example="2023-01-15T00:00:00")
    amount: float = Field(None, example=50.0)
    description: str = Field(None, example="Grocery shopping")
    account_id: str = Field(None, example="some_account_id")
    category_id: str = Field(None, example="some_category_id")
    type: str = Field(None, example="expense")


class Transaction(TransactionBase):
    id: str

    class Config:
        from_attributes = True

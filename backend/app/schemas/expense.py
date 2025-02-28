# fortuna/backend/app/schemas/expense.py
from datetime import datetime
from pydantic import BaseModel, Field


class ExpenseBase(BaseModel):
    date: datetime = Field(..., example="2023-01-15T00:00:00")
    amount: float = Field(..., example=50.0)
    description: str = Field(..., example="Grocery shopping")
    account_id: str = Field(..., example="some_account_id")
    category_id: str = Field(..., example="some_category_id")


class ExpenseCreate(ExpenseBase):
    # No extra fields needed; the service sets type to "expense"
    pass


class ExpenseUpdate(BaseModel):
    date: datetime = Field(None, example="2023-01-15T00:00:00")
    amount: float = Field(None, example=50.0)
    description: str = Field(None, example="Grocery shopping")
    account_id: str = Field(None, example="some_account_id")
    category_id: str = Field(None, example="some_category_id")


class Expense(ExpenseBase):
    id: str

    class Config:
        from_attributes = True

# fortuna/backend/app/schemas/income.py
from datetime import datetime
from pydantic import BaseModel, Field


class IncomeBase(BaseModel):
    date: datetime = Field(..., example="2023-01-15T00:00:00")
    amount: float = Field(..., example=1000.0)
    description: str = Field(..., example="Salary payment")
    account_id: str = Field(..., example="account_id_example")
    category_id: str = Field(..., example="income_category_id_example")


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    date: datetime = Field(None, example="2023-01-15T00:00:00")
    amount: float = Field(None, example=1000.0)
    description: str = Field(None, example="Salary payment")
    account_id: str = Field(None, example="account_id_example")
    category_id: str = Field(None, example="income_category_id_example")


class Income(IncomeBase):
    id: str

    class Config:
        from_attributes = True

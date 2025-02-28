# fortuna/backend/app/schemas/category.py
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., example="Groceries")
    budget: float = Field(..., example=300.0)
    type: str = Field(..., example="expense")  # or "income"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str = Field(None, example="Food")
    budget: float = Field(None, example=350.0)
    type: str = Field(None, example="expense")


class Category(CategoryBase):
    id: str

    class Config:
        from_attributes = True

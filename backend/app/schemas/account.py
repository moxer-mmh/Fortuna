# fortuna/backend/app/schemas/account.py
from pydantic import BaseModel, Field

class AccountBase(BaseModel):
    name: str = Field(..., example="Main Account")
    balance: float = Field(..., example=1000.0)

class AccountCreate(AccountBase):
    id: str = Field(None, example="123e4567-e89b-12d3-a456-426614174000")

class AccountUpdate(BaseModel):
    name: str = Field(None, example="Updated Account Name")
    balance: float = Field(None, example=1500.0)

class Account(AccountBase):
    id: str

    class Config:
        from_attributes = True

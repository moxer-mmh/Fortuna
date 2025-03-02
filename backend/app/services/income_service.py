# fortuna/backend/app/services/income_service.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..schemas import IncomeCreate, IncomeUpdate, Income
from ..db import (
    Transaction as TransactionModel,
    Category as CategoryModel,
    Account as AccountModel,
)
from sqlalchemy import func


class IncomeService:
    def __init__(self, db: Session):
        self.db = db

    def create_income(self, income_data: IncomeCreate) -> Income:
        # Validate that the category exists and is of type "income"
        category = (
            self.db.query(CategoryModel)
            .filter(
                CategoryModel.id == income_data.category_id,
                CategoryModel.type == "income",
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Income category not found")

        # Validate that the account exists
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == income_data.account_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Create the income transaction (set type to "income")
        income_dict = income_data.model_dump(exclude_unset=True)
        income_dict["type"] = "income"
        transaction = TransactionModel(**income_dict)
        self.db.add(transaction)

        # Update account balance (increase by income amount)
        account.balance += income_data.amount

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error creating income: " + str(e)
            )
        self.db.refresh(transaction)
        return transaction

    def get_income(self, income_id: str) -> Optional[Income]:
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.id == income_id, TransactionModel.type == "income")
            .first()
        )

    def get_all_incomes(self) -> List[Income]:
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.type == "income")
            .all()
        )

    def update_income(self, income_id: str, income_data: IncomeUpdate) -> Income:
        income = self.get_income(income_id)
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        old_amount = income.amount
        update_data = income_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(income, key, value)
        if "amount" in update_data:
            account = (
                self.db.query(AccountModel)
                .filter(AccountModel.id == income.account_id)
                .first()
            )
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")
            # Reverse the old income effect then apply the new income amount
            account.balance -= old_amount
            account.balance += income.amount
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error updating income: " + str(e)
            )
        self.db.refresh(income)
        return income

    def delete_income(self, income_id: str) -> None:
        income = self.get_income(income_id)
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == income.account_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        # Reverse the income effect on the account balance
        account.balance -= income.amount
        self.db.delete(income)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error deleting income: " + str(e)
            )

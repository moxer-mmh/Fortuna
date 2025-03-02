# fortuna/backend/app/services/expense_service.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from ..schemas import ExpenseCreate, ExpenseUpdate, Expense
from ..db import (
    Transaction as TransactionModel,
    Category as CategoryModel,
    Account as AccountModel,
)


class ExpenseService:
    def __init__(self, db: Session):
        self.db = db

    def create_expense(self, expense_data: ExpenseCreate) -> Expense:
        # Validate the category exists and is of type "expense"
        category = (
            self.db.query(CategoryModel)
            .filter(
                CategoryModel.id == expense_data.category_id,
                CategoryModel.type == "expense",
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Expense category not found")

        # Check the current month's total expense for the category to enforce budget limits
        expense_year = expense_data.date.year
        expense_month = expense_data.date.month
        # Using SQLite date functions (adjust if using another database)
        total_expense = (
            self.db.query(func.sum(TransactionModel.amount))
            .filter(
                TransactionModel.category_id == category.id,
                TransactionModel.type == "expense",
                func.strftime("%Y", TransactionModel.date) == str(expense_year),
                func.strftime("%m", TransactionModel.date) == f"{expense_month:02d}",
            )
            .scalar()
            or 0.0
        )

        if total_expense + expense_data.amount > category.budget:
            raise HTTPException(
                status_code=400, detail="Category budget exceeded for this month"
            )

        # Validate the account exists
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == expense_data.account_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Create the expense transaction with type "expense"
        expense_dict = expense_data.model_dump(exclude_unset=True)
        expense_dict["type"] = "expense"
        transaction = TransactionModel(**expense_dict)
        self.db.add(transaction)

        # Update account balance (deduct the expense amount)
        account.balance -= expense_data.amount
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error creating expense: " + str(e)
            )
        self.db.refresh(transaction)
        return transaction

    def get_expense(self, expense_id: str) -> Optional[Expense]:
        return (
            self.db.query(TransactionModel)
            .filter(
                TransactionModel.id == expense_id, TransactionModel.type == "expense"
            )
            .first()
        )

    def get_all_expenses(self) -> List[Expense]:
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.type == "expense")
            .all()
        )

    def update_expense(self, expense_id: str, expense_data: ExpenseUpdate) -> Expense:
        expense = self.get_expense(expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        old_amount = expense.amount
        update_data = expense_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(expense, key, value)
        if "amount" in update_data:
            account = (
                self.db.query(AccountModel)
                .filter(AccountModel.id == expense.account_id)
                .first()
            )
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")
            # Revert the old expense amount then apply the new expense amount
            account.balance += old_amount
            account.balance -= expense.amount
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error updating expense: " + str(e)
            )
        self.db.refresh(expense)
        return expense

    def delete_expense(self, expense_id: str) -> None:
        expense = self.get_expense(expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        account = (
            self.db.query(AccountModel)
            .filter(AccountModel.id == expense.account_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        # Revert the expense amount back to the account balance
        account.balance += expense.amount
        self.db.delete(expense)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Error deleting expense: " + str(e)
            )
        return True

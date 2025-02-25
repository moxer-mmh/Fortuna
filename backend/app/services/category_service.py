# fortuna/backend/app/services/category_service.py
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import extract, func
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas import CategoryCreate, CategoryUpdate, Category
from db import Category as CategoryModel, Transaction as TransactionModel


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category: CategoryCreate) -> Category:
        db_category = CategoryModel(**category.model_dump())
        self.db.add(db_category)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Error creating category")
        self.db.refresh(db_category)
        return db_category

    def get_category_by_id(self, category_id: str) -> Optional[Category]:
        return (
            self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        )

    def get_category_by_name(self, name: str, type: str) -> Optional[Category]:
        return (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == name, CategoryModel.type == type)
            .first()
        )

    def get_all_categories(self) -> List[Category]:
        return self.db.query(CategoryModel).all()

    def update_category(
        self, category_id: str, category: CategoryUpdate
    ) -> Optional[Category]:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: str) -> None:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        self.db.delete(db_category)
        self.db.commit()

    def get_transactions_for_month(
        self, category_id: str, year: int, month: int
    ) -> List[TransactionModel]:
        transactions = (
            self.db.query(TransactionModel)
            .filter(
                TransactionModel.category_id == category_id,
                extract("year", TransactionModel.date) == year,
                extract("month", TransactionModel.date) == month,
            )
            .all()
        )
        return transactions

    def get_monthly_total(self, category_id: str, year: int, month: int) -> float:
        total = (
            self.db.query(func.sum(TransactionModel.amount))
            .filter(
                TransactionModel.category_id == category_id,
                extract("year", TransactionModel.date) == year,
                extract("month", TransactionModel.date) == month,
            )
            .scalar()
        )
        return float(total or 0.0)

    def get_monthly_status(
        self, category_id: str, year: int, month: int
    ) -> Tuple[float, float, float]:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        monthly_total = self.get_monthly_total(category_id, year, month)
        if db_category.type == "expense":
            remaining = db_category.budget - monthly_total
            percentage = (
                (monthly_total / db_category.budget * 100)
                if db_category.budget > 0
                else 0
            )
            return monthly_total, remaining, percentage
        else:
            remaining_to_target = db_category.budget - monthly_total
            percentage = (
                (monthly_total / db_category.budget * 100)
                if db_category.budget > 0
                else 0
            )
            return monthly_total, remaining_to_target, percentage

    def can_add_transaction(
        self, category_id: str, amount: float, date: datetime
    ) -> bool:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        if db_category.type == "income":
            return True
        year, month = date.year, date.month
        current_total = self.get_monthly_total(category_id, year, month)
        return (current_total + amount) <= db_category.budget

    def get_all_transactions_in_category(
        self, category_id: str
    ) -> List[TransactionModel]:
        transactions = (
            self.db.query(TransactionModel)
            .filter(TransactionModel.category_id == category_id)
            .all()
        )
        return transactions

    def get_total_transactions_in_category(self, category_id: str) -> float:
        total = (
            self.db.query(func.sum(TransactionModel.amount))
            .filter(TransactionModel.category_id == category_id)
            .scalar()
        )
        return float(total or 0.0)

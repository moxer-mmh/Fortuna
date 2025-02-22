#fortuna/backend/app/services/category_service.py
from typing import List, Optional, Tuple
from datetime import datetime
import uuid
from sqlalchemy import extract, func
from ..db import Category as CategoryModel
from ..db import Transaction as TransactionModel
from ..db import DatabaseConnection
from .transaction_service import Transaction


class Category:
    def __init__(self, name: str, budget: float, type: str, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.budget = budget
        self.type = type
        self._db = DatabaseConnection()

    @classmethod
    def from_orm(cls, db_category: CategoryModel) -> "Category":
        """Convert ORM model instance to Category domain object"""
        return cls(
            name=db_category.name,
            budget=db_category.budget,
            type=db_category.type,
            id=db_category.id,
        )

    def to_orm(self) -> CategoryModel:
        """Convert Category domain object to ORM model instance"""
        return CategoryModel(
            id=self.id, name=self.name, budget=self.budget, type=self.type
        )

    def save(self) -> None:
        with self._db.get_session() as session:
            db_category = session.query(CategoryModel).filter_by(id=self.id).first()
            if db_category:
                db_category.name = self.name
                db_category.budget = self.budget
                db_category.type = self.type
            else:
                db_category = self.to_orm()
                session.add(db_category)
            session.commit()

    def get_transactions_for_month(self, year: int, month: int) -> List[Transaction]:
        with self._db.get_session() as session:
            db_transactions = (
                session.query(TransactionModel)
                .filter(
                    TransactionModel.category_id == self.id,
                    extract("year", TransactionModel.date) == year,
                    extract("month", TransactionModel.date) == month,
                )
                .all()
            )
            return [Transaction.from_orm(t) for t in db_transactions]

    def get_monthly_total(self, year: int, month: int) -> float:
        with self._db.get_session() as session:
            result = (
                session.query(func.sum(TransactionModel.amount))
                .filter(
                    TransactionModel.category_id == self.id,
                    extract("year", TransactionModel.date) == year,
                    extract("month", TransactionModel.date) == month,
                )
                .scalar()
            )
            return float(result or 0.0)

    def get_monthly_status(self, year: int, month: int) -> Tuple[float, float, float]:
        monthly_total = self.get_monthly_total(year, month)

        if self.type == "expense":
            remaining = self.budget - monthly_total
            percentage = (monthly_total / self.budget * 100) if self.budget > 0 else 0
            return monthly_total, remaining, percentage
        else:  # income
            remaining_to_target = self.budget - monthly_total
            percentage = (monthly_total / self.budget * 100) if self.budget > 0 else 0
            return monthly_total, remaining_to_target, percentage

    def can_add_transaction(self, amount: float, date: datetime) -> bool:
        if self.type == "income":
            return True

        year, month = date.year, date.month
        current_total = self.get_monthly_total(year, month)
        return (current_total + amount) <= self.budget

    def get_transactions_from_category(self) -> List[Transaction]:
        with self._db.get_session() as session:
            db_transactions = (
                session.query(TransactionModel)
                .filter(TransactionModel.category_id == self.id)
                .all()
            )
            return [Transaction.from_orm(t) for t in db_transactions]

    def get_total_transactions_in_category(self) -> float:
        with self._db.get_session() as session:
            result = (
                session.query(func.sum(TransactionModel.amount))
                .filter(TransactionModel.category_id == self.id)
                .scalar()
            )
            return float(result or 0.0)

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Category"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_category = session.query(CategoryModel).filter_by(id=id).first()
            return cls.from_orm(db_category) if db_category else None

    @classmethod
    def get_by_name(cls, name: str, type: str) -> Optional["Category"]:
        db = DatabaseConnection()
        with db.get_session() as session:
            db_category = (
                session.query(CategoryModel).filter_by(name=name, type=type).first()
            )
            return cls.from_orm(db_category) if db_category else None

    def __str__(self) -> str:
        budget_type = "Budget" if self.type == "expense" else "Target"
        return f"{self.name} (Monthly {budget_type}: {self.budget:.2f} DA)"

    def __repr__(self) -> str:
        return f"Category(name='{self.name}', monthly_{self.type}_amount={self.budget}, type='{self.type}')"

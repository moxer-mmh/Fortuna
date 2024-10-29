import uuid
from typing import List, Optional, Tuple
from datetime import datetime
from ..database import DatabaseConnection
from .transaction import Transaction


class Category:
    def __init__(self, name: str, budget: float, type: str, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.budget = budget
        self.type = type
        self.db = DatabaseConnection()

    def save(self):
        self.db.execute_query(
            "INSERT OR REPLACE INTO categories (id, name, budget, type) VALUES (?, ?, ?, ?)",
            (self.id, self.name, self.budget, self.type),
        )

    def get_transactions_for_month(self, year: int, month: int) -> List[Transaction]:
        results = self.db.fetch_all(
            """
            SELECT id, date, amount, description, account_id
            FROM transactions
            WHERE category_id = ? 
            AND strftime('%Y', date) = ? 
            AND strftime('%m', date) = ?
            """,
            (self.id, str(year), str(month).zfill(2)),
        )
        return [
            Transaction(
                date=row[1],
                amount=row[2],
                description=row[3],
                account_id=row[4],
                id=row[0],
            )
            for row in results
        ]

    def get_monthly_total(self, year: int, month: int) -> float:
        result = self.db.fetch_one(
            """
            SELECT SUM(amount)
            FROM transactions
            WHERE category_id = ?
            AND strftime('%Y', date) = ?
            AND strftime('%m', date) = ?
            """,
            (self.id, str(year), str(month).zfill(2)),
        )
        return result[0] or 0.0

    def get_monthly_status(self, year: int, month: int) -> Tuple[float, float, float]:
        monthly_total = self.get_monthly_total(year, month)

        if self.type == "expense":
            remaining = self.budget - monthly_total
            percentage = (monthly_total / self.budget * 100) if self.budget > 0 else 0
            return monthly_total, remaining, percentage
        else:  # income
            remaining_to_target = self.budget - monthly_total  # budget acts as target
            percentage = (monthly_total / self.budget * 100) if self.budget > 0 else 0
            return monthly_total, remaining_to_target, percentage

    def can_add_transaction(self, amount: float, date: datetime) -> bool:
        if self.type == "income":
            return True

        year, month = date.year, date.month
        current_total = self.get_monthly_total(year, month)
        return (current_total + amount) <= self.budget

    def get_transactions_from_category(self) -> List[Transaction]:
        results = self.db.fetch_all(
            """
            SELECT id, date, amount, description, account_id
            FROM transactions
            WHERE category_id = ?
            """,
            (self.id,),
        )
        return [
            Transaction(
                date=row[1],
                amount=row[2],
                description=row[3],
                account_id=row[4],
                id=row[0],
            )
            for row in results
        ]

    def get_total_transactions_in_category(self) -> float:
        result = self.db.fetch_one(
            "SELECT SUM(amount) FROM transactions WHERE category_id = ?", (self.id,)
        )
        return result[0] or 0.0

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Category"]:
        db = DatabaseConnection()
        result = db.fetch_one(
            "SELECT id, name, budget, type FROM categories WHERE id = ?", (id,)
        )
        if result:
            return cls(name=result[1], budget=result[2], type=result[3], id=result[0])
        return None

    @classmethod
    def get_by_name(cls, name: str, type: str) -> Optional["Category"]:
        db = DatabaseConnection()
        result = db.fetch_one(
            "SELECT id, name, budget, type FROM categories WHERE name = ? AND type = ?",
            (name, type),
        )
        if result:
            return cls(name=result[1], budget=result[2], type=result[3], id=result[0])
        return None

    def __str__(self) -> str:
        budget_type = "Budget" if self.type == "expense" else "Target"
        return f"{self.name} (Monthly {budget_type}: {self.budget:.2f} DA)"

    def __repr__(self) -> str:
        return f"Category(name='{self.name}', monthly_{self.type}_amount={self.budget}, type='{self.type}')"

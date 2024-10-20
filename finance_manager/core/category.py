import uuid
from typing import List, Optional
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
        return f"{self.name} (Budget: {self.budget:.2f} DA)"

    def __repr__(self) -> str:
        return f"Category(name='{self.name}', budget={self.budget}, type='{self.type}')"

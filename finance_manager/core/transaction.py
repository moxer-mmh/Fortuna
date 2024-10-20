import uuid
from datetime import datetime
from ..database import DatabaseConnection


class Transaction:
    def __init__(
        self,
        date: datetime,
        amount: float,
        description: str,
        account_id: str,
        category_id: str = None,
        type: str = None,
        id: str = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.date = (
            date if isinstance(date, datetime) else datetime.strptime(date, "%Y-%m-%d")
        )
        self.amount = amount
        self.description = description
        self.account_id = account_id
        self.category_id = category_id
        self.type = type
        self.db = DatabaseConnection()

    def save(self):
        self.db.execute_query(
            """
            INSERT OR REPLACE INTO transactions 
            (id, date, amount, description, account_id, category_id, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.id,
                self.date.strftime("%Y-%m-%d"),
                self.amount,
                self.description,
                self.account_id,
                self.category_id,
                self.type,
            ),
        )

    @classmethod
    def get_by_id(cls, id: str) -> "Transaction":
        db = DatabaseConnection()
        result = db.fetch_one(
            """
            SELECT id, date, amount, description, account_id, category_id, type
            FROM transactions
            WHERE id = ?
            """,
            (id,),
        )
        if result:
            return cls(
                date=result[1],
                amount=result[2],
                description=result[3],
                account_id=result[4],
                category_id=result[5],
                type=result[6],
                id=result[0],
            )
        return None

    def delete(self):
        self.db.execute_query("DELETE FROM transactions WHERE id = ?", (self.id,))

    def __str__(self) -> str:
        return f"(id='{self.id}' - date='{self.date.strftime('%Y-%m-%d')}' - amount={self.amount:.2f})"

    def __repr__(self) -> str:
        return self.__str__()

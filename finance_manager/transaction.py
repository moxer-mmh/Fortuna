
import uuid

from datetime import datetime



class Transaction:
    def __init__(self, date: datetime, amount: float, description: str):
        self.id: str = str(uuid.uuid4())
        self.date: datetime = date
        self.amount: float = amount
        self.description: str = description

    def __str__(self) -> str:
        return f"{self.date.strftime('%Y-%m-%d')} - ${self.amount:.2f} - {self.description}"

    def __repr__(self) -> str:
        return f"Transaction(date='{self.date.strftime('%Y-%m-%d')}', amount={self.amount}, description='{self.description}')"

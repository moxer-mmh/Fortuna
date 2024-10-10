from datetime import datetime
from typing import List, Optional
from .transaction import Transaction

class Category:
    def __init__(self, name: str, budget: float):
        self.name: str = name
        self.budget: float = budget
        self.transactions: List[Transaction] = []

    def __str__(self) -> str:
        return f"{self.name} (Budget: ${self.budget:.2f})"

    def __repr__(self) -> str:
        return f"Category(name='{self.name}', budget={self.budget})"

    def add_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise ValueError("Transaction must be an instance of Transaction class")
        self.transactions.append(transaction)

    def get_transactions(self) -> List[Transaction]:
        return self.transactions

    def get_total_transactions(self) -> float:
        return sum(t.amount for t in self.transactions)

    def delete_transaction(self, transaction: Transaction) -> None:
        if transaction in self.transactions:
            self.transactions.remove(transaction)
        else:
            raise ValueError("Transaction not found in category")



from typing import List
from .transaction import Transaction

class Category:
    def __init__(self, name: str, budget: float):
        self.name: str = name
        self.budget: float = budget
        self.transactions: List[Transaction] = []

    def __str__(self) -> str:
        return f"{self.name} (Budget: {self.budget:.2f} DA)"

    def __repr__(self) -> str:
        return f"Category(name='{self.name}', budget={self.budget})"

    def add_transaction_to_category(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise ValueError("Transaction must be an instance of Transaction class")
        self.transactions.append(transaction)

    def get_transactions_from_category(self) -> List[Transaction]:
        return self.transactions

    def delete_transaction_from_category(self, transaction: Transaction) -> None:
        if transaction in self.transactions:
            self.transactions.remove(transaction)
        else:
            raise ValueError("Transaction not found in category")

    def get_total_transactions_in_category(self) -> float:
        return sum(t.amount for t in self.transactions)


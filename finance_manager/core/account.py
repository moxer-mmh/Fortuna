import uuid
from typing import List, Optional
from ..database import DatabaseConnection


class Account:
    def __init__(self, name: str, balance: float = 0, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.balance = balance
        self.db = DatabaseConnection()

    def save(self):
        self.db.execute_query(
            "INSERT OR REPLACE INTO accounts (id, name, balance) VALUES (?, ?, ?)",
            (self.id, self.name, self.balance),
        )

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()

    def transfer(self, amount: float, target: "Account") -> None:
        self.withdraw(amount)
        target.deposit(amount)

    @classmethod
    def get_by_id(cls, id: str) -> Optional["Account"]:
        db = DatabaseConnection()
        result = db.fetch_one(
            "SELECT id, name, balance FROM accounts WHERE id = ?", (id,)
        )
        if result:
            return cls(name=result[1], balance=result[2], id=result[0])
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Account"]:
        db = DatabaseConnection()
        result = db.fetch_one(
            "SELECT id, name, balance FROM accounts WHERE name = ?", (name,)
        )
        if result:
            return cls(name=result[1], balance=result[2], id=result[0])
        return None

    def __repr__(self) -> str:
        return f"Account(name='{self.name}', balance={self.balance:.2f})"

    def __str__(self) -> str:
        return f"{self.name} - {self.balance:.2f}"


class AccountManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_account(self, name: str) -> Optional[Account]:
        return Account.get_by_name(name)

    def get_all_accounts(self) -> List[Account]:
        results = self.db.fetch_all("SELECT id, name, balance FROM accounts")
        return [Account(name=row[1], balance=row[2], id=row[0]) for row in results]

    def add_account(self, name: str, initial_balance: float = 0) -> None:
        if self.get_account(name):
            raise ValueError(f"Account '{name}' already exists")
        account = Account(name, initial_balance)
        account.save()

    def display_accounts(self) -> None:
        accounts = self.get_all_accounts()
        for account in accounts:
            print(f"{account.name} - Balance: {account.balance:.2f} DA")

    def edit_account(self, name, new_name, new_balance) -> None:

        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")

        if new_name:
            account.name = new_name
        if new_balance:
            account.balance = float(new_balance)

        account.save()
        print(f"Account '{name}' edited successfully.")

    def delete_account(self, name) -> None:

        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")

        self.db.execute_query("DELETE FROM accounts WHERE id = ?", (account.id,))
        print(f"Account '{name}' deleted successfully.")

    def transfer_between_accounts(
        self, from_account_name, to_account_name, amount
    ) -> None:
        from_account = self.get_account(from_account_name)
        if not from_account:
            raise ValueError(f"Account '{from_account_name}' not found")
        to_account = self.get_account(to_account_name)
        if not to_account:
            raise ValueError(f"Account '{to_account_name}' not found")
        from_account.transfer(amount, to_account)
        print(
            f"{amount:.2f} DA transferred from '{from_account_name}' to '{to_account_name}'."
        )

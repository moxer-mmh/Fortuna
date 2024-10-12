from typing import List, Optional


class Account:
    def __init__(self, name: str, balance: float = 0):
        self.name: str = name
        self.balance: float = balance

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount

    def transfer(self, amount: float, target: "Account") -> None:
        self.withdraw(amount)
        target.deposit(amount)

    def __repr__(self) -> str:
        return f"Account(name='{self.name}', balance={self.balance:.2f})"

    def __str__(self) -> str:
        return f"{self.name} - {self.balance:.2f}"


class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []

    def get_account(self, name: str) -> Optional[Account]:
        return next((acc for acc in self.accounts if acc.name == name), None)

    def add_account(self, name: str, initial_balance: float = 0) -> None:
        if self.get_account(name):
            raise ValueError(f"Account '{name}' already exists")
        new_account = Account(name, initial_balance)
        self.accounts.append(new_account)

    def display_accounts(self) -> None:
        for account in self.accounts:
            print(f"{account.name} - Balance: {account.balance:.2f} DA")

    def edit_account_name(self, name: str, new_name: str) -> None:
        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")
        account.name = new_name
        print(f"Account '{name}' updated to '{new_name}' successfully.")

    def delete_account(self, name: str) -> None:
        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")
        self.accounts.remove(account)
        print(f"Account '{name}' deleted successfully.")

    def transfer_between_accounts(
        self, from_account_name: str, to_account_name: str, amount: float
    ) -> None:
        from_account = self.get_account(from_account_name)
        to_account = self.get_account(to_account_name)

        if not from_account:
            raise ValueError(f"Account '{from_account_name}' not found")
        if not to_account:
            raise ValueError(f"Account '{to_account_name}' not found")

        from_account.transfer(amount, to_account)
        print(
            f"Transferred {amount:.2f} DA from {from_account_name} to {to_account_name}"
        )

    def input_account(self) -> None:
        name = input("Enter account name: ")
        initial_balance = float(input("Enter initial balance: "))
        self.add_account(name, initial_balance)
        print(f"Account '{name}' added successfully.")

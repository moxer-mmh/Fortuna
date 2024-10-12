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

    def edit_account(self) -> None:
        name = input("Enter account name: ")
        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")
        new_name = input("Enter new account name: ")
        new_balance = input("Enter new balance: ")
        if new_name:
            account.name = new_name
        if new_balance:
            account.balance = float(new_balance)
        print(f"Account '{name}' edited successfully.")

    def delete_account(self) -> None:
        name = input("Enter account name: ")
        account = self.get_account(name)
        if not account:
            raise ValueError(f"Account '{name}' not found")
        self.accounts.remove(account)
        print(f"Account '{name}' deleted successfully.")

    def transfer_between_accounts(self) -> None:
        source_name = input("Enter source account name: ")
        target_name = input("Enter target account name: ")
        amount = float(input("Enter amount to transfer: "))
        source_account = self.get_account(source_name)
        target_account = self.get_account(target_name)
        if not source_account:
            raise ValueError(f"Account '{source_name}' not found")
        if not target_account:
            raise ValueError(f"Account '{target_name}' not found")
        source_account.transfer(amount, target_account)
        print(
            f"{amount:.2f} DA transferred from '{source_name}' to '{target_name}' successfully."
        )

    def input_account(self) -> None:
        name = input("Enter account name: ")
        initial_balance = input("Enter initial balance: ")
        if initial_balance:
            self.add_account(name, float(initial_balance))
        else:
            self.add_account(name, 0)
        print(f"Account '{name}' added successfully.")

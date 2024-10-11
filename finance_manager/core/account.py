from typing import List, Optional

class Account:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def __str__(self):
        return f"{self.name} - {self.balance}"

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount

    def transfer(self, amount, target):
        self.withdraw(amount)
        target.deposit(amount)

    def __repr__(self):
        return f"Account(name='{self.name}', balance={self.balance})"

    def __str__(self):
        return f"{self.name} - {self.balance}"

class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []

    def add_account(self, name: str, initial_balance: float = 0) -> None:
        if self.get_account(name):
            raise ValueError(f"Account '{name}' already exists")
        new_account = Account(name, initial_balance)
        self.accounts.append(new_account)

    def get_account(self, name: str) -> Optional[Account]:
        return next((acc for acc in self.accounts if acc.name == name), None)

    def display_accounts(self) -> None:
        for account in self.accounts:
            print(f"{account.name} - Balance: ${account.balance:.2f}")

    def transfer(self, from_account_name: str, to_account_name: str, amount: float) -> None:
        from_account = self.get_account(from_account_name)
        to_account = self.get_account(to_account_name)

        if not from_account:
            raise ValueError(f"Account '{from_account_name}' not found")
        if not to_account:
            raise ValueError(f"Account '{to_account_name}' not found")

        from_account.withdraw(amount)
        to_account.deposit(amount)
        print(f"Transferred ${amount:.2f} from {from_account_name} to {to_account_name}")

    def input_account(self) -> None:
        name = input("Enter account name: ")
        initial_balance = float(input("Enter initial balance: "))
        self.add_account(name, initial_balance)
        print(f"Account '{name}' added successfully.")
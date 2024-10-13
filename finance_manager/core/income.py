from typing import List, Optional
from datetime import datetime
from .transaction import Transaction
from .category import Category
from .account import Account


class Income:
    def __init__(self, transaction: Transaction, category: Category, account: Account):
        self.transaction = transaction
        self.category = category
        self.account = account

        self.category.add_transaction_to_category(self.transaction)
        self.account.deposit(self.transaction.amount)

    def __str__(self):
        return (
            f"Income: {self.transaction} - Description: {self.transaction.description} "
            f"- Category: {self.category.name} - Account: {self.account.name}"
        )

    @classmethod
    def add_income(
        cls,
        date: datetime,
        amount: float,
        description: str,
        category: Category,
        account: Account,
    ) -> "Income":
        transaction = Transaction(date, amount, description, account)
        return cls(transaction, category, account)

    def edit(
        self,
        new_date: Optional[datetime] = None,
        new_amount: Optional[float] = None,
        new_description: Optional[str] = None,
        new_category: Optional[Category] = None,
    ) -> None:
        if new_date:
            self.transaction.date = new_date
        if new_amount is not None:
            old_amount = self.transaction.amount
            self.transaction.amount = new_amount
            self.account.withdraw(old_amount)
            self.account.deposit(new_amount)
        if new_description:
            self.transaction.description = new_description
        if new_category:
            self.category.delete_transaction_from_category(self.transaction)
            new_category.add_transaction_to_category(self.transaction)
            self.category = new_category

    def delete(self) -> None:
        self.category.delete_transaction_from_category(self.transaction)
        self.account.withdraw(self.transaction.amount)


class IncomeManager:
    def __init__(self):
        self.incomes: List[Income] = []
        self.categories: List[Category] = []

    def add_income(self, income: Income) -> None:
        self.incomes.append(income)

    def add_category(self, name: str, target: float) -> None:
        if self.get_category(name):
            raise ValueError(f"Category '{name}' already exists")
        new_category = Category(name, target)
        self.categories.append(new_category)

    def get_income(self, transaction_id: str) -> Optional[Income]:
        return next(
            (inc for inc in self.incomes if inc.transaction.id == transaction_id), None
        )

    def get_category(self, name: str) -> Optional[Category]:
        return next((cat for cat in self.categories if cat.name == name), None)

    def display_incomes(self, category_name: Optional[str] = None) -> None:
        filtered_incomes = self.incomes
        if category_name:
            filtered_incomes = [
                inc for inc in self.incomes if inc.category.name == category_name
            ]

        for income in filtered_incomes:
            print(income)

    def display_categories(self) -> None:
        for category in self.categories:
            print(f"{category.name} (Target: {category.budget:.2f} DA)")

    def edit_income(self):
        income_id = input("Enter the ID of the income to edit: ")
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d") if new_date_str else None

        new_amount_str = input("Enter new amount or leave blank: ")
        new_amount = float(new_amount_str) if new_amount_str else None

        new_description = input("Enter new description or leave blank: ")

        new_category_name = input("Enter new category name or leave blank: ")
        new_category = (
            self.get_category(new_category_name) if new_category_name else None
        )

        income.edit(new_date, new_amount, new_description, new_category)
        print("Income edited successfully.")

    def edit_category(self):
        category_name = input("Enter the name of the category to edit: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        new_name = input("Enter new name or leave blank: ")
        new_target_str = input("Enter new target or leave blank: ")
        new_target = float(new_target_str) if new_target_str else None

        if new_name:
            category.name = new_name
        if new_target is not None:
            category.budget = new_target

        print("Category edited successfully.")

    def move_transaction(self):
        income_id = input("Enter the ID of the income to move: ")
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        new_category_name = input("Enter the name of the new category: ")
        new_category = self.get_category(new_category_name)
        if not new_category:
            print("Category not found.")
            return

        income.edit(new_category=new_category)
        print(f"Income moved to category '{new_category_name}' successfully.")

    def delete_income(self):
        income_id = input("Enter the ID of the income to delete: ")
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        income.delete()
        self.incomes.remove(income)
        print("Income deleted successfully.")

    def delete_category(self):
        category_name = input("Enter the name of the category to delete: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        for income in self.incomes:
            if income.category == category:
                income.delete()
                self.incomes.remove(income)

        self.categories.remove(category)
        print("Category deleted successfully.")

    def input_income(self, account_manager) -> None:
        date_str = input("Enter income date (YYYY-MM-DD): ")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        amount = float(input("Enter income amount: "))
        description = input("Enter income description: ")
        category_name = input("Enter category name: ")
        account_name = input("Enter account name: ")

        category = self.get_category(category_name)
        if not category:
            raise ValueError(f"Category '{category_name}' not found")

        account = account_manager.get_account(account_name)
        if not account:
            raise ValueError(f"Account '{account_name}' not found")

        income = Income.add_income(date, amount, description, category, account)
        self.add_income(income)
        print("Income added successfully.")

    def input_category(self):
        name = input("Enter category name: ")
        target = input("Enter category target: ")
        if target:
            self.add_category(name, float(target))
        else:
            self.add_category(name, 0)
        print(f"Category '{name}' added successfully.")

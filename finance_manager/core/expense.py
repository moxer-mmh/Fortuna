from typing import List, Optional
from datetime import datetime
from .transaction import Transaction
from .category import Category
from .account import Account

class Expense:
    def __init__(self, transaction: Transaction, category: Category, account: Account):
        self.transaction = transaction
        self.category = category
        self.account = account

        self.category.add_transaction_to_category(self.transaction)
        
        self.account.withdraw(self.transaction.amount)

    def __str__(self):
        return f"Expense: {self.transaction} - Category: {self.category.name} - Account: {self.account.name}"

    @classmethod
    def create_expense(cls, date: datetime, amount: float, description: str, category: Category, account: Account) -> 'Expense':
        transaction = Transaction(date, amount, description)
        return cls(transaction, category, account)

    def edit(self, new_date: Optional[datetime] = None, new_amount: Optional[float] = None, 
             new_description: Optional[str] = None, new_category: Optional[Category] = None) -> None:
        if new_date:
            self.transaction.date = new_date
        if new_amount is not None:
            old_amount = self.transaction.amount
            self.transaction.amount = new_amount
            self.account.deposit(old_amount)
            self.account.withdraw(new_amount)
        if new_description:
            self.transaction.description = new_description
        if new_category:
            self.category.delete_transaction_from_category(self.transaction)
            new_category.add_transaction_to_category(self.transaction)
            self.category = new_category

    def delete(self) -> None:
        self.category.delete_transaction_from_category(self.transaction)
        self.account.deposit(self.transaction.amount)

class ExpenseManager:
    def __init__(self):
        self.expenses: List[Expense] = []
        self.categories: List[Category] = []

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def add_category(self, name: str, budget: float) -> None:
        if self.get_category(name):
            raise ValueError(f"Category '{name}' already exists")
        new_category = Category(name, budget)
        self.categories.append(new_category)

    def get_category(self, name: str) -> Optional[Category]:
        return next((cat for cat in self.categories if cat.name == name), None)

    def display_categories(self) -> None:
        for category in self.categories:
            print(f"{category.name} (Budget: {category.budget:.2f} DA)")

    def display_expenses(self, category_name: Optional[str] = None) -> None:
        filtered_expenses = self.expenses
        if category_name:
            filtered_expenses = [exp for exp in self.expenses if exp.category.name == category_name]
        
        for expense in filtered_expenses:
            print(expense)

    def input_expense(self, account_manager) -> None:
        date_str = input("Enter expense date (YYYY-MM-DD): ")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        amount = float(input("Enter expense amount: "))
        description = input("Enter expense description: ")
        category_name = input("Enter category name: ")
        account_name = input("Enter account name: ")

        category = self.get_category(category_name)
        if not category:
            raise ValueError(f"Category '{category_name}' not found")

        account = account_manager.get_account(account_name)
        if not account:
            raise ValueError(f"Account '{account_name}' not found")

        expense = Expense.create_expense(date, amount, description, category, account)
        self.add_expense(expense)
        print("Expense added successfully.")

    def move_transaction(self):
        expense_id = input("Enter the ID of the expense to move: ")
        expense = next((exp for exp in self.expenses if exp.transaction.id == expense_id), None)
        if not expense:
            print("Expense not found.")
            return

        new_category_name = input("Enter the name of the new category: ")
        new_category = self.get_category(new_category_name)
        if not new_category:
            print("Category not found.")
            return

        expense.edit(new_category=new_category)
        print(f"Expense moved to category '{new_category_name}' successfully.")

    def edit_expense(self):
        expense_id = input("Enter the ID of the expense to edit: ")
        expense = next((exp for exp in self.expenses if exp.transaction.id == expense_id), None)
        if not expense:
            print("Expense not found.")
            return

        new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d") if new_date_str else None

        new_amount_str = input("Enter new amount or leave blank: ")
        new_amount = float(new_amount_str) if new_amount_str else None

        new_description = input("Enter new description or leave blank: ")

        new_category_name = input("Enter new category name or leave blank: ")
        new_category = self.get_category(new_category_name) if new_category_name else None

        expense.edit(new_date, new_amount, new_description, new_category)
        print("Expense edited successfully.")

    def delete_expense(self):
        expense_id = input("Enter the ID of the expense to delete: ")
        expense = next((exp for exp in self.expenses if exp.transaction.id == expense_id), None)
        if not expense:
            print("Expense not found.")
            return

        expense.delete()
        self.expenses.remove(expense)
        print("Expense deleted successfully.")

    def delete_category(self):
        category_name = input("Enter the name of the category to delete: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        for expense in self.expenses:
            if expense.category == category:
                expense.delete()
                self.expenses.remove(expense)

        self.categories.remove(category)
        print("Category deleted successfully.")


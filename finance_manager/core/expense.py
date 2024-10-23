from typing import List, Optional
from datetime import datetime
from .transaction import Transaction
from .category import Category
from .account import Account
from ..database import DatabaseConnection


class Expense:
    def __init__(self, transaction: Transaction, category: Category, account: Account):
        if not transaction:
            raise ValueError("Transaction cannot be None")
        if not category:
            raise ValueError("Category cannot be None")
        if not account:
            raise ValueError("Account cannot be None")

        self.transaction = transaction
        self.category = category
        self.account = account
        self.db = DatabaseConnection()

        self.transaction.type = "expense"
        self.transaction.category_id = category.id

    def save(self):
        if not self.category.can_add_transaction(
            self.transaction.amount, self.transaction.date
        ):
            print(f"Budget limit reached for category: {self.category.name} this month")
            print("Do you want to continue?")
            if input("y/n: ").lower() != "y":
                return 0
            else:
                self.transaction.save()
                self.account.withdraw(self.transaction.amount)
                return 1
        else:
            self.transaction.save()
            self.account.withdraw(self.transaction.amount)
            return 1

    def delete(self) -> None:
        self.account.deposit(self.transaction.amount)
        self.transaction.delete()

    @classmethod
    def add_expense(
        cls,
        date: datetime,
        amount: float,
        description: str,
        category: Category,
        account: Account,
    ) -> "Expense":
        transaction = Transaction(
            date=date,
            amount=amount,
            description=description,
            account_id=account.id,
            category_id=category.id,
            type="expense",
        )
        expense = cls(transaction, category, account)
        state = expense.save()
        if state == 1:
            return expense
        else:
            return None

    def __str__(self):
        return (
            f"Expense: {self.transaction} - Description: {self.transaction.description} "
            f"- Category: {self.category.name} - Account: {self.account.name}"
        )


class ExpenseManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_expense(self, expense: Expense) -> None:
        expense.save()

    def add_category(self, name: str, budget: float) -> None:
        category = Category.get_by_name(name, "expense")
        if category:
            raise ValueError(f"Category '{name}' already exists")

        category = Category(name=name, budget=budget, type="expense")
        category.save()

    def get_expense(self, transaction_id: str) -> Optional[Expense]:
        transaction = Transaction.get_by_id(transaction_id)
        if not transaction or transaction.type != "expense":
            return None

        category = Category.get_by_id(transaction.category_id)
        account = Account.get_by_id(transaction.account_id)

        return Expense(transaction, category, account)

    def get_category(self, name: str) -> Optional[Category]:
        return Category.get_by_name(name, "expense")

    def get_all_categories(self) -> List[Category]:
        results = self.db.fetch_all(
            "SELECT id, name, budget, type FROM categories WHERE type = 'expense'"
        )
        return [
            Category(name=row[1], budget=row[2], type=row[3], id=row[0])
            for row in results
        ]

    def get_all_expenses(self) -> List[Expense]:
        expenses = []
        results = self.db.fetch_all(
            "SELECT id, date, amount, description, account_id, category_id FROM transactions WHERE type = 'expense'"
        )

        for row in results:
            try:
                transaction = Transaction(
                    date=row[1],
                    amount=row[2],
                    description=row[3],
                    account_id=row[4],
                    category_id=row[5],
                    type="expense",
                    id=row[0],
                )

                category = Category.get_by_id(transaction.category_id)
                if not category:
                    print(
                        f"Warning: Category not found for transaction {transaction.id}"
                    )
                    continue

                account = Account.get_by_id(transaction.account_id)
                if not account:
                    print(
                        f"Warning: Account not found for transaction {transaction.id}"
                    )
                    continue

                expense = Expense(transaction, category, account)
                expenses.append(expense)

            except Exception as e:
                print(f"Error processing transaction {row[0]}: {str(e)}")
                continue

        return expenses

    def display_expenses(self) -> None:
        try:
            expenses = self.get_all_expenses()
            if not expenses:
                print("No expenses found.")
                return

            print("\nExpense List:")
            print("-" * 80)
            for expense in expenses:
                try:
                    print(expense)
                except Exception as e:
                    print(f"Error displaying expense: {str(e)}")
            print("-" * 80)

        except Exception as e:
            print(f"Error retrieving expenses: {str(e)}")

    def display_categories(self) -> None:
        categories = self.get_all_categories()
        for category in categories:
            print(f"{category.name} (Budget: {category.budget:.2f} DA)")

    def edit_expense(self):
        expense_id = input("Enter the ID of the expense to edit: ")
        expense = self.get_expense(expense_id)
        if not expense:
            print("Expense not found.")
            return

        new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
        new_amount_str = input("Enter new amount or leave blank: ")
        new_description = input("Enter new description or leave blank: ")
        new_category_name = input("Enter new category name or leave blank: ")

        expense.account.deposit(expense.transaction.amount)

        if new_date_str:
            expense.transaction.date = datetime.strptime(new_date_str, "%Y-%m-%d")
        if new_amount_str:
            expense.transaction.amount = float(new_amount_str)
        if new_description:
            expense.transaction.description = new_description
        if new_category_name:
            new_category = self.get_category(new_category_name)
            if not new_category:
                print("Category not found.")
                return
            expense.category = new_category
            expense.transaction.category_id = new_category.id

        state = expense.save()
        if state == 1:
            print("Expense edited successfully.")
        else:
            print("Failed to edit expense.")

    def edit_category(self):
        category_name = input("Enter the name of the category to edit: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        new_name = input("Enter new category name: ")
        new_budget = input("Enter new budget: ")

        if new_name:
            category.name = new_name
        if new_budget:
            category.budget = float(new_budget)

        category.save()
        print("Category edited successfully.")

    def delete_expense(self):
        expense_id = input("Enter the ID of the expense to delete: ")
        expense = self.get_expense(expense_id)
        if not expense:
            print("Expense not found.")
            return

        expense.delete()
        print("Expense deleted successfully.")

    def delete_category(self):
        category_name = input("Enter the name of the category to delete: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        expenses = [
            exp for exp in self.get_all_expenses() if exp.category.id == category.id
        ]

        for expense in expenses:
            expense.delete()

        self.db.execute_query("DELETE FROM categories WHERE id = ?", (category.id,))
        print("Category deleted successfully.")

    def input_expense(self, account_manager) -> None:
        try:
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

            expense = Expense.add_expense(date, amount, description, category, account)
            if expense is not None:
                print("Expense added successfully.")
                return expense
            else:
                print("Failed to add expense.")
        except ValueError as e:
            print(f"Error: {str(e)}")
            return None

    def input_category(self) -> None:
        name = input("Enter category name: ")
        budget = float(input("Enter category budget: "))
        self.add_category(name, budget)
        print("Category added successfully.")

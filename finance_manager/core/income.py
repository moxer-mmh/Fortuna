from typing import List, Optional
from datetime import datetime
from .transaction import Transaction
from .category import Category
from .account import Account
from ..database import DatabaseConnection


class Income:
    def __init__(self, transaction: Transaction, category: Category, account: Account):
        self.transaction = transaction
        self.category = category
        self.account = account
        self.db = DatabaseConnection()

        self.transaction.type = "income"
        self.transaction.category_id = category.id

    def save(self):
        self.transaction.save()
        self.account.deposit(self.transaction.amount)

    def delete(self) -> None:
        self.account.withdraw(self.transaction.amount)
        self.transaction.delete()

    @classmethod
    def add_income(
        cls,
        date: datetime,
        amount: float,
        description: str,
        category: Category,
        account: Account,
    ) -> "Income":
        transaction = Transaction(
            date=date,
            amount=amount,
            description=description,
            account_id=account.id,
            category_id=category.id,
            type="income",
        )
        income = cls(transaction, category, account)
        income.save()
        return income

    def __str__(self):
        return (
            f"Income: {self.transaction} - Description: {self.transaction.description} "
            f"- Category: {self.category.name} - Account: {self.account.name}"
        )


class IncomeManager:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_income(self, income: Income) -> None:
        income.save()

    def add_category(self, name: str, target: float) -> None:
        category = Category.get_by_name(name, "income")
        if category:
            raise ValueError(f"Category '{name}' already exists")

        category = Category(name=name, budget=target, type="income")
        category.save()

    def get_income(self, transaction_id: str) -> Optional[Income]:
        transaction = Transaction.get_by_id(transaction_id)
        if not transaction or transaction.type != "income":
            return None

        category = Category.get_by_id(transaction.category_id)
        account = Account.get_by_id(transaction.account_id)

        return Income(transaction, category, account)

    def get_category(self, name: str) -> Optional[Category]:
        return Category.get_by_name(name, "income")

    def get_all_categories(self) -> List[Category]:
        results = self.db.fetch_all(
            "SELECT id, name, budget, type FROM categories WHERE type = 'income'"
        )
        return [
            Category(name=row[1], budget=row[2], type=row[3], id=row[0])
            for row in results
        ]

    def get_all_incomes(self) -> List[Income]:
        incomes = []
        results = self.db.fetch_all(
            "SELECT id, date, amount, description, account_id, category_id FROM transactions WHERE type = 'income'"
        )

        for row in results:
            try:
                transaction = Transaction(
                    date=row[1],
                    amount=row[2],
                    description=row[3],
                    account_id=row[4],
                    category_id=row[5],
                    type="income",
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

                income = Income(transaction, category, account)
                incomes.append(income)

            except Exception as e:
                print(f"Error processing transaction {row[0]}: {str(e)}")
                continue

        return incomes

    def display_incomes(self) -> None:
        try:
            incomes = self.get_all_incomes()
            if not incomes:
                print("No incomes found.")
                return

            print("\nIncomes List:")
            print("-" * 80)
            for income in incomes:
                try:
                    print(income)
                except Exception as e:
                    print(f"Error displaying income: {str(e)}")
            print("-" * 80)

        except Exception as e:
            print(f"Error retrieving incomes: {str(e)}")

    def display_categories(self) -> None:
        categories = self.get_all_categories()
        for category in categories:
            print(f"{category.name} (Target: {category.budget:.2f} DA)")

    def edit_income(self):
        income_id = input("Enter the ID of the income to edit: ")
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        new_date_str = input("Enter new date (YYYY-MM-DD) or leave blank: ")
        new_amount_str = input("Enter new amount or leave blank: ")
        new_description = input("Enter new description or leave blank: ")
        new_category_name = input("Enter new category name or leave blank: ")

        income.account.withdraw(income.transaction.amount)

        if new_date_str:
            income.transaction.date = datetime.strptime(new_date_str, "%Y-%m-%d")
        if new_amount_str:
            income.transaction.amount = float(new_amount_str)
        if new_description:
            income.transaction.description = new_description
        if new_category_name:
            new_category = self.get_category(new_category_name)
            if not new_category:
                print("Category not found.")
                return
            income.category = new_category
            income.transaction.category_id = new_category.id

        income.save()
        print("Income edited successfully.")

    def edit_category(self):
        category_name = input("Enter the name of the category to edit: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        new_name = input("Enter new category name: ")
        new_target = input("Enter new target amount: ")

        if new_name:
            category.name = new_name
        if new_target:
            category.budget = float(new_target)

        category.save()
        print("Category edited successfully.")

    def delete_income(self):
        income_id = input("Enter the ID of the income to delete: ")
        income = self.get_income(income_id)
        if not income:
            print("Income not found.")
            return

        income.delete()
        print("Income deleted successfully.")

    def delete_category(self):
        category_name = input("Enter the name of the category to delete: ")
        category = self.get_category(category_name)
        if not category:
            print("Category not found.")
            return

        incomes = [
            inc for inc in self.get_all_incomes() if inc.category.id == category.id
        ]

        for income in incomes:
            income.delete()

        self.db.execute_query("DELETE FROM categories WHERE id = ?", (category.id,))
        print("Category deleted successfully.")

    def input_income(self, account_manager) -> None:
        try:
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
            print("Income added successfully.")
            return income
        except ValueError as e:
            print(f"Error: {str(e)}")
            return None

    def input_category(self) -> None:
        name = input("Enter category name: ")
        target = float(input("Enter target amount: "))
        self.add_category(name, target)
        print("Category added successfully.")

import os
import json
from typing import List, Optional
from datetime import datetime
from .category import Category
from .transaction import Transaction

class BudgetTracker:
    def __init__(self):
        self.categories: List[Category] = []

    def add_category(self, category: Category) -> None:
        if not isinstance(category, Category):
            raise ValueError("Category must be an instance of Category class")
        if self.get_category(category.name):
            raise ValueError(f"Category '{category.name}' already exists")
        self.categories.append(category)

    def get_category(self, name: str) -> Optional[Category]:
        return next((category for category in self.categories if category.name == name), None)

    def add_transaction(self, category_name: str, transaction: Transaction) -> None:
        category = self.get_category(category_name)
        if category:
            category.add_transaction(transaction)
        else:
            raise ValueError(f"Category '{category_name}' not found")

    def get_total_budget(self) -> float:
        return sum(category.budget for category in self.categories)

    def get_total_spent(self) -> float:
        return sum(category.get_total_transactions() for category in self.categories)

    def get_remaining_budget(self) -> float:
        return self.get_total_budget() - self.get_total_spent()

    def input_transaction(self) -> None:
        print("-------------------------------------------------------")
        print("\nEnter expense details:")
        while True:
            try:
                date_str = input("Date (YYYY-MM-DD): ")
                date = datetime.strptime(date_str, "%Y-%m-%d")
                amount = float(input("Amount: "))
                description = input("Description: ")
                category_name = input("Category: ")

                transaction = Transaction(date, amount, description)
                self.add_transaction(category_name, transaction)
                print("Expense added successfully!")
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")

    def display_categories(self) -> None:
        print("-------------------------------------------------------")
        print("\nCategories:")
        for category in self.categories:
            print(f"- {category.name} (Budget: ${category.budget:.2f})")

    def display_transactions(self, category_name: Optional[str] = None) -> None:
        if category_name:
            category = self.get_category(category_name)
            if not category:
                print(f"Category '{category_name}' not found.")
                return
            transactions = category.get_transactions()
            print(f"\nTransactions for {category_name}:")
        else:
            transactions = [t for c in self.categories for t in c.get_transactions()]
            print("\nAll Transactions:")

        for transaction in transactions:
            print(f"- ID: {transaction.id} | {transaction}")

    def generate_report(self) -> None:
        print("-------------------------------------------------------")
        print("\nBudget Report:")
        print(f"Total Budget: ${self.get_total_budget():.2f}")
        print(f"Total Spent: ${self.get_total_spent():.2f}")
        print(f"Remaining Budget: ${self.get_remaining_budget():.2f}")

        print("\nCategory Breakdown:")
        for category in self.categories:
            spent = category.get_total_transactions()
            remaining = category.budget - spent
            print(f"- {category.name}:")
            print(f"  Budget: ${category.budget:.2f}")
            print(f"  Spent: ${spent:.2f}")
            print(f"  Remaining: ${remaining:.2f}")

    def edit_category(self) -> None:
        category_name = input("Enter the name of the category to edit: ")
        category = self.get_category(category_name)
        if category:
            new_name = input(f"Enter new name for '{category_name}' (or press Enter to keep current): ")
            new_budget = input(f"Enter new budget for '{category_name}' (or press Enter to keep current): ")
            if new_name:
                category.name = new_name
            if new_budget:
                category.budget = float(new_budget)
            print("Category updated successfully!")
        else:
            print(f"Category '{category_name}' not found.")

    def delete_category(self) -> None:
        category_name = input("Enter the name of the category to delete: ")
        category = self.get_category(category_name)
        if category:
            self.categories.remove(category)
            print(f"Category '{category_name}' deleted successfully!")
        else:
            print(f"Category '{category_name}' not found.")

    def edit_transaction(self) -> None:
        category_name = input("Enter the category name of the transaction: ")
        category = self.get_category(category_name)
        if category:
            transaction_id = input("Enter the transaction ID: ")
            transaction = next((t for t in category.get_transactions() if t.id == transaction_id), None)
            if transaction:
                new_date = input("Enter new date (YYYY-MM-DD) or press Enter to keep current: ")
                new_amount = input("Enter new amount or press Enter to keep current: ")
                new_description = input("Enter new description or press Enter to keep current: ")

                if new_date:
                    transaction.date = datetime.strptime(new_date, "%Y-%m-%d")
                if new_amount:
                    transaction.amount = float(new_amount)
                if new_description:
                    transaction.description = new_description

                print("Transaction updated successfully!")
            else:
                print(f"Transaction with ID '{transaction_id}' not found in category '{category_name}'.")
        else:
            print(f"Category '{category_name}' not found.")

    def delete_transaction(self) -> None:
        category_name = input("Enter the category name of the transaction: ")
        category = self.get_category(category_name)
        if category:
            transaction_id = input("Enter the transaction ID: ")
            transaction = next((t for t in category.get_transactions() if t.id == transaction_id), None)
            if transaction:
                category.delete_transaction(transaction)
                print("Transaction deleted successfully!")
            else:
                print(f"Transaction with ID '{transaction_id}' not found in category '{category_name}'.")
        else:
            print(f"Category '{category_name}' not found.")

    # def save_data(self, filename: str) -> None:
    #     data = {
    #         "categories": [
    #             {
    #                 "name": category.name,
    #                 "budget": category.budget,
    #                 "transactions": [
    #                     {
    #                         "id": t.id,
    #                         "date": t.date.strftime("%Y-%m-%d"),
    #                         "amount": t.amount,
    #                         "description": t.description
    #                     } for t in category.get_transactions()
    #                 ]
    #             } for category in self.categories
    #         ]
    #     }
    #     try:
    #         # Ensure the directory exists
    #         os.makedirs(os.path.dirname(filename), exist_ok=True)
    #         with open(filename, "w") as file:
    #             json.dump(data, file, indent=2)
    #         print(f"Data saved to {filename}")
    #     except OSError as e:
    #         print(f"Error saving data: {e}")

    # def load_data(self, filename: str) -> None:
    #     try:
    #         with open(filename, "r") as file:
    #             data = json.load(file)
            
    #         self.categories = []
    #         for cat_data in data["categories"]:
    #             category = Category(cat_data["name"], cat_data["budget"])
    #             for trans_data in cat_data["transactions"]:
    #                 transaction = Transaction(
    #                     datetime.strptime(trans_data["date"], "%Y-%m-%d"),
    #                     trans_data["amount"],
    #                     trans_data["description"]
    #                 )
    #                 transaction.id = trans_data["id"]
    #                 category.add_transaction(transaction)
    #             self.add_category(category)
    #         print(f"Data loaded from {filename}")
    #     except FileNotFoundError:
    #         print(f"File not found: {filename}")
    #     except json.JSONDecodeError:
    #         print(f"Error decoding JSON from file: {filename}")
    #     except OSError as e:
    #         print(f"Error loading data: {e}")

    def run_cli(self) -> None:
        while True:
            print("-------------------------------------------------------")
            print("\nBudget Tracker Menu:")
            print("1. Add Expense")
            print("2. View Categories")
            print("3. View Transactions")
            print("4. Generate Report")
            print("5. Edit Category")
            print("6. Delete Category")
            print("7. Edit Transaction")
            print("8. Delete Transaction")
            # print("9. Save Data")
            # print("10. Load Data")
            print("11. Exit")

            choice = input("Enter your choice (1-11): ")

            if choice == '1':
                self.input_transaction()
            elif choice == '2':
                self.display_categories()
            elif choice == '3':
                category = input("Enter category name (or press Enter for all): ")
                self.display_transactions(category if category else None)
            elif choice == '4':
                self.generate_report()
            elif choice == '5':
                self.edit_category()
            elif choice == '6':
                self.delete_category()
            elif choice == '7':
                self.edit_transaction()
            elif choice == '8':
                self.delete_transaction()
            # elif choice == '9':
            #     filename = input("Enter filename to save data: ")
            #     self.save_data(filename)
            # elif choice == '10':
            #     filename = input("Enter filename to load data: ")
            #     self.load_data(filename)
            elif choice == '11':
                print("Thank you for using the Budget Tracker. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
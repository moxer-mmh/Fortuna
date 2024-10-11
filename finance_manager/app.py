from typing import List, Optional
from .core import ExpenseManager, IncomeManager,AccountManager

class FinanceManager:
    def __init__(self):
        self.expense_manager = ExpenseManager()
        self.income_manager = IncomeManager()
        self.account_manager = AccountManager()

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")
            self.process_choice(choice)

    def display_menu(self):
        print("\n===== Finance Manager =====")
        print("1. Display")
        print("2. Add")
        print("3. Edit")
        print("4. Delete")
        print("5. Transfer Between Accounts")
        print("6. Move Transaction")
        print("0. Exit")

    def process_choice(self, choice):
        if choice == "1":
            self.display_submenu()
        elif choice == "2":
            self.add_submenu()
        elif choice == "3":
            self.edit_submenu()
        elif choice == "4":
            self.delete_submenu()
        elif choice == "5":
            self.transfer_between_accounts()
        elif choice == "6":
            self.move_transaction()
        elif choice == "0":
            print("Thank you for using Finance Manager. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please try again.")

    def display_submenu(self):
        print("\n----- Display Menu -----")
        print("1. Display Expenses")
        print("2. Display Incomes")
        print("3. Display Accounts")
        print("4. Display Expense Categories")
        print("5. Display Income Categories")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.display_expenses()
        elif choice == "2":
            self.income_manager.display_incomes()
        elif choice == "3":
            self.account_manager.display_accounts()
        elif choice == "4":
            self.expense_manager.display_categories()
        elif choice == "5":
            self.income_manager.display_categories()
        else:
            print("Invalid choice.")

    def add_submenu(self):
        print("\n----- Add Menu -----")
        print("1. Add Expense")
        print("2. Add Income")
        print("3. Add Account")
        print("4. Add Expense Category")
        print("5. Add Income Category")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.input_expense(self.account_manager)
        elif choice == "2":
            self.income_manager.input_income(self.account_manager)
        elif choice == "3":
            self.account_manager.input_account()
        elif choice == "4":
            self.input_expense_category()
        elif choice == "5":
            self.input_income_category()
        else:
            print("Invalid choice.")

    def edit_submenu(self):
        print("\n----- Edit Menu -----")
        print("1. Edit Expense")
        print("2. Edit Income")
        print("3. Edit Account")
        print("4. Edit Expense Category")
        print("5. Edit Income Category")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.edit_expense()
        elif choice == "2":
            self.income_manager.edit_income()
        elif choice == "3":
            self.account_manager.edit_account()
        elif choice == "4":
            self.expense_manager.edit_category()
        elif choice == "5":
            self.income_manager.edit_category()
        else:
            print("Invalid choice.")

    def delete_submenu(self):
        print("\n----- Delete Menu -----")
        print("1. Delete Expense")
        print("2. Delete Income")
        print("3. Delete Account")
        print("4. Delete Expense Category")
        print("5. Delete Income Category")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.delete_expense()
        elif choice == "2":
            self.income_manager.delete_income()
        elif choice == "3":
            self.account_manager.delete_account()
        elif choice == "4":
            self.expense_manager.delete_category()
        elif choice == "5":
            self.income_manager.delete_category()
        else:
            print("Invalid choice.")

    def input_expense_category(self):
        name = input("Enter expense category name: ")
        budget = float(input("Enter category budget: "))
        try:
            self.expense_manager.add_category(name, budget)
            print(f"Expense category '{name}' added successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    def input_income_category(self):
        name = input("Enter income category name: ")
        budget = float(input("Enter category budget: "))
        try:
            self.income_manager.add_category(name, budget)
            print(f"Income category '{name}' added successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    def transfer_between_accounts(self):
        from_account = input("Enter the name of the account to transfer from: ")
        to_account = input("Enter the name of the account to transfer to: ")
        amount = float(input("Enter the amount to transfer: "))
        try:
            self.account_manager.transfer(from_account, to_account, amount)
        except ValueError as e:
            print(f"Error: {e}")

    def move_transaction(self):
        print("\n----- Move Transaction -----")
        print("1. Move Expense")
        print("2. Move Income")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.expense_manager.move_transaction()
        elif choice == "2":
            self.income_manager.move_transaction()
        else:
            print("Invalid choice.")